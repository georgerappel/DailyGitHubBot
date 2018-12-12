#!/usr/bin/env python
# -*- coding:utf-8 -*-

from sys import path
from configparser import ConfigParser
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from GitApi import GitHub

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



# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('today', today, pass_args=True))
dispatcher.add_handler(CommandHandler('org', org, pass_args=True))

# Start the program
up.start_polling()
