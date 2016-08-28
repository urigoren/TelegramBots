# -*- coding: utf-8 -*-
from timelyBot import TimelyBot


class ReminderBot(TimelyBot):
    def processMessage(self, state, message):
        if message.startswith('+'):
            ts, data = message[1:].split(' ', 1)
            ts=int(ts)
            if not ts in state.keys():
                state[ts] = []
            state[ts].append(data)
            return state

    def processTime(self, state, epoch):
        ret = state
        outgoing = []
        for timestamp, msgs in state.items():
            if timestamp.isdigit() and (int(timestamp) < epoch):
                outgoing.extend(msgs)
                del ret[timestamp]
        ret['outgoing'] = outgoing
        return ret


if __name__ == '__main__':
    with open('reminder.token', 'r') as f:
        token = f.readlines()[0].strip()
    bot = ReminderBot(token, 'reminder_state.json')
    print (bot.state)
    bot.runOnce()
    print (bot.state)