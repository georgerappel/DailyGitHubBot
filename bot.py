#!/usr/bin/env python
# -*- coding:utf-8 -*-
from configparser import ConfigParser
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import re
import os
from apscheduler.schedulers.background import BackgroundScheduler
from GitApi import GitHub
from db_helper import DBHelper


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


# Connect and Setup the database
db = DBHelper(dbpath=PROJECT_DIR + '/db_bot.sqlite')
db.setup()


# Bot Configuration
config_file = ConfigParser()
config_file.read_file(open(PROJECT_DIR + '/config.ini'))


# Connecting the telegram API
# Updater will take the information and dispatcher connect the message to
# the bot
up = Updater(token=config_file['DEFAULT']['token'])
dispatcher = up.dispatcher


##########################################
#                                        #
#           COMMAND HANDLERS             #
#                                        #
##########################################
def start(bot, update):
    msg = "Hello, I'm {bot_name}. I can notify you of today's commits for any organization.\n"
    msg += "To learn how to use and setup automatic daily notifications, use /help.\n"

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(bot_name=bot.name))


def usage_help(bot, update):
    msg = ""
    msg += "This bot daily messages the commit count for your organization. You can also use "
    msg += "the /today <organization> when necessary.\n"
    msg += "To get started, setup your organization's username and the time for the notifications."
    msg += "\n\n"
    msg += "*Configuration*\n"
    msg += config_usage()
    msg += "\n"
    msg += "*On Demand*\n"
    msg += "/repos _organization_ - List repos for an organization (up to 30 most recent)\n"
    msg += "/today _organization_ - Count commits pushed today for an organization (up to 20 most recent)\n"
    msg += "\nThis bot is OpenSource and contributions are welcome [on GitHub]("
    msg += "https://github.com/georgerappel/DailyGitHubBot)."

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg,
                     disable_web_page_preview=True,
                     parse_mode=ParseMode.MARKDOWN)


# List the repositories of an Organization
def repos(bot, update, args):
    if len(args) < 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Please provide an organization username')
        return
    elif len(args) > 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Please provide only one valid username for the organization')
        return

    organization = args[0]
    gh = GitHub(config_file)

    bot.send_message(chat_id=update.message.chat_id,
                     text=gh.get_org_repos(organization),
                     parse_mode=ParseMode.MARKDOWN,
                     disable_web_page_preview=True)


# List commits made today by an organization
def today(bot, update, args):
    if len(args) < 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Please provide an organization username')
        return
    elif len(args) > 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Please provide only one valid username for the organization')
        return

    send_today_message(bot, update.message.chat_id, args[0])


# Prepares and sends the message with today's updates for an organization
def send_today_message(bot, chat_id, organization):
    gh = GitHub(config_file)

    bot.send_message(chat_id=chat_id,
                     text=gh.get_org_today(organization),
                     parse_mode=ParseMode.MARKDOWN,
                     disable_web_page_preview=True)


# Set or Read chat configurations
def update_config(bot, update, args):
    msg = ""
    if len(args) == 0:
        chat_config = db.get_config(update.message.chat_id)
        if chat_config is None:
            msg = "Use /help to learn how to setup the bot for this chat"
        else:
            msg = "Current configuration:\n\n"
            msg += chat_config.to_string()
    elif len(args) < 2 or len(args) > 2:
        msg = "The config command requires 2 parameters.\n"
        msg += config_usage()
    else:
        if args[0] == "time":
            match = re.match("([0-2]?[0-9])", args[1])
            if match is not None:
                hour = int(match.group(0))
                if hour > 23 or hour < 0:
                    msg = "Invalid hour.\n"
                    msg += config_usage()
                else:
                    msg = "Hour saved: " + match.group(0) + " o'clock.\n"
                    msg += get_time()
                    chat_config = db.set_config(update.message.chat_id, hour=int(match.group(1)))
                    msg += "\n\n*Current configurations*\n"
                    msg += chat_config.to_string()
            else:
                msg = "Invalid hour.\n"
                msg += config_usage()
        elif args[0] == "days":
            new_days = str(args[1]).lower()
            if new_days != "weekdays" and new_days != "daily":
                msg += "Invalid option for notification days. Use weekdays or daily."
            else:
                chat_config = db.set_config(update.message.chat_id, days=new_days)
                msg = "Notification days saved.\n\n*Current configurations*\n"
                msg += chat_config.to_string()

        elif args[0] == "org" or args[0] == "username":
            new_username = str(args[1])
            if new_username.startswith("@"):
                new_username = new_username[1:]
            chat_config = db.set_config(update.message.chat_id, username=new_username)
            msg = "Username saved.\n\n*Current configurations*\n"
            msg += chat_config.to_string()
        else:
            msg = "Invalid configuration key.\nUse /help for usage examples.\n"

    bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)


##########################################
#                                        #
#           HELPER FUNCTIONS             #
#                                        #
##########################################
# Usage guide for the /config command
def config_usage():
    usage = ""
    usage += "Usage:\n"
    usage += "  /config - shows current configuration\n"
    usage += "  /config org {username} \n"
    usage += "  /config time {0-23}\n"
    usage += "  /config days [weekdays/daily]\n"
    usage += "Examples:\n"
    usage += "  /config org myorg\n"
    usage += "  /config time 9\n"
    usage += "  /config time 17\n"
    usage += "  /config days weekdays\n"
    usage += "  /config days daily\n"
    usage += get_time() + "\n"
    return usage


def get_time():
    return "UTC Time(GMT+0): " + datetime.utcnow().strftime("%H:%M")


# noinspection PyUnusedLocal
def error_handler(bot, update, error):
    print("Error")


def scheduled_handler():
    chats = db.all_configs()
    for chat in chats:
        if chat.should_send_message():
            send_today_message(dispatcher.bot, chat.chat_id, chat.username)


# Add command handlers to dispatcher, those are functions to handle each command received from an user
dispatcher.add_error_handler(error_handler)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', usage_help))
dispatcher.add_handler(CommandHandler('today', today, pass_args=True))
dispatcher.add_handler(CommandHandler('config', update_config, pass_args=True))
dispatcher.add_handler(CommandHandler('repos', repos, pass_args=True))

# Start the bot with clean flag to ignore commands while it was offline
up.start_polling(clean=True)

# Scheduler to handle the notifications every hour
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_handler, 'cron', hour='*/1')
# scheduler.add_job(notification_handler, 'cron', minute='*/5')
scheduler.start()

print("Bot is up and running")
