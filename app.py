from __future__ import unicode_literals

import datetime
import errno

import os
import re

from watson_developer_cloud import NaturalLanguageUnderstandingV1, WatsonException
import watson_developer_cloud.natural_language_understanding.features.v1 as Features

import tempfile
from random import randint
from urllib.error import HTTPError

from urllib.request import urlopen, Request

import requests
from flask import Flask, request, abort, json


from linebot import (

    LineBotApi, WebhookHandler

)

from linebot.exceptions import (

    InvalidSignatureError

)

from linebot.models import (

    MessageEvent, TextMessage, TextSendMessage,

    SourceUser, SourceGroup, SourceRoom,

    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,

    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,

    CarouselTemplate, CarouselColumn, PostbackEvent,

    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,

    ImageMessage, VideoMessage, AudioMessage,

    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,

    ImageSendMessage, VideoSendMessage)

app = Flask(__name__)

line_bot_api = LineBotApi('O3tevompb2TBI20Oeodk53nif/edA8yIQfrtbDnae6CkfSpGjxmgInzF/WmThvWlmve+7VRgBF28+smp3IHLjiwx5WCqiT315U8n5M1vLYgXLg8YBvlNqlSxfJjlWPjk0DMzojD3TKCVD18bdXzbowdB04t89/1O/w1cDnyilFU=')

handler = WebhookHandler('2cd36ded8c1df15419670d69f6d02b31')



static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')





# function for create tmp dir for download content

def make_static_tmp_dir():

    try:

        os.makedirs(static_tmp_path)

    except OSError as exc:

        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):

            pass

        else:

            raise





@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
def getJsonForCountry(country):
    jsonurl = urlopen('https://restcountries.eu/rest/v2/alpha/'+country)
    jsonpart = json.loads(jsonurl.read())
    return jsonpart['name']
def getJson(nickname, mode, token):

    jsonurl = urlopen(
        'https://osu.ppy.sh/api/get_user?k=37967304c711a663eb326dcf8b41e1a5987e2b7f&u=' + nickname.lower() + '&m=' + mode)
    jsonpart = json.loads(jsonurl.read())

    if len(jsonpart) == 0:
        line_bot_api.reply_message(token,TextSendMessage(text='dont know'))
    else:
        if jsonpart[0]['pp_rank']==None:
            line_bot_api.reply_message(token,TextSendMessage(text='the user has not played recently'))
        else:
            username = jsonpart[0]['username']
            pp_rank = jsonpart[0]['pp_rank']
            userid = jsonpart[0]['user_id']
            imageurl = 'https://a.ppy.sh/' + userid
            country_rank = jsonpart[0]['pp_country_rank']
            country = getJsonForCountry(jsonpart[0]['country'])
            carousel_template = CarouselTemplate(columns=[
                CarouselColumn(
                    text='global rank: ' + pp_rank + ' (#' + country_rank + ' ' + country + ')',
                    thumbnail_image_url=imageurl, title=username, actions=[
                        URITemplateAction(
                            label='go to user', uri=goo_shorten_url('https://osu.ppy.sh/u/' + username))
                    ])
            ])
            template_message = TemplateSendMessage(
                alt_text='meguri sent a photo.', template=carousel_template)
            line_bot_api.reply_message(token, template_message)


def regexMethodForHour(text):
    searchObj = re.search(r' (.*?);', text + ';', re.M | re.I)
    number = searchObj.group(1)
    #number+=24
    return number
def methodForNow():
    time = int(datetime.datetime.now().hour+7)

    return int(time)


