with open('reminder.token','r') as f:
    TOKEN = f.readlines()[0].strip()
    print ('TOKEN: '+TOKEN)

import json
import requests
import os
from datetime import datetime


def getUpdates(last_read=0):
    """telegram api getUpdates"""
    updates_url='https://api.telegram.org/bot'+TOKEN+'/getUpdates'
    if last_read==0:
        r = requests.post(updates_url)
    else:
        r = requests.post(updates_url, data={'offset':last_read+1})
    if r.status_code == 200:
        return json.loads(r.text)['result']
    return []


def sendMessage(chat_id,message,keyboard=None):
    """telegram api sendMessage"""
    message_url='https://api.telegram.org/bot'+TOKEN+'/sendMessage'
    response={'chat_id':chat_id,'text':message}
    if type(keyboard)==list:
        if type(keyboard[0])!=list:
            keyboard=[keyboard]
        response['reply_markup']=json.dumps({'keyboard':keyboard,'one_time_keyboard':True})
    r = requests.post(message_url, data=response)
    return json.loads(r.text)

def processMessage(chat_id,message):
    """handles question-answer queries"""
    global state
    return None

def processTime(now):
    """handles time depended queries"""
    global state
    return None

if __name__=='__main__':
    if os.path.isfile('reminder_state.json'):
        with open('reminder_state.json', 'r') as f:
            state = json.load(f)
    else:
        state={'last_read':0}
    processTime(datetime.now())
    incoming = sorted([(u['update_id'],u['message']['chat']['id'],u['message']['text']) for u in getUpdates(state['last_read'])])
    for update_id,chat_id,message in incoming:
        answer = processMessage(chat_id,message)
        if type(answer)==str:
            sendMessage(chat_id,answer)
        elif type(answer)==tuple:
            sendMessage(chat_id, answer[0],answer[1])
        state['last_read']=update_id
    with open('reminder_state.json','w') as f:
        json.dump(state,f)