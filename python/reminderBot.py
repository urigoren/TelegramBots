# -*- coding: utf-8 -*-
from timelyBot import TimelyBot
import os


class ReminderBot(TimelyBot):
    def timeParse(self,s):
        try:
            number,quant=s.split(' ',1)
            quant=quant.lower()
            number=int(number)
            if quant.find('sec')>-1:
                quant=1
            elif quant.find('min')>-1:
                quant=60
            elif quant.find('hour') > -1:
                quant = 3600
            elif quant.find('day') > -1:
                quant = 3600*24
            elif quant.find('week') > -1:
                quant = 3600 * 24 * 7
            elif quant.find('month') > -1:
                quant = 3600 * 24 * 30
            return number*quant
        except:
            return None

    def defaultCommand(self, state, message):
        if message=='/ok':
            if 'session' in state.keys():
                del state['session']
        elif message=='/debug':
            print (state)
        return state

    def clearCommand(self, state, message):
        return {}

    def todoCommand(self, state, message):
        data = message.split(' ', 1)
        ts=self.now()+3600*24
        if not ts in state.keys():
            state[ts] = []
        state['session']='{t}.{i}'.format(t=ts,i=len(state[ts]))
        state[ts].append(data)
        state['outgoing']=[('You will be reminded same time tomorrow',[['/ok','/in 3 hours','/in 6 hours'],['/in 1 day','/in 3 days','/in 7 days']])]
        return state

    def inCommand(self, state, message):
        if not 'session' in state.keys():
            state['outgoing']=['could not understand',str(state.keys())]
            return state
        ts,i=state['session'].split('.',1)
        msg=state[ts][int(i)]
        state[ts].remove(msg)
        addition = self.timeParse(message)
        if addition is None:
            state['outgoing'] = ['could not parse']
            return state
        new_ts=self.now()+addition
        if not new_ts in state.keys():
            state[new_ts]=[]
        state[new_ts].append(msg)

    def processTime(self, state, epoch):
        ret = state
        outgoing = []
        for timestamp, msgs in state.items():
            if str(timestamp).isdigit() and (int(timestamp) < epoch):
                outgoing.extend(msgs)
                del ret[timestamp]
                ret['overdo']=ret['overdo']+msgs if 'overdo' in ret.keys() else msgs
        ret['outgoing'] = outgoing
        return ret

if __name__ == '__main__':
    with open('reminder.token', 'r') as f:
        token = f.readlines()[0].strip()
    bot = ReminderBot(token, 'reminder_state.json')
    bot.runEvery(4)
    print (bot.state)
    bot.runOnce()
    print (bot.state)