def getJsonForWeather(city,token):
    try:
        jsonurl = urlopen(
            'http://api.openweathermap.org/data/2.5/forecast?q=' + city + '&appid=fe18035f6b83c8b163d1a7a8ef934a75')
        jsonpart = json.loads(jsonurl.read())
        countryId = getJsonForCountry(jsonpart['city']['country'])
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(
                text=regexMethodForHour(jsonpart['list'][3]['dt_txt']) + ' it is gonna be ' +jsonpart['list'][3]['weather'][0]['main'],
                thumbnail_image_url='https://openweathermap.org/img/w/' + jsonpart['list'][3]['weather'][0][
                    'icon'] + '.png',
                title=jsonpart['city']['name'] + ', ' + countryId, actions=[
                    URITemplateAction(
                        label='open in browser', uri='https://openweathermap.org/')
                ]),
            CarouselColumn(
                text=regexMethodForHour(jsonpart['list'][4]['dt_txt']) + ' it is gonna be ' +
                     jsonpart['list'][4]['weather'][0]['main'],
                thumbnail_image_url='https://openweathermap.org/img/w/' + jsonpart['list'][4]['weather'][0][
                    'icon'] + '.png',
                title=jsonpart['city']['name'] + ', ' + countryId, actions=[
                    URITemplateAction(
                        label='open in browser', uri='https://openweathermap.org/')
                ]),
            CarouselColumn(
                text=regexMethodForHour(jsonpart['list'][5]['dt_txt']) + ' it is gonna be ' +
                     jsonpart['list'][5]['weather'][0]['main'],
                thumbnail_image_url='https://openweathermap.org/img/w/' + jsonpart['list'][5]['weather'][0][
                    'icon'] + '.png',
                title=jsonpart['city']['name'] + ', ' + countryId, actions=[
                    URITemplateAction(
                        label='open in browser', uri='https://openweathermap.org/')
                ])
        ])
        template_message = TemplateSendMessage(
            alt_text='meguri sent a photo.', template=carousel_template)
        line_bot_api.reply_message(token, template_message)

    except HTTPError as err:
        if err.code == 404:
            line_bot_api.reply_message(token,TextSendMessage(text='city not found'))
def videoMessage(token,text):

    try:
        jsonurl = urlopen('https://ytdl-a.herokuapp.com/api/info?url='+text)
        jsonpart = json.loads(jsonurl.read())
        content = jsonpart['info']['url']
        thumbnail = jsonpart['info']['thumbnail']
        video_message = VideoSendMessage(
            original_content_url=content,
            preview_image_url=thumbnail
        )
        line_bot_api.reply_message(token, video_message)
    except HTTPError as err:
        if err.code == 500:
           line_bot_api.reply_message(token,TextSendMessage(text='video not supported'))

def videoMessageForSearchAPI(token,text):
    try:
        jsonurl = urlopen('https://ytdl-a.herokuapp.com/api/info?url='+text)
        jsonpart = json.loads(jsonurl.read())
        content = jsonpart['info']['url']
        thumbnail = jsonpart['info']['thumbnail']
        video_message = VideoSendMessage(
            original_content_url=content,
            preview_image_url=thumbnail
        )
        return line_bot_api.reply_message(token, video_message)
    except IndexError:
        line_bot_api.reply_message(token,TextSendMessage(text='not found'))


def goo_shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyBDB-GF8QsWHoy7_Kc-wiTHRnrAeiJs8A8'
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    jsonpart = r.json()
    return jsonpart['id']
def azureImage(text):
    req = Request('https://api.cognitive.microsoft.com/bing/v5.0/images/search?q=' + text)
    req.add_header('Ocp-Apim-Subscription-Key', 'f17c155ad77b4ae9926829e0d9c44cb9')
    resp = urlopen(req)
    content = json.loads(resp.read())
    return content


def imageSearch(token,text):
    try:
        content = azureImage(text)
        textEncode = text.replace('+', ' ')
        if len(content['value']) < 5:
            randomNumber = randint(0, len(content['value']) - 1)
            carousel_template = CarouselTemplate(columns=[
                CarouselColumn(
                    text=textEncode,
                    thumbnail_image_url=content['value'][randomNumber]['thumbnailUrl'], actions=[
                        URITemplateAction(
                            label='open in browser', uri=goo_shorten_url(content['value'][randomNumber]['contentUrl']))
                    ])
            ])
            template_message = TemplateSendMessage(
                alt_text='meguri sent a photo.', template=carousel_template)
            line_bot_api.reply_message(token, template_message)
        else:
            carousel_template = CarouselTemplate(columns=[
                CarouselColumn(
                    text=textEncode,
                    thumbnail_image_url=content['value'][0]['thumbnailUrl'], actions=[
                        URITemplateAction(
                            label='open in browser', uri=goo_shorten_url(content['value'][0]['contentUrl']))
                    ]),
                CarouselColumn(
                    text=textEncode,
                    thumbnail_image_url=content['value'][1]['thumbnailUrl'], actions=[
                        URITemplateAction(
                            label='open in browser', uri=goo_shorten_url(content['value'][1]['contentUrl']))
                    ]),
                CarouselColumn(
                    text=textEncode,
                    thumbnail_image_url=content['value'][2]['thumbnailUrl'], actions=[
                        URITemplateAction(
                            label='open in browser', uri=goo_shorten_url(content['value'][2]['contentUrl']))
                    ]),
                CarouselColumn(
                    text=textEncode,
                    thumbnail_image_url=content['value'][3]['thumbnailUrl'], actions=[
                        URITemplateAction(
                            label='open in browser', uri=goo_shorten_url(content['value'][3]['contentUrl']))
                    ]),
                CarouselColumn(
                    text=textEncode,
                    thumbnail_image_url=content['value'][4]['thumbnailUrl'], actions=[
                        URITemplateAction(
                            label='open in browser', uri=goo_shorten_url(content['value'][4]['contentUrl']))
                    ])

            ])
            template_message = TemplateSendMessage(
                alt_text='meguri sent a photo.', template=carousel_template)
            line_bot_api.reply_message(token, template_message)
    except HTTPError:
        line_bot_api.reply_message(token,TextSendMessage(text='not found'))


