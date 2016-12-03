# -*- coding: utf-8 -*-
from icalendar import Calendar
from datetime import datetime, date
import requests
import cPickle as pickle
import os
import json
from pytz import UTC


def fixdate(d):
    if isinstance(d, datetime):
        if d.tzinfo is None:
            return d.replace(tzinfo=UTC)
        else:
            return d
    if isinstance(d, date):
        return datetime.combine(d, datetime.min.time()).replace(tzinfo=UTC)
    raise TypeError("unknown type for " + repr(d))

class icalBot:
    def __init__(self, token):
        self.token = token
        self.events = []
        if os.path.isfile('icalBot.events'):
            with open('icalBot.events', 'r') as f:
                self.events = pickle.load(f)

    def __del__(self):
        with open('icalBot.events', 'w') as f:
            pickle.dump(self.events,f)

    def fetch_events(self, ical_url):
        response = requests.get(ical_url, verify=False)
        if response.status_code == 200:
            cal = Calendar.from_ical(response.content)
            #day = lambda dt: tuple(map(int, str(dt).split(' ', 1)[0].split('-', 2)))
            self.events = [(fixdate(e['DTSTART'].dt), e['SUMMARY'].title()) for e in cal.walk('vevent') if fixdate(e['DTSTART'].dt) >= datetime.now(UTC)]
        else:
            raise SystemError('status code is ' + str(response.status_code))

    def telegram_message(self, chat_id, message):
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

    def telegram_inbox(self):
        """telegram api getUpdates"""
        updates_url = 'https://api.telegram.org/bot' + self.token + '/getUpdates'
        r = requests.post(updates_url, data={'offset': 0})
        if r.status_code == 200:
            return json.loads(r.text)['result']
        return []

    def tick(self, chat_id):
        past_events = [(d, t) for d, t in self.events if d <= datetime.now(d.tzinfo)]
        self.events = [(d, t) for d, t in self.events if d > datetime.now(d.tzinfo)]
        print self.events
        for d, t in past_events:
            self.telegram_message(chat_id, t)
            print (t)

if __name__ == '__main__':
    with open("ical.json",'r') as f:
        config = json.load(f)
    ib = icalBot(config['token'])
    if datetime.now().hour % 6 ==0 and datetime.now().minute in range(20):
        #update the file once every 6 hours
        ib.fetch_events(config['ical'])
    ib.tick(config['chat'])
