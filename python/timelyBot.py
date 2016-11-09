# -*- coding: utf-8 -*-
import json
import os
import sys
import time

import requests


class TimelyBot:
    def __init__(self, token, state_file):
        self.token = token
        self.state_file = state_file
        self.state = {}
        self.load()

    def __del__(self):
        self.save()

    def load(self):
        print ('saving state')
        if os.path.isfile(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {'meta': {'last_read': 0}}
        print (self.state)

    def save(self):
        print ('saving state')
        print (self.state)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f)

    def getUpdates(self):
        """telegram api getUpdates"""
        updates_url = 'https://api.telegram.org/bot' + self.token + '/getUpdates'
        r = requests.post(updates_url, data={'offset': self.state['meta']['last_read'] + 1})
        if r.status_code == 200:
            return json.loads(r.text)['result']
        return []

    def sendMessage(self, chat_id, message):
        """telegram api sendMessage"""
        message_url = 'https://api.telegram.org/bot' + self.token + '/sendMessage'
        if type(message) == tuple:
            message, keyboard = message
        else:
            keyboard = None
        response = {'chat_id': chat_id, 'text': message}
        if type(keyboard) == list:
            if type(keyboard[0]) != list:
                keyboard = [keyboard]
            response['reply_markup'] = json.dumps({'keyboard': keyboard, 'one_time_keyboard': True})
        r = requests.post(message_url, data=response)
        return json.loads(r.text)

    def processMessage(self, state, message):
        """handles question-answer queries"""
        if message.find('/') > -1:
            if message.find(' ') > -1:
                name, param = message.split(' ', 1)
            else:
                name = 'default'
                param = message
            if name.find('@') > -1:
                name = name[:name.find('@')]
            name = name.replace('/', '').lower() + 'Command'
            print ('Calling {n} with {p}'.format(n=name, p=param))
            commandFunction = getattr(self, name, None)
            if commandFunction is not None:
                print state
                state = commandFunction(state, param.strip())
            return state
        else:
            self.defaultCommand(state, message)

    def processTime(self, state, epoch):
        """handles time depended queries"""
        raise SyntaxWarning('processTime is not implemented')
        return None

    def now(self):
        return int(time.time())

    def handleOutgoing(self, chat_id, new_state):
        if type(new_state) == dict:
            self.state[chat_id] = new_state
        elif new_state:
            self.state[chat_id]['outgoing'] = new_state
        if 'outgoing' in self.state[chat_id].keys():
            if type(self.state[chat_id]['outgoing']) != list:
                self.state[chat_id]['outgoing'] = [self.state[chat_id]['outgoing']]
            for msg in self.state[chat_id]['outgoing']:
                self.sendMessage(chat_id, msg)
            del self.state[chat_id]['outgoing']

    def runOnce(self):
        # iterate acive chats
        for chat_id in self.state.keys():
            if chat_id == 'meta':
                continue
            self.handleOutgoing(chat_id, self.processTime(self.state[chat_id], self.now()))
            if self.state[chat_id] == {}:
                del self.state[chat_id]
        # iterate incoming messages
        incoming = sorted(
            [(u['update_id'], u['message']['chat']['id'], u['message']['text']) for u in self.getUpdates()])
        for update_id, chat_id, message in incoming:
            if not chat_id in self.state.keys():
                self.state[chat_id] = dict()
            self.handleOutgoing(chat_id, self.processMessage(self.state[chat_id], message))
            self.state['meta']['last_read'] = update_id

    def runEvery(self, interval):
        while True:
            try:
                self.runOnce()
                time.sleep(interval)
            except Exception, e:
                sys.stdout.write(str(e) + '\n')
