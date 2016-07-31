# coding=utf-8
import sys
import threading
import time

import itchat
from itchat.tools import htmlParser

groups = []
bgroups = []
block_groups = [u'西码会-U']
PREFIX = u'西码会-'


def update_groups():
    global groups, bgroups
    tmp_groups = []
    tmp_bgroups = []
    for group in itchat.get_chatrooms(update=True):
        if group['NickName'].startswith(PREFIX):
            tmp_groups.append(group['UserName'])
            itchat.get_batch_contract(group['UserName'])
        if group['NickName'] in block_groups :
            tmp_bgroups.append(group['UserName'])

    groups = tmp_groups
    bgroups = tmp_bgroups

    print(groups)
    print(bgroups)
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
        elif gid not in bgroups:
            in_group = True
    if not in_group: return []
    return destinations


def complex_reply():

    @itchat.msg_register(['Text', 'Map', 'Sharing'], isGroupChat=True)
    def text_reply(msg):
        print msg
        url = ''
        if msg['Url']: url = ' - ' + htmlParser.unescape(msg['Url'])
        for destination in destinations(msg):
            if url == '':
                itchat.send('%s: \n%s%s' % (msg['ActualDisplayName'], msg['Text'], url), destination)
            else:
                itchat.send(u'%s共享了一个链接: \n%s\n%s' % (msg['ActualDisplayName'], msg['Text'], url), destination)

    # @itchat.msg_register(['Note'], isGroupChat=True)
    # def text_reply(msg):
    #     for destination in destinations(msg):
    #         itchat.send(msg['Text'], destination)

    # @itchat.msg_register(['Note','Card', 'Sharing'])
    # def text_reply(msg):
    #     print(msg)
    #     itchat.send('@url@%s' % (msg['Content']), msg['FromUserName'])

    @itchat.msg_register(['Card'], isGroupChat=True)
    def card_reply(msg):
        print msg
        print msg['RecommendInfo']
        info = msg['RecommendInfo']
        wechat_number = u'微信号暂时不可得' if info['Alias'] == None or info['Alias'] == "" else info['Alias']
        for destination in destinations(msg):
            itchat.send( u'%s共享了一个名片:\n昵称：%s\n微信号：%s' % (msg['ActualDisplayName'], info['NickName'], wechat_number), destination)

    @itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video', 'Gif'], isGroupChat=True)
    def download_files(msg):
        dict = {'Picture': u"图片", "Gif": u"表情", "Recording": u"录音", "Video": u"小视频", "Attachment": u"文件"}
        fileDir = './storage/%s%s' % (msg['Type'], int(time.time()))
        flag = True
        if msg['Type'] == 'Gif': fileDir += '.gif'
        msg['Text'](fileDir)
        for destination in destinations(msg):
            itchat.send(u'%s发送了%s' % (msg['ActualDisplayName'], dict[msg['Type']]), destination)
            if not itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' or msg['Type'] == 'Gif' else 'fil', fileDir), destination):
                flag = False
        if not flag:
            for destination in destinations(msg):
                itchat.send(u'[暂不支持的官方表情]', destination)

    update_groups()
    itchat.run()


if __name__ == '__main__':
    itchat.auto_login(hotReload=True, enableCmdQR=True)
    complex_reply()
    itchat.dump_login_status()
