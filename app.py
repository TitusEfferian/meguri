from __future__ import unicode_literals



import errno

import os
import re



import tempfile


from urllib.request import urlopen

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

    ImageSendMessage)

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
def getJsonForBeatmapDetails(id,mode):
    jsonurl = urlopen('https://osu.ppy.sh/api/get_beatmaps?k=37967304c711a663eb326dcf8b41e1a5987e2b7f&m='+mode+'&b='+id)
    jsonpart=json.loads(jsonurl.read())
    return jsonpart[0]['title']+' - '+jsonpart[0]['version']
def getJsonForBeatmapsetId(id,mode):
    jsonurl = urlopen('https://osu.ppy.sh/api/get_beatmaps?k=37967304c711a663eb326dcf8b41e1a5987e2b7f&m='+mode+'&b='+id)
    jsonpart=json.loads(jsonurl.read())
    return jsonpart[0]['beatmapset_id']
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

            jsonUrlForGetUserBest = urlopen(
                'https://osu.ppy.sh/api/get_user_best?k=37967304c711a663eb326dcf8b41e1a5987e2b7f&u=' + nickname + '&m=' + mode)
            jsonPartForGetUserBest = json.loads(jsonUrlForGetUserBest.read())
            list = []
            for x in range(0, 5):
                list.append(jsonPartForGetUserBest[x])
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
                    ]),
                CarouselColumn(
                    text=getJsonForBeatmapDetails(list[0]['beatmap_id'],mode),
                    thumbnail_image_url='https://b.ppy.sh/thumb/'+getJsonForBeatmapsetId(list[0]['beatmap_id'],mode)+'l.jpg', title=username+' - '+str(round(float(list[0]['pp'])))+'pp', actions=[
                        URITemplateAction(
                            label='go to map', uri='https://osu.ppy.sh/b/'+list[0]['beatmap_id']+'?m='+mode)
                    ]),
                CarouselColumn(
                    text=getJsonForBeatmapDetails(list[1]['beatmap_id'], mode),
                    thumbnail_image_url='https://b.ppy.sh/thumb/' + getJsonForBeatmapsetId(list[1]['beatmap_id'],
                                                                                           mode) + 'l.jpg',
                    title=username + ' - ' + str(round(float(list[1]['pp'])))+'pp', actions=[
                        URITemplateAction(
                            label='go to map', uri='https://osu.ppy.sh/b/' + list[1]['beatmap_id'] + '?m=' + mode)
                    ]),
                CarouselColumn(
                    text=getJsonForBeatmapDetails(list[2]['beatmap_id'], mode),
                    thumbnail_image_url='https://b.ppy.sh/thumb/' + getJsonForBeatmapsetId(list[2]['beatmap_id'],
                                                                                           mode) + 'l.jpg',
                    title=username + ' - ' + str(round(float(list[2]['pp'])))+'pp', actions=[
                        URITemplateAction(
                            label='go to map', uri='https://osu.ppy.sh/b/' + list[2]['beatmap_id'] + '?m=' + mode)
                    ]),
                CarouselColumn(
                    text=getJsonForBeatmapDetails(list[3]['beatmap_id'], mode),
                    thumbnail_image_url='https://b.ppy.sh/thumb/' + getJsonForBeatmapsetId(list[3]['beatmap_id'],
                                                                                           mode) + 'l.jpg',
                    title=username + ' - ' + str(round(float(list[3]['pp'])))+'pp', actions=[
                        URITemplateAction(
                            label='go to map', uri='https://osu.ppy.sh/b/' + list[3]['beatmap_id'] + '?m=' + mode)
                    ])
            ])
            template_message = TemplateSendMessage(
                alt_text='tamachan sent a photo.', template=carousel_template)
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


    else:
        if isinstance(event.source, SourceGroup):
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.leave_room(event.source.room_id)


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


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
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))


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