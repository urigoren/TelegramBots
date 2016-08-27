# -*- coding: utf-8 -*-
with open('latex.token','r') as f:
    TOKEN = f.readlines()[0].strip()
    print ('TOKEN: '+TOKEN)
	
import sys,os,json
import telepot
from telepot.delegate import per_chat_id, create_open

with open('config.json','r') as f:
	config=json.load(f)

class ifThenBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(ifThenBot, self).__init__(seed_tuple, timeout)
        self.q=''
        self.scenarios={}

    def on_chat_message(self, msg):
        if not 'text' in msg.keys():
                return
        if os.path.isfile('scenarios.json'):
			with open('scenarios.json','r') as f:
				self.scenarios=json.load(f)
        txt=msg['text']
		print ('recieving '+txt)
        if txt.startswith(config['name']):
			print ('Command "NAME"')
			txt=txt.replace(config['name']+' ' , u'')
			for q,a in self.scenarios.items():
				if txt.find(q)>-1:
					self.sender.sendMessage(a)
        elif txt.startswith(config['if']):
			print ('Command "IF"')
			self.q=txt.replace(config['if']+' ',u'')
        elif txt.startswith(config['then']):
			print ('Command "THEN"')
			if self.q=='':
				print ('No question, ignoring')
				return
			self.scenarios[self.q]=txt.replace(config['then']+' ',u'')
			with open('scenarios.json','w') as f:
				json.dump(self.scenarios,f)
		elif txt==config['status']:
			print ('Command "STATUS"')
			self.sender.sendMessage('\n'.join(map(lambda x:x[0]+': '+x[1],self.scenarios.items())))
		elif txt==config['reset']:
			print ('Command "RESET"')
			self.scenarios={}


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(ifThenBot, timeout=20)),
])
bot.setWebhook()
bot.message_loop(run_forever='Listening ...')
