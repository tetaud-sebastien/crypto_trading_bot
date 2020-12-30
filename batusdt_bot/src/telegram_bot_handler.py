#!interpreter
# -*- coding: utf-8 -*-
# Sebastien tetaud 2020-11-28

from telegram.ext import CommandHandler, CallbackQueryHandler, Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from function import telegram_send_message
import config
import json


print("Start Telegram Bot")


# Telegram
telegram_token = config.TELEGRAM_TOKEN
telegram_chat_id = config.TELEGRAM_CHAT_ID

############################### Bot ############################################
def start(update, context):
    update.message.reply_text(main_menu_message(),
                            reply_markup=main_menu_keyboard())

def main_menu(update,context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                        text=main_menu_message(),
                        reply_markup=main_menu_keyboard())
    
def first_menu(update,context):

    query = update.callback_query
    status = {"status":query.data}
    with open('src/bot_status.json', 'w') as json_file:
        json.dump(status, json_file)
    message = "Bot " + query.data
    telegram_send_message(message, telegram_chat_id, telegram_token)
    print(query.data)

############################ Keyboards #########################################
def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('/start', callback_data='start')],
              [InlineKeyboardButton('/stop', callback_data='stop')]]
    return InlineKeyboardMarkup(keyboard)

def main():

    updater = Updater(telegram_token, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('menu', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
    updater.dispatcher.add_handler(CallbackQueryHandler(first_menu, pattern='start'))
    updater.dispatcher.add_handler(CallbackQueryHandler(first_menu, pattern='stop'))
    updater.start_polling()

############################# Messages #########################################
def main_menu_message():
    return 'BAT USDT Bot Options'

############################# Handlers #########################################
if __name__ == '__main__':
    main()
