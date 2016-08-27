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

    def sendMessage(self, chat_id, message, keyboard=None):
        """telegram api sendMessage"""
        message_url = 'https://api.telegram.org/bot' + self.token + '/sendMessage'
        response = {'chat_id': chat_id, 'text': message}
        if type(keyboard) == list:
            if type(keyboard[0]) != list:
                keyboard = [keyboard]
            response['reply_markup'] = json.dumps({'keyboard': keyboard, 'one_time_keyboard': True})
        r = requests.post(message_url, data=response)
        return json.loads(r.text)

    def processMessage(self, chat_id, message):
        """handles question-answer queries"""
        raise SyntaxWarning('processMessage is not implemented')
        return None

    def processTime(self, epoch):
        """handles time depended queries"""
        raise SyntaxWarning('processTime is not implemented')
        return None

    def runOnce(self):
        self.processTime(int(time.time()))
        incoming = sorted(
            [(u['update_id'], u['message']['chat']['id'], u['message']['text']) for u in self.getUpdates()])
        for update_id, chat_id, message in incoming:
            answer = self.processMessage(chat_id, message)
            if type(answer) == str:
                self.sendMessage(chat_id, answer)
            elif type(answer) == tuple:
                self.sendMessage(chat_id, answer[0], answer[1])
            self.state['last_read'] = update_id

    def runEvery(self, interval):
        while True:
            try:
                self.runOnce()
                time.sleep(interval)
            except Exception, e:
                sys.stdout.write(str(e) + '\n')
