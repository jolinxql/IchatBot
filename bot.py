# coding=utf-8
import sys
import threading
import time

import itchat
from itchat.tools import htmlParser

groups = []
PREFIX = u'机器人'


def update_groups():
    global groups
    groups = []
    for group in itchat.get_chatrooms(update=True):
        if group['NickName'].startswith(PREFIX):
            groups.append(group['UserName'])
            itchat.get_batch_contract(group['UserName'])
    print(time.time())
    thread = threading.Timer(55, update_groups)
    thread.daemon = True
    thread.start()


def destinations(msg):
    destinations = []
    in_group = False
    for gid in groups:
        if gid != msg['FromUserName']:
            destinations.append(gid)
        else:
            in_group = True
    if not in_group: return []
    return destinations


def complex_reply():
    @itchat.msg_register(['Text', 'Map', 'Card', 'Sharing'], isGroupChat=True)
    def text_reply(msg):
        url = ''
        if msg['Url']: url = ' - ' + htmlParser.unescape(msg['Url'])
        for destination in destinations(msg):
            itchat.send('%s: %s%s' % (msg['ActualDisplayName'], msg['Text'], url), destination)

    @itchat.msg_register(['Note'], isGroupChat=True)
    def text_reply(msg):
        for destination in destinations(msg):
            itchat.send(msg['Text'], destination)

    # @itchat.msg_register(['Note','Card', 'Sharing'])
    # def text_reply(msg):
    #     print(msg)
    #     itchat.send('@url@%s' % (msg['Content']), msg['FromUserName'])

    @itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video', 'Gif'], isGroupChat=True)
    def download_files(msg):
        fileDir = '%s%s' % (msg['Type'], int(time.time()))
        if msg['Type'] == 'Gif': fileDir += '.gif'
        msg['Text'](fileDir)
        for destination in destinations(msg):
            itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' or msg['Type'] == 'Gif' else 'fil', fileDir),
                        destination)
            itchat.send('%s by %s' % (msg['Type'], msg['ActualDisplayName']), destination)

    update_groups()
    itchat.run()


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    complex_reply()
    itchat.dump_login_status()