def stalkInstagram(token,text):
    try:
        jsonurl = urlopen('https://www.instagram.com/'+text+'/?__a=1')
        jsonpart = json.loads(jsonurl.read())
        if jsonpart['user']['is_private'] == True:
            line_bot_api.reply_message(token,TextSendMessage(text='user is private'))
        else:
            if len(jsonpart['user']['media']['nodes'])<12:
                carousel_template = CarouselTemplate(columns=[
                    CarouselColumn(
                        text=text,
                        thumbnail_image_url=jsonpart['user']['media']['nodes'][randint(0,len(jsonpart['user']['media']['nodes']))]['thumbnail_src'], actions=[
                            URITemplateAction(
                                label='download',
                                uri=jsonpart['user']['media']['nodes'][randint(0,len(jsonpart['user']['media']['nodes']))]['thumbnail_src']
                            )
                        ])
                ])
                template_message = TemplateSendMessage(
                    alt_text='meguri sent a photo.', template=carousel_template)
                line_bot_api.reply_message(token, template_message)

            else:
                result = []
                used = []
                for x in range(0, 11):
                    add = int(randint(0, 11))
                    while (add in used):
                        add = int(randint(0, 11))
                    used.append(add)
                    result.append(add)

                carousel_template = CarouselTemplate(columns=[
                    CarouselColumn(
                        text=text,
                        thumbnail_image_url=jsonpart['user']['media']['nodes'][result[0]]['thumbnail_src'], actions=[
                            URITemplateAction(
                                label='download',
                                uri=jsonpart['user']['media']['nodes'][result[0]]['thumbnail_src']
                            )
                        ]),
                    CarouselColumn(
                        text=text,
                        thumbnail_image_url=jsonpart['user']['media']['nodes'][result[1]]['thumbnail_src'], actions=[
                            URITemplateAction(
                                label='download',
                                uri=jsonpart['user']['media']['nodes'][result[1]]['thumbnail_src']
                            )
                        ]),
                    CarouselColumn(
                        text=text,
                        thumbnail_image_url=jsonpart['user']['media']['nodes'][result[2]]['thumbnail_src'], actions=[
                            URITemplateAction(
                                label='download',
                                uri=jsonpart['user']['media']['nodes'][result[2]]['thumbnail_src']
                            )
                        ]),
                    CarouselColumn(
                        text=text,
                        thumbnail_image_url=jsonpart['user']['media']['nodes'][result[3]]['thumbnail_src'], actions=[
                            URITemplateAction(
                                label='download',
                                uri=jsonpart['user']['media']['nodes'][result[3]]['thumbnail_src']
                            )
                        ]),
                    CarouselColumn(
                        text=text,
                        thumbnail_image_url=jsonpart['user']['media']['nodes'][result[4]]['thumbnail_src'], actions=[
                            URITemplateAction(
                                label='download',
                                uri=jsonpart['user']['media']['nodes'][result[4]]['thumbnail_src']
                            )
                        ])
                ])
                template_message = TemplateSendMessage(
                    alt_text='meguri sent a photo.', template=carousel_template)
                line_bot_api.reply_message(token, template_message)
    except HTTPError as err:
        if err.code == 400:
            line_bot_api.reply_message(token,TextSendMessage(text='user not found'))
def methodForHelp(token):
        line_bot_api.reply_message(token,TextSendMessage(text='/text /stalk /video /image /bukalapak /weather /osu /about\n\nfor more information type /help <command name>\nex:/help osu'))
