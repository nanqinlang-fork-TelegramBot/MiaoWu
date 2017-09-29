#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from random import randint
from db import DB
from config import BOT_TOKEN

def check_table(f):
    def g(*args):
        db.execute("CREATE TABLE IF NOT EXISTS '%s' (trigger TEXT, result TEXT);" % args[1].effective_chat.id)
        return f(*args)
    return g

def split_two(s, c):
    index = s.find(c)
    if index == -1:
        return s, ''
    return s[:index], s[index + 1:]

@check_table
def add_command(bot, update):
    try:
        trigger, result = split_two(split_two(update.message.text, ' ')[1], '@')
        assert trigger and result, 'Usage: /add trigger@result'
        chat_id = update.effective_chat.id
        look_up = db.execute("SELECT COUNT() FROM '%s' WHERE trigger = ? AND result = ?" % chat_id, (trigger, result))
        assert next(look_up)[0] == 0, 'Already added: %s - %s' % (trigger, result)
        db.execute("INSERT INTO '%s' (trigger, result) VALUES (?, ?)" % chat_id, (trigger, result))
        update.message.reply_text('Added: %s - %s' % (trigger, result))
    except AssertionError as e:
        update.message.reply_text(str(e))

@check_table
def list_command(bot, update):
    try:
        _, trigger = split_two(update.message.text, ' ')
        assert trigger, 'Usage: /list trigger'
        look_up = db.execute("SELECT result FROM '%s' WHERE trigger = ?" % update.effective_chat.id, (trigger,))
        look_up = list(look_up)
        assert len(look_up) > 0, 'No result found.'
        look_up = [x[0] for x in look_up]
        update.message.reply_text('\n'.join(look_up))
    except AssertionError as e:
        update.message.reply_text(str(e))

@check_table
def listall_command(bot, update):
    try:
        look_up = db.execute("SELECT trigger, result FROM '%s'" % update.effective_chat.id)
        look_up = list(look_up)
        assert len(look_up) > 0, 'No result found.'
        look_up = ['%s - %s' % (x[0], x[1]) for x in look_up]
        update.message.reply_text('\n'.join(look_up))
    except AssertionError as e:
        update.message.reply_text(str(e))

@check_table
def del_command(bot, update):
    try:
        trigger, result = split_two(split_two(update.message.text, ' ')[1], '@')
        assert trigger and result, 'Usage: /del trigger@result'
        chat_id = update.effective_chat.id
        look_up = db.execute("SELECT COUNT() FROM '%s' WHERE trigger = ? AND result = ?" % chat_id, (trigger, result))
        assert next(look_up)[0] > 0, '%s - %s not exists.' % (trigger, result)
        db.execute("DELETE FROM '%s' WHERE trigger = ? AND result = ?" % chat_id, (trigger, result))
        update.message.reply_text('Deleted: %s - %s' % (trigger, result))
    except AssertionError as e:
        update.message.reply_text(str(e))

def help_command(bot, update):
    update.message.reply_text("""/add trigger@result: Add a new trigger-result pair.
/list trigger: List all results corresponding to a trigger.
/listall: List all trigger-result pairs.
/del trigger@result: Delete a trigger-result pair.
/help: Show this help""")

@check_table
def message(bot, update):
    look_up = db.execute("SELECT * FROM '%s'" % update.effective_chat.id)
    look_up = list(look_up)
    look_up.sort(key=lambda x: len(x[0]), reverse=True)
    for trigger, result in look_up:
        if trigger in update.message.text:
            results = [x[1] for x in look_up if x[0] == trigger]
            update.message.reply_text(results[randint(0, len(results) - 1)])
            return

def main():
    global db
    db = DB('MiaoWu.db')
    updater = Updater(BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('add', add_command, Filters.group))
    updater.dispatcher.add_handler(CommandHandler('list', list_command, Filters.group))
    updater.dispatcher.add_handler(CommandHandler('listall', listall_command, Filters.group))
    updater.dispatcher.add_handler(CommandHandler('del', del_command, Filters.group))
    updater.dispatcher.add_handler(CommandHandler('help', help_command, Filters.group))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
