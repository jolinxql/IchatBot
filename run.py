import time

import itchat

groups = {}
groups_no = {}
group_member_names = {}



def destinations(msg):
    destinations = []
    global groups, groups_no
    if (isinstance(msg['Text'], basestring)) and msg['Text'][:5] == 'start' and msg['Text'][5:]:
        if groups.has_key(msg['Text'][5:]):
            groups_no.pop(groups[msg['Text'][5:]])
            groups.pop(msg['Text'][5:])
        groups[msg['Text'][5:]] = msg['FromUserName']
        groups_no[msg['FromUserName']] = msg['Text'][5:]
        set_group_member_names(msg['FromUserName'])
        itchat.send('set group %s to %s' % (msg['Text'][5:], msg['FromUserName']), msg['FromUserName'])
    print(groups)
    if groups_no.has_key(msg['FromUserName']):
        for key, gid in groups.iteritems():
            if gid != msg['FromUserName']: destinations.append(gid)
    return destinations


def set_group_member_names(gid):
    data = itchat.get_batch_contract(gid)
    global group_member_names
    group_member_names[gid] = {}
    for member in data['MemberList']:
        name = member['DisplayName']
        if not member['DisplayName'].strip(): name = member['NickName']
        group_member_names[gid][member['UserName']] = name + '#' + data['NickName']


def get_sender_name(msg):
    return group_member_names.get(msg['FromUserName'], {}).get(msg['ActualUserName'], msg['ActualNickName'])



def complex_reply():
    @itchat.msg_register(['Text', 'Map', 'Note','Card', 'Sharing'], isGroupChat=True)
    def text_reply(msg):
        url = ''
        if msg['Url']: url = ' - ' + msg['Url']
        for destination in destinations(msg):
            itchat.send('%s: %s%s' % (get_sender_name(msg), msg['Text'],url), destination)

    @itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video'], isGroupChat=True)
    def download_files(msg):
        fileDir = '%s%s' % (msg['Type'], int(time.time()))
        msg['Text'](fileDir)
        for destination in destinations(msg):
            itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', fileDir), destination)
            itchat.send('%s by %s' % (msg['Type'], get_sender_name(msg)), destination)

    # @itchat.msg_register(['Note','Card', 'Sharing'])
    # def text_reply(msg):
    #     print(msg)
    #     itchat.send('@url@%s' % (msg['Content']), msg['FromUserName'])

    itchat.run()



if __name__ == '__main__':
    itchat.auto_login()
    complex_reply()