def methodForHelpVideo(token):
        line_bot_api.reply_message(token,TextSendMessage(text='share or search youtube video and break the limit you can share video more than 5 minutes\n\nexample 1:\n/video https://www.youtube.com/watch?v=Vsc8uGxTlFQ\n\nexample 2:/video hatsune miku\n\nnow support to share video from twitch and vimeo\nex:https://www.twitch.tv/videos/156691454'))
def methodForHelpBukalapak(token):
    line_bot_api.reply_message(token, TextSendMessage(
        text='search a product in one of biggest e-commerce in southeast asia BUKALAPAK\nexample:\n/bukalapak <productname>\n(/bukalapak zenfone 3)'))
def methodForHelpOsu(token):
        line_bot_api.reply_message(token,TextSendMessage(text='command for osu player /std /ctb /taiko /mania\nex:/ctb deceitful'))
def methodForHelpAbout(token):
    line_bot_api.reply_message(token, TextSendMessage(
        text='under development for personal amusement by :\ntitus efferian (line id: adhistitus) and\nkato@linuxsec.org'))
def methodForHelpImage(token):
    line_bot_api.reply_message(token, TextSendMessage(
        text='search any image in the internet powered by Bing Microsoft Azure\nexample: /image <search>\n(/image hatsune miku)'))
def methodForHelpWeather(token):
    line_bot_api.reply_message(token, TextSendMessage(text='weather forecast\n\nex:/weather jakarta'))
def methodForHelpText(token):
    line_bot_api.reply_message(token,TextSendMessage(text='Natural Language Processing algorithm\n\nexample:\n/text i really love you'))
def methodForHelpStalk(token):
        line_bot_api.reply_message(token,TextSendMessage(text='stalk your instagram friends\n/stalk <username>\nex:/stakl yingtze'))
def priceCurrency(text):
    return (str('Rp {:0,.0f}'.format(text)).replace(',','.'))
def bukalapak(token,text):
    try:
        jsonurl = urlopen('https://api.bukalapak.com/v2/products.json?keywords='+text+'&page=1&top_seller=1&per_page=5')
        jsonpart = json.loads(jsonurl.read())
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(

                text=str(priceCurrency(jsonpart['products'][0]['price'])),
                thumbnail_image_url=
                jsonpart['products'][0]['images'][0], actions=[
                    URITemplateAction(
                        label='open in browser',
                        uri=str(jsonpart['products'][0]['url'])
                    )
                ]),
            CarouselColumn(
                text=str(priceCurrency(jsonpart['products'][1]['price'])),
                thumbnail_image_url=
                jsonpart['products'][1]['images'][0], actions=[
                    URITemplateAction(
                        label='open in browser',
                        uri=str(jsonpart['products'][1]['url'])
                    )
                ]),
            CarouselColumn(
                text=str(priceCurrency(jsonpart['products'][2]['price'])),
                thumbnail_image_url=
                jsonpart['products'][2]['images'][0], actions=[
                    URITemplateAction(
                        label='open in browser',
                        uri=str(jsonpart['products'][2]['url'])
                    )
                ]),
            CarouselColumn(
                text=str(priceCurrency(jsonpart['products'][3]['price'])),
                thumbnail_image_url=
                jsonpart['products'][3]['images'][0], actions=[
                    URITemplateAction(
                        label='open in browser',
                        uri=str(jsonpart['products'][3]['url'])
                    )
                ]),
            CarouselColumn(
                text=str(priceCurrency(jsonpart['products'][4]['price'])),
                thumbnail_image_url=
                jsonpart['products'][4]['images'][0], actions=[
                    URITemplateAction(
                        label='open in browser',
                        uri=str(jsonpart['products'][4]['url'])
                    )
                ])
        ])
        template_message = TemplateSendMessage(
            alt_text='meguri sent a photo.', template=carousel_template)
        line_bot_api.reply_message(token, template_message)

    except IndexError:
        line_bot_api.reply_message(token,TextSendMessage(text='not found'))

