import sys
import telepot
from telepot.delegate import per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

with open('picnic.token','r') as f:
    TOKEN = f.readlines()[0].strip()
    print ('TOKEN: '+TOKEN)

class PicnicBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(PicnicBot, self).__init__(seed_tuple, timeout)
        self.group=0
        self.groceries={}
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
    def choose_items(self,txt,refer_to_command,counts=None):
        if counts:
            item_keyboard=[[KeyboardButton(text='/{r} {i} {c}'.format(r=refer_to_command,i=item,c=c)) for item in self.groceries.keys()] for c in counts]
        else:
            item_keyboard=[[KeyboardButton(text='/{r} {i}'.format(r=refer_to_command,i=item)) for item in self.groceries.keys()]]
        self.sender.sendMessage(txt, reply_markup=ReplyKeyboardMarkup( keyboard=item_keyboard,one_time_keyboard=True  ))

    def add(self,sender,content):
        if content=='':
            return 'Usage example:\n /add salad \n /add beer 6'
        try:
            item,count = content.split(' ',1)
            count = int(count)
        except:
            item = content
            count = 1
        self.groceries[item] = {'total': count}

    def remove(self,sender,content):
        if content=='':
            self.choose_items('Remove what item ?','remove')
            return None
        try:
            del self.groceries[content]
        except:
            return

    def bring(self,sender,content):
        if content=='':
            self.choose_items('Bring what ?','bring',[1,2])
            return None
        try:
            item,count = content.split(' ',1)
            count = int(count)
        except:
            item = content
            count = 1
        try:
            if sender in self.groceries[item].keys():
                self.groceries[item][sender]+=count
            else:
                self.groceries[item][sender]=count
            return self.sender2name[sender]+' is bringing {c} {i}'.format(c=count,i=item)
        except:
            return

    def regret(self,sender,content):
        ret=[]
        for item in self.groceries.keys():
            if sender in self.groceries[item].keys():
                ret.append({'user':self.sender2name[sender],'item':item,'count':self.groceries[item][sender]})
                del self.groceries[item][sender]
        return '\n'.join(['{user} no longer brings {count} {item}'.format(**r) for r in ret])

    def remaining(self,sender,content):
        ret=[]
        for item, counts in self.groceries.items():
            total = counts['total']
            remaining = 2*total - sum(counts.values())
            ret.append('{i}: {r}'.format(i=item,r=remaining))
        if len(ret)==0:
            return 'Woohoo! No remaining items'
        return 'Remaining items:'+'\n'.join(ret)

    def my(self,sender,content):
        ret=[]
        for item, counts in self.groceries.items():
            if not sender in counts.keys():
                continue
            ret.append('{i}: {c}'.format(i=item,c=counts[sender]))
        if len(ret)==0:
            return self.sender2name[sender]+", your picnic list is empty,\n Use /bring to take part in the picnic"
        return self.sender2name[sender]+' brings:'+'\n'.join(ret)

    def list(self,sender,content):
        ret=[]
        for item, counts in self.groceries.items():
            total = counts['total']
            ret.append('{i}:{t}'.format(i=item,t=total))
        if len(ret)==0:
            return "Picnic list is empty,\n Use /add to populate it"
        return '\n'.join(ret)

    def help(self,sender,content):
        return '''Use /add and /remove to modify the picnic list
        /bring and /regret to share what you bring
        /list, /remaining and /my to view the current list status
        '''


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(PicnicBot, timeout=1000)),
])
bot.setWebhook()
bot.message_loop(run_forever='Listening ...')