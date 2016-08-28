# -*- coding: utf-8 -*-
from timelyBot import TimelyBot


class ReminderBot(TimelyBot):
    def defaultCommand(self, state, message):
        state['outgoing']=[message]
        return state

    def remindinCommand(self, state, message):
        ts, data = message.split(' ', 1)
        ts=int(ts)+self.now()
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