def textanalytics(token,text):
    try:
        natural_language_understanding = NaturalLanguageUnderstandingV1(
            username="9d600703-7095-4ada-b888-e3a8289bf74e",
            password="HzbSjQzEReja",
            version="2017-02-27")

        response = natural_language_understanding.analyze(
            text=text,
            features=[
                Features.Emotion()
            ]
        )
        jsonpart = json.loads(json.dumps(response, indent=2))
        sadness = jsonpart['emotion']['document']['emotion']['sadness']
        joy = jsonpart['emotion']['document']['emotion']['joy']
        fear = jsonpart['emotion']['document']['emotion']['fear']
        disgust = jsonpart['emotion']['document']['emotion']['disgust']
        anger = jsonpart['emotion']['document']['emotion']['anger']
        sadnessText = 'sadness = ' + str(round(sadness * 100)) + '%'
        joyText = 'joy = ' + str(round(joy * 100)) + '%'
        fearText = 'fear = ' + str(round(fear * 100)) + '%'
        disgustText = 'disgust = ' + str(round(disgust * 100)) + '%'
        angerText = 'anger = ' + str(round(anger * 100)) + '%'
        line_bot_api.reply_message(token,TextSendMessage(text=text+'\n\n'+sadnessText+'\n'+joyText+'\n'+fearText+'\n'+disgustText+'\n'+angerText))


    except WatsonException as err:
        if '400' in str(err):
            line_bot_api.reply_message(token,TextSendMessage(text='unsupported text language'))
        elif '422' in str(err):
            line_bot_api.reply_message(token,TextSendMessage(text='not enough text for language processing'))
        else:
            line_bot_api.reply_message(token,TextSendMessage(text='dont know'))


def alkitab(kitab,pasal,ayat,token):
    import urllib.request

    opener = urllib.request.FancyURLopener({})
    url = 'http://alkitab.me/'+kitab+'/'+pasal+'/'+ayat
    f = opener.open(url)
    content = f.read().decode("utf-8")

    searchObj = re.search(r'<a class="nomor-ayat" href="'+url+'">\r\n\t\t\t'+ayat+'.\r\n\t\t\t</a>\r\n\t\t\t(.*?)</p>', content, re.M | re.I)
    confirm_template = ConfirmTemplate(text=' ', actions=[
        MessageTemplateAction(label='Next', text='alkitabNext'),
        MessageTemplateAction(label='Prev', text='alkitabPrev'),

    ])
    line_bot_api.reply_message(token,[TextSendMessage(text=kitab+' '+pasal+':'+ayat+'\n\n'+searchObj.group(1)),TemplateSendMessage(
        alt_text='Confirm alt text', template=confirm_template)])

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    token = event.reply_token
    ayat = 1
    pasalNext = 'null'
    kitabNext = 'null'


    if 'bot leave' not in event.message.text.lower():

        if text.startswith('/ctb'):
            searchObjForCommand = re.search(r'/(.*?) ', text, re.M | re.I)
            searchObj = re.search(r'/' + searchObjForCommand.group(1) + ' (.*?);', text + ';', re.M | re.I)
            getJson(searchObj.group(1), '2', token)
        if text.startswith('/mania'):
            searchObjForCommand = re.search(r'/(.*?) ', text, re.M | re.I)
            searchObj = re.search(r'/' + searchObjForCommand.group(1) + ' (.*?);', text + ';', re.M | re.I)
            getJson(searchObj.group(1), '3', token)
        if text.startswith('/taiko'):
            searchObjForCommand = re.search(r'/(.*?) ', text, re.M | re.I)
            searchObj = re.search(r'/' + searchObjForCommand.group(1) + ' (.*?);', text + ';', re.M | re.I)
            getJson(searchObj.group(1), '1', token)
        if text.startswith('/std'):
            searchObjForCommand = re.search(r'/(.*?) ', text, re.M | re.I)
            searchObj = re.search(r'/' + searchObjForCommand.group(1) + ' (.*?);', text + ';', re.M | re.I)
            getJson(searchObj.group(1), '0', token)
        if text.startswith('/weather'):
            searchObj = re.search(r'/weather (.*?);', text + ';', re.M | re.I)
            getJsonForWeather(searchObj.group(1),token)
        if text.startswith('/video https://'):
            searchObj = re.search(r'/video https://(.*?);', text + ';', re.M | re.I)
            videoMessage(token,'https://'+searchObj.group(1))
        if text.startswith('/image'):
            searchObj = re.search(r'/image (.*?);', text + ';', re.M | re.I)
            replaceText = searchObj.group(1).replace(' ','+')
            imageSearch(token,replaceText)

        if text.startswith('/stalk'):
            searchObj = re.search(r'/stalk (.*?);', text + ';', re.M | re.I)
            stalkInstagram(token,searchObj.group(1))
        if text=='/help':
            methodForHelp(token)
        if text.startswith('/help stalk'):
            methodForHelpStalk(token)
        if text.startswith('/help video'):
            methodForHelpVideo(token)
        if text.startswith('/help bukalapak'):
            methodForHelpBukalapak(token)
        if text.startswith('/help image'):
            methodForHelpImage(token)
        if text.startswith('/help text'):
            methodForHelpText(token)
        if text.startswith('/help osu'):
            methodForHelpOsu(token)
        if text.startswith('/help weather'):
            methodForHelpWeather(token)
        if text.startswith('/about'):
            methodForHelpAbout(token)
        if text.startswith('/video'):
            searchObj = re.search(r'/video (.*?);', text + ';', re.M | re.I)
            replaceText = searchObj.group(1).replace(' ', '+')
            jsonurl = urlopen(
                'https://www.googleapis.com/youtube/v3/search?part=snippet&q='+replaceText+'&type=video&key=AIzaSyDbfeClXLMorneLuPnEILavUgZkiB-3SrM&maxResults=25')
            jsonpart = json.loads(jsonurl.read())
            used = []
            random = randint(0,24)
            link = 'https://www.youtube.com/watch?v='+str(jsonpart['items'][random]['id']['videoId'])
            videoMessageForSearchAPI(token,link)
        if text.startswith('/bukalapak'):
            searchObj = re.search(r'/bukalapak (.*?);', text + ';', re.M | re.I)
            replaceText = searchObj.group(1).replace(' ', '+')
            bukalapak(token,replaceText)
        if text.startswith('/text'):
            searchObj = re.search(r'/text (.*?);', text + ';', re.M | re.I)
            textanalytics(token,searchObj.group(1))
        if text.startswith('/alkitab'):
            kitab = re.search(r'/alkitab (.*?) ', text + ';', re.M | re.I)
            pasal = re.search(r'/alkitab ' + kitab.group(1) + ' (.*?):(.*)', text, re.M | re.I)
            #line_bot_api.reply_message(token,TextSendMessage(text=kitab.group(1)+' '+pasal.group(1)+':'+pasal.group(2)))
            ayat = int(pasal.group(2))
            pasalNext = str(pasal.group(1))
            kitabNext = str(kitab.group(1))
            alkitab(kitab.group(1).title(),pasal.group(1),pasal.group(2),token)
        if 'alkitabNext' in text:
            line_bot_api.reply_message(token,TextSendMessage(text=pasalNext))











    else:
        if isinstance(event.source, SourceGroup):
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.leave_room(event.source.room_id)






