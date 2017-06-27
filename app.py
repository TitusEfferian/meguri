from __future__ import unicode_literals

import datetime
import errno

import os
import re



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

line_bot_api = LineBotApi('IFLYBHwHTM6qnQwm0y25h+eYD82RvTYs6tIvkejI89SSgXWkpzh+PB8pW07LyWuLjRQmYRKqm2OWcccY85GqjEzTqopCSFsIn7ghD1ICfLdGi7xR9fQg2LJXSyZdq0oabKJhXNnrbYRgJZHsTk9DkgdB04t89/1O/w1cDnyilFU=')

handler = WebhookHandler('86e0e5b2dbade0ffb1babdfb52be6ee6')



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
        'https://osu.ppy.sh/api/get_user?k=37967304c711a663eb326dcf8b41e1a5987e2b7f&u=' + nickname + '&m=' + mode)
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
                            label='go to user', uri='https://osu.ppy.sh/u/' + username)
                    ])
            ])
            template_message = TemplateSendMessage(
                alt_text='meguri sent a photo.', template=carousel_template)
            line_bot_api.reply_message(token, template_message)


def regexMethodForHour(text):
    searchObj = re.search(r' (.*?):', text + ';', re.M | re.I)
    number = int(searchObj.group(1))
    number+=24

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
                text=str(int(regexMethodForHour(
                    jsonpart['list'][3]['dt_txt']) - methodForNow())) + ' hours from now, it is gonna be ' +
                     jsonpart['list'][3]['weather'][0]['main'],
                thumbnail_image_url='https://openweathermap.org/img/w/' + jsonpart['list'][3]['weather'][0][
                    'icon'] + '.png',
                title=jsonpart['city']['name'] + ', ' + countryId, actions=[
                    URITemplateAction(
                        label='open in browser', uri='https://openweathermap.org/')
                ]),
            CarouselColumn(
                text=str(int(regexMethodForHour(
                    jsonpart['list'][4]['dt_txt']) - methodForNow())) + ' hours from now, it is gonna be ' +
                     jsonpart['list'][4]['weather'][0]['main'],
                thumbnail_image_url='https://openweathermap.org/img/w/' + jsonpart['list'][4]['weather'][0][
                    'icon'] + '.png',
                title=jsonpart['city']['name'] + ', ' + countryId, actions=[
                    URITemplateAction(
                        label='open in browser', uri='https://openweathermap.org/')
                ]),
            CarouselColumn(
                text=str(int(regexMethodForHour(
                    jsonpart['list'][5]['dt_txt']) - methodForNow())) + ' hours from now, it is gonna be ' +
                     jsonpart['list'][5]['weather'][0]['main'],
                thumbnail_image_url='https://openweathermap.org/img/w/' + jsonpart['list'][5]['weather'][0][
                    'icon'] + '.png',
                title=jsonpart['city']['name'] + ', ' + countryId, actions=[
                    URITemplateAction(
                        label='open in browser', uri='https://openweathermap.org/')
                ]),
            CarouselColumn(
                text=str(int(regexMethodForHour(
                    jsonpart['list'][6]['dt_txt']) - methodForNow())) + ' hours from now, it is gonna be ' +
                     jsonpart['list'][6]['weather'][0]['main'],
                thumbnail_image_url='https://openweathermap.org/img/w/' + jsonpart['list'][6]['weather'][0][
                    'icon'] + '.png',
                title=jsonpart['city']['name'] + ', ' + countryId, actions=[
                    URITemplateAction(
                        label='open in browser', uri='https://openweathermap.org/')
                ]),
            CarouselColumn(
                text=str(int(regexMethodForHour(
                    jsonpart['list'][7]['dt_txt']) - methodForNow())) + ' hours from now, it is gonna be ' +
                     jsonpart['list'][7]['weather'][0]['main'],
                thumbnail_image_url='https://openweathermap.org/img/w/' + jsonpart['list'][7]['weather'][0][
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
        jsonurl = urlopen('http://megumin-yt.herokuapp.com/api/info?url='+text)
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
        jsonurl = urlopen('http://megumin-yt.herokuapp.com/api/info?url=' + text)
        jsonpart = json.loads(jsonurl.read())
        content = jsonpart['info']['url']
        thumbnail = jsonpart['info']['thumbnail']
        video_message = VideoSendMessage(
            original_content_url=content,
            preview_image_url=thumbnail
        )
        return line_bot_api.reply_message(token, video_message)
    except HTTPError as err:
        if err.code == 500:
            return '0'


def goo_shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyBDB-GF8QsWHoy7_Kc-wiTHRnrAeiJs8A8'
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    jsonpart = r.json()
    return jsonpart['id']
def azureImage(text):
    req = Request('https://api.cognitive.microsoft.com/bing/v5.0/images/search?q=' + text)
    req.add_header('Ocp-Apim-Subscription-Key', 'db017bc371a34c488702df1801fc8f11')
    resp = urlopen(req)
    content = json.loads(resp.read())
    return content


def imageSearch(token,text):
    try:
        content = azureImage(text)
        textEncode = text.replace('+',' ')
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(
                text=textEncode,
                thumbnail_image_url=content['value'][0]['thumbnailUrl'], actions=[
                    PostbackTemplateAction(
                        label='download',
                        data=text+':'+'0'
                    )
                ]),
            CarouselColumn(
                text=textEncode,
                thumbnail_image_url=content['value'][1]['thumbnailUrl'], actions=[
                    PostbackTemplateAction(
                        label='download',
                        data=text + ':' + '1'
                    )
                ]),
            CarouselColumn(
                text=textEncode,
                thumbnail_image_url=content['value'][2]['thumbnailUrl'], actions=[
                    PostbackTemplateAction(
                        label='download',
                        data=text + ':' + '2'
                    )
                ]),
            CarouselColumn(
                text=textEncode,
                thumbnail_image_url=content['value'][3]['thumbnailUrl'], actions=[
                    PostbackTemplateAction(
                        label='download',
                        data=text + ':' + '3'
                    )
                ]),
            CarouselColumn(
                text=textEncode,
                thumbnail_image_url=content['value'][4]['thumbnailUrl'], actions=[
                    PostbackTemplateAction(
                        label='download',
                        data=text + ':' + '4'
                    )
                ])

        ])
        template_message = TemplateSendMessage(
            alt_text='meguri sent a photo.', template=carousel_template)
        line_bot_api.reply_message(token, template_message)
    except HTTPError as err:
        if err.code:
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
                for x in range(0, 12):
                    add = int(randint(0, 12))
                    while (add in used):
                        add = int(randint(0, 12))
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
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(
            text=' ', actions=[
                PostbackTemplateAction(
                    label='instagram',
                    data='instagram'
                ),
                PostbackTemplateAction(
                    label='youtube',
                    data='youtube'
                ),
                PostbackTemplateAction(
                    label='image',
                    data='image'
                )
            ]),
        CarouselColumn(
            text=' ', actions=[
                PostbackTemplateAction(
                    label='bukalapak',
                    data='bukalapak'
                ),
                PostbackTemplateAction(
                    label='osu',
                    data='osu'
                ),
                PostbackTemplateAction(
                    label='weather',
                    data='weather'
                )
            ])
    ])
    template_message = TemplateSendMessage(
        alt_text='meguri sent a photo.', template=carousel_template)
    line_bot_api.reply_message(token, template_message)






