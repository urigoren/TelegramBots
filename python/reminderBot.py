from timelyBot import TimelyBot


class ReminderBot(TimelyBot):
    def processMessage(self, chat_id, message):
        pass

    def processTime(self, epoch):
        pass


if __name__ == '__main__':
    with open('reminder.token', 'r') as f:
        token = f.readlines()[0].strip()
    bot = ReminderBot(token, 'reminder_state.json')
    bot.runOnce()
