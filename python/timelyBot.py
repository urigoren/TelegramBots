# -*- coding: utf-8 -*-
import sys
import json
import requests
import os
import time


class TimelyBot:
    def __init__(self, token, state_file):
        self.token = token
        self.state_file = state_file
        if os.path.isfile(state_file):
            with open(state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {'last_read': 0}

    def __del__(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f)

    def getUpdates(self):
        """telegram api getUpdates"""
        updates_url = 'https://api.telegram.org/bot' + self.token + '/getUpdates'
        r = requests.post(updates_url, data={'offset': self.state['last_read'] + 1})
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
        raise SyntaxWarning('processMessage is not implemented')
        return None

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
            if chat_id == 'last_read':
                continue
            self.handleOutgoing(chat_id, self.processTime(self.state[chat_id], self.now()))
        # iterate incoming messages
        incoming = sorted(
            [(u['update_id'], u['message']['chat']['id'], u['message']['text']) for u in self.getUpdates()])
        for update_id, chat_id, message in incoming:
            if not chat_id in self.state.keys():
                self.state[chat_id] = dict()
            self.handleOutgoing(chat_id, self.processMessage(self.state[chat_id], message))
            self.state['last_read'] = update_id

    def runEvery(self, interval):
        while True:
            try:
                self.runOnce()
                time.sleep(interval)
            except Exception, e:
                sys.stdout.write(str(e) + '\n')