@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    token = event.reply_token


    if 'bot leave' not in event.message.text:
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
        if text.startswith('/help'):
            methodForHelp(token)
        if text.startswith('/video'):
            searchObj = re.search(r'/video (.*?);', text + ';', re.M | re.I)
            replaceText = searchObj.group(1).replace(' ', '+')
            jsonurl = urlopen(
                'https://www.googleapis.com/youtube/v3/search?part=snippet&q='+replaceText+'&type=video&key=AIzaSyDbfeClXLMorneLuPnEILavUgZkiB-3SrM&maxResults=25')
            jsonpart = json.loads(jsonurl.read())
            link = 'https://www.youtube.com/watch?v='+str(jsonpart['items'][randint(0,25)]['id']['videoId'])
            while (videoMessageForSearchAPI(token,link)=='0'):
                link='https://www.youtube.com/watch?v='+str(jsonpart['items'][randint(0,25)]['id']['videoId'])
            videoMessageForSearchAPI(token,link)







    else:
        if isinstance(event.source, SourceGroup):
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.leave_room(event.source.room_id)





@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text='ini image'))
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

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


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
    if len(event.postback.data) > 0:
        if event.postback.data == 'developer':
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='under development for personal amusement by :\ntitus efferian (line id: adhistitus) and\nkato@linuxsec.org'))
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


        else:
            searchObj = re.search(r'(.*?):(.*);', event.postback.data + ';', re.M | re.I)
            content = azureImage(searchObj.group(1))
            contentImage = goo_shorten_url(content['value'][int(searchObj.group(2))]['contentUrl'])
            thumbnail = content['value'][int(searchObj.group(2))]['thumbnailUrl']
            line_bot_api.reply_message(
                event.reply_token, ImageSendMessage(contentImage,thumbnail))


@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(
                event.beacon.hwid, event.beacon.dm)))



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


#google-APi : AIzaSyACppscHMJnI6GvWDJToAtS9vAUbGVcDr8
#azure api : db017bc371a34c488702df1801fc8f11
#google api :AIzaSyBDB-GF8QsWHoy7_Kc-wiTHRnrAeiJs8A8
#cloudinary.com : JsOgvhHvZyGIuPwv6jTPvoz2UYc