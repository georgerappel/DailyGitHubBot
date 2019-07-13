#!/usr/bin/env python
# -*- coding:utf-8 -*-

from configparser import ConfigParser
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import re
from apscheduler.schedulers.background import BackgroundScheduler

from GitApi import GitHub
from dbhelper import DBHelper

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


##########################################
#                                        #
#           COMMAND HANDLERS             #
#                                        #
##########################################
def start(bot, update):
    msg = "Hello, I'm {bot_name}. \n"
    msg += "To learn how to use the bot and start using the automatic daily notifications, check the /help command.\n"

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(bot_name=bot.name))


def help(bot, update):
    msg = ""
    msg += "This bot will message the current chat everyday or on weekdays with the "
    msg += "daily commit count for your organization. To get started, configure your"
    msg += " organization's username and the time you want to receive the notifications.\n\n"
    msg += "= Configuration =\n"
    msg += config_usage()
    msg += "\n"
    msg += "= Use on demand =\n"
    msg += "/org + organization - List an organization's repositories \n"
    msg += "/today + organization - List today's commits for an organization\n"
    msg += "Ex: /org devmobufrj | /today devmobufrj\n"
    msg += "\nThis bot is OpenSource and contributions are welcome at "
    msg += "https://github.com/georgerappel/DailyGitHubBot\n"

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg)


# List the repositories of an Organization
def org(bot, update, args):
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


# List commits made today by an organization
def today(bot, update, args):
    if len(args) < 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Please provide an organization name')
        return
    elif len(args) > 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Please provide only one valid username for the organization')
        return

    send_today_message(bot, update.message.chat_id, args[0])


# Set or Read chat configurations
def config(bot, update, args):
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
            match = re.match("([0-2]{0,1}[0-9])", args[1])
            if match is not None:
                hour = int(match.group(0))
                if hour > 23 or hour < 0:
                    msg = "Invalid hour.\n"
                    msg += config_usage()
                else:
                    msg = "Hour saved: " + match.group(0) + " o'clock.\n"
                    msg += get_time()
                    config = db.set_config(update.message.chat_id, hour=int(match.group(1)))
                    msg += "\n\n*Current configurations*\n"
                    msg += config.to_string()
            else:
                msg = "Invalid hour.\n"
                msg += config_usage()
        elif args[0] == "days":
            new_days = str(args[1]).lower()
            if new_days != "weekdays" and new_days != "daily":
                msg += "Invalid option for notification days. Use weekdays or daily."
            else:
                config = db.set_config(update.message.chat_id, days=new_days)
                msg = "Notification days saved.\n\n*Current configurations*\n"
                msg += config.to_string()

        elif args[0] == "org" or args[0] == "username":
            new_username = str(args[1])
            if new_username.startswith("@"):
                new_username = new_username[1:]
            config = db.set_config(update.message.chat_id, username=new_username)
            msg = "Username saved.\n\n*Current configurations*\n"
            msg += config.to_string()
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
    usage += "  /config org DevMobUFRJ\n"
    usage += "  /config time 9\n"
    usage += "  /config time 17\n"
    usage += "  /config days weekdays\n"
    usage += "  /config days daily\n"
    usage += get_time() + "\n"
    return usage


def get_time():
    return "UTC Time(GMT+0): " + datetime.utcnow().strftime("%H:%M")


def error_handler(bot, update, error):
    print("Error handled: ")
    print(error)


# Prepares and sends the message with today's updates for an organization
def send_today_message(bot, chat_id, organization):
    gh = GitHub()
    bot.send_message(chat_id=chat_id,
                     text='{0} Listing today\'s updates for '
                     .format('\U0001F5C4') +
                          '[{0}](https://github.com/{0}) >>'.format(
                              organization),
                     parse_mode=ParseMode.MARKDOWN)

    bot.send_message(chat_id=chat_id,
                     text=gh.get_org_today(organization))


def scheduled_handler():
    chats = db.all_configs()
    for chat in chats:
        if chat.valid() and chat.hour == datetime.utcnow().hour:  # TODO Considerar weekdays ou daily.
            send_today_message(dispatcher.bot, chat.chat_id, chat.username)


# Add command handlers to dispatcher
dispatcher.add_error_handler(error_handler)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('today', today, pass_args=True))
dispatcher.add_handler(CommandHandler('config', config, pass_args=True))
dispatcher.add_handler(CommandHandler('org', org, pass_args=True))

# Start the bot with clean flag to ignore commands while it was offline
up.start_polling(clean=True)

# Scheduler to handle the notifications every hour
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_handler, 'cron', hour='*/1')
# scheduler.add_job(notification_handler, 'cron', minute='*/5')
scheduler.start()

print("Bot is up and running (probably)")
