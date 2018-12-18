#!/usr/bin/env python
# -*- coding:utf-8 -*-

from sys import path
from configparser import ConfigParser
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import re


from GitApi import GitHub
from dbhelper import DBHelper, Config

# Connect and Setup the database
db = DBHelper()
db.setup()

# Bot Configuration
config = ConfigParser()
config.read_file(open('config.ini'))

# Connecting the telegram API
# Updater will take the information and dispatcher connect the message to
# the bot
up = Updater(token=config['DEFAULT']['token'])
dispatcher = up.dispatcher



# Home function
def start(bot, update):
    print("Comando start")
    # Home message
    msg = "Hello {user_name}! I'm {bot_name}. \n"
    msg += "What would you like to do? \n"
    msg += "/org + organization - List an organization's repositories \n"
    msg += "/today + organization - List today's commits for an organization\n"
    msg += "Ex: /org devmobufrj | /today devmobufrj"

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         user_name=update.message.from_user.first_name,
                         bot_name=bot.name))


# Function to list the Organization's repositories
def org(bot, update, args):
    print("Comando org")
    gh = GitHub()
    for organization in args:
        bot.send_message(chat_id=update.message.chat_id,
                         text='{0} Listing the Organization\'s repositories '
                         .format('\U0001F5C4') +
                         '[{0}](https://github.com/{0}) >>'.format(
                             organization),
                         parse_mode=ParseMode.MARKDOWN)

        bot.send_message(chat_id=update.message.chat_id,
                         text=gh.get_org_repos(organization))


# Function to list the Organization's repositories
def today(bot, update, args):
    print("Comando today")

    gh = GitHub()
    if len(args) < 1:
        bot.send_message(chat_id=update.message.chat_id,
                            text='Please provide an organization name')
        return

    if len(args) > 1:
        bot.send_message(chat_id=update.message.chat_id,
                            text='Please provide only one valid username for the organization')
        return

    organization = args[0]
    bot.send_message(chat_id=update.message.chat_id,
                        text='{0} Listing todays updates for '
                        .format('\U0001F5C4') +
                        '[{0}](https://github.com/{0}) >>'.format(
                            organization),
                        parse_mode=ParseMode.MARKDOWN)

    bot.send_message(chat_id=update.message.chat_id,
                        text=gh.get_org_today(organization))


def handle_todo(bot, update, args):
    print("Handle todo")
    try:
        text = " ".join(args)
        items = db.get_items()
        print("Items: ")
        print(items)

        if text in items:
            db.delete_item(text)
            items = db.get_items()
        else:
            db.add_item(text)
            items = db.get_items()

        msg = "TODO List:\n"
        msg += "\n".join(items)
        bot.send_message(chat_id=update.message.chat_id,
                    text=msg)
    except KeyError:
        print("Key error pass")
        pass

def config(bot, update, args):
    msg = ""
    if len(args) < 2 or len(args) > 2:
        msg = "The config command requires 2 parameters.\n"
        msg += usage_config()
    else:
        if args[0] == "time":
            match = re.match("([0-1]{0,1}[0-9])([ap]m)", args[1])
            if match is not None:
                hour = int(match.group(1))
                if hour > 12 or hour < 0:
                    msg = "Invalid hour.\n"
                    msg += usage_config()
                else:
                    ampm = match.group(2)
                    msg = "Data válida: " + match.group(0)
                    msg += "\n" + get_time()
                    print("Fazer teste")
                    try:
                        config = db.set_config(update.message.chat_id,
                            "devmobufrj", int(match.group(1)))
                        msg += "\n" + config.to_string()
                    except Exception as e:
                        print(e)
            else:
                msg = "Invalid hour.\n"
                msg += usage_config()
        elif args[0] == "days":
            print("Ok")
            # TODO
        else:
            msg = "Invalid configuration key.\nUse one of: time, days\n"
            msg += usage_config()
    print(update.message)
    bot.send_message(chat_id=update.message.chat_id,
                text=msg)

def usage_config():
    usage = ""
    usage += "Usage:\n"
    usage += "  /config time {0-12}[am/pm]\n"
    usage += "  /config days [weekdays/daily]\n"
    usage += "Examples:\n"
    usage += "  /config time 9am\n"
    usage += "  /config time 5pm\n"
    usage += "  /config days weekdays\n"
    usage += "  /config days daily\n"
    usage += get_time() + "\n"
    return usage


def get_time():
    return "UTC Time(GMT+0): " + datetime.utcnow().strftime("%H:%M")


def error_handler(bot, update, error):
    print("Erro: ")
    print(error)


# Add handlers to dispatcher
dispatcher.add_error_handler(error_handler)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('todo', handle_todo, pass_args=True))
dispatcher.add_handler(CommandHandler('today', today, pass_args=True))
dispatcher.add_handler(CommandHandler('config', config, pass_args=True))
dispatcher.add_handler(CommandHandler('org', org, pass_args=True))

# Start the program
up.start_polling()