def faceapi(token,url):
    line_bot_api.reply_message(token,TextSendMessage(text=url))

# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)
    url = request.host_url + os.path.join('static', 'tmp', dist_name)
    faceapi(event.reply_token,url)


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'developer':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='under development for personal amusement by :\ntitus efferian (line id: adhistitus) and\nkato@linuxsec.org'))
    if event.postback.data == 'instagram':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='stalk your instagram friends\n/stalk <username>\nexample: /stalk yingtze'))
    if event.postback.data == 'osu':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='this command for osu player: /std /taiko /ctb /mania\nexample: /ctb deceitful'))
    if event.postback.data == 'bukalapak':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='search a product in one of biggest e-commerce in southeast asia BUKALAPAK\nexample:\n/bukalapak <productname>\n(/bukalapak zenfone 3)'))
    if event.postback.data == 'youtube':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='share or search youtube video and break the limit you can share video more than 5 minutes\n\nexample 1:\n/video https://www.youtube.com/watch?v=Vsc8uGxTlFQ\n\nexample 2:/video hatsune miku'))
    if event.postback.data == 'image':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='search any image in the internet powered by Bing Microsoft Azure\nexample: /image <search>\n(/image hatsune miku)'))
    if event.postback.data == 'weather':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='weather forecast\n\nex:/weather jakarta'))
@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(
                event.beacon.hwid, event.beacon.dm)))



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    #make_static_tmp_dir()
    app.run(host='0.0.0.0', port=port)


#google-APi : AIzaSyACppscHMJnI6GvWDJToAtS9vAUbGVcDr8
#azure api : db017bc371a34c488702df1801fc8f11
#google api :AIzaSyBDB-GF8QsWHoy7_Kc-wiTHRnrAeiJs8A8
#cloudinary.com : JsOgvhHvZyGIuPwv6jTPvoz2UYc