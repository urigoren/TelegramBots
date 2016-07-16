with open('latex.token','r') as f:
    TOKEN = f.readlines()[0].strip()
    print ('TOKEN: '+TOKEN)


import sys
import telepot
from telepot.delegate import per_chat_id, create_open
import urllib


class LatexBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(LatexBot, self).__init__(seed_tuple, timeout)

    def on_chat_message(self, msg):
		url=urllib.urlencode({'latex':msg}).replace('latex=','https://latex.codecogs.com/gif.latex?')
		f=urllib.urlopen(url)
        self.sender.sendPhoto(f)
        #self.sender.sendMessage(msg)
		f.close()


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(LatexBot, timeout=10)),
])
bot.setWebhook()
bot.message_loop(run_forever='Listening ...')