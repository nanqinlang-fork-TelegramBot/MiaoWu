#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from db import DB
from config import BOT_TOKEN

db = DB('MiaoWu.db')

def check_table(f):
    def g(*args):
        db.execute("CREATE TABLE IF NOT EXISTS '%d' (trigger, text);" % args[1].effective_chat.id)
        return f(*args)
    return g

@check_table
def add_command(bot, update):
    update.message.reply_text(update.message.text)

@check_table
def message(bot, update):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('add', add_command, Filters.group))
    updater.dispatcher.add_handler(MessageHandler(Filters.text and Filters.group, message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
