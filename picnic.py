import sys
import telepot
from telepot.delegate import per_chat_id, create_open

with open('picnic.token','r') as f:
    TOKEN = f.readlines()[0].strip()
    print ('TOKEN: '+TOKEN)

class PicnicBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(PicnicBot, self).__init__(seed_tuple, timeout)
        self.group=0
        self.db={}
        self.sender2name={}

    def on_chat_message(self, msg):
        response = None
        if msg['chat']['type']!='group':
            self.sender.sendMessage('This is a group bot')
            return
        self.group = msg['chat']['id']
        sender = msg['from']['id']
        self.sender2name[sender]= msg['from']['first_name']+' '+msg['from']['last_name']
        if msg['text'].find('/') > -1:
            if msg['text'].find(' ')>-1:
                name,param = msg['text'].split(' ',1)

            else:
                name = msg['text']
                param = ''
            if name.find('@')>-1:
                name = name[:name.find('@')]
            name = name.replace('/','')
            print ('Calling {n} with {p}'.format(n=name,p=param))
            response = getattr(self, name)(sender, param.strip())
        else:
            self.sender.sendMessage('Unknown command')
            return
        if response:
            self.sender.sendMessage(response)

    def add(self,sender,content):
        if content=='':
            return 'Add what ?'
        try:
            item,count = content.split(' ',1)
            count = int(count)
        except:
            item = content
            count = 1
        self.db[item] = {'total': count}

    def remove(self,sender,content):
        if content=='':
            return 'Remove what ?'
        try:
            del self.db[content]
        except:
            return

    def bring(self,sender,content):
        if content=='':
            return 'Bring what ?'
        try:
            item,count = content.split(' ',1)
            count = int(count)
        except:
            item = content
            count = 1
        try:
            if sender in self.db[item].keys():
                self.db[item][sender]+=count
            else:
                self.db[item][sender]=count
        except:
            return

    def unbring(self,sender,content):
        if content=='':
            return 'Unbring what ?'
        try:
            item,count = content.split(' ',1)
            count = int(count)
        except:
            item = content
            count = 1
        self.bring(sender,'{i} {c}'.format(i=item,c=-count))

    def status(self,sender,content):
        if content=='all':
            return self.db
        #remaining
        ret={}
        for item, counts in self.db.items():
            total = counts['total']
            remaining = 2*total - sum(counts.values())
            ret[item]=remaining
        return ret


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(PicnicBot, timeout=1000)),
])
bot.setWebhook()
bot.message_loop(run_forever='Listening ...')