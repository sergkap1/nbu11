#!/usr/bin/python
#coding:utf-8

import telebot
from telebot import types
import requests
import json
from collections import namedtuple
import os
from flask import Flask, request
import logging

TOKEN = "TOKEN"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json'

bot = telebot.TeleBot(TOKEN)

def nbu(message):
    #bot.send_message(message.chat.id, "Привіт, я Telegram бот ddd")
    response = requests.get(url)
    resp = response.json()
    data=json.dumps(resp, sort_keys=True, indent=4)
    x = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    i=1
    while i<len(x):
        if x[i].cc.lower()==message.lower():
            stroka=x[i].exchangedate + ' : 1 ' +x[i].txt + ' - ' + str(x[i].rate) + ' Українська гривня'
            #bot.send_message(message.chat.id, stroka)
            #print (x[i].txt)
            break
        else: i=i+1
    if i==len(x):
        stroka='Такої валюти немає'
        #bot.send_message(message.chat.id, 'Такої валюти немає')
    return stroka

def inline_key(num):
    """Функция для вывода кнопок
    """
    i=1
    btns = []
    while i<=num:
        btns.append(types.InlineKeyboardButton(text='Кнопка '+str(i+10), callback_data='butt'+str(i+10)))
        i=i+1
    btns.append(types.InlineKeyboardButton(text='назад', callback_data='nazad'))
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*btns)
    return keyboard

@bot.callback_query_handler(func=lambda call: True)
def inline(c):

    if c.data=='usd':
        bot.send_message(c.message.chat.id, nbu('usd'))        
##    elif c.data=='usd':
##        bot.edit_message_text(
##            chat_id=c.message.chat.id,
##            message_id=c.message.message_id,
##            text="нажата *кнопка 1*",
##            parse_mode="markdown")
    elif c.data=='eur':
        bot.send_message(c.message.chat.id, nbu('eur'))
    elif c.data=='gbp':
        bot.send_message(c.message.chat.id, nbu('gbp'))
    elif c.data=='all':
        response = requests.get(url)
        resp = response.json()
        data=json.dumps(resp, sort_keys=True, indent=4)
        x = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        i=1
        while i<len(x):
            stroka=x[i].exchangedate + ' : 1 ' +x[i].txt + ' - ' + str(x[i].rate) + ' Українська гривня' + ' ('+x[i].cc+')'
            bot.send_message(c.message.chat.id, stroka)
            i=i+1

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привіт, я Telegram бот")
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    button_usd = types.KeyboardButton(text="Долар США")
    button_eur = types.KeyboardButton(text="Євро")
    button_3 = types.KeyboardButton(text="Фунт стерлінгів")
    button_4 = types.KeyboardButton(text="Всі валюти")
    keyboard.add(button_usd, button_eur, button_3, button_4)
    bot.send_message(message.chat.id, "Виберіть або напишіть код", reply_markup=keyboard)
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Долар США",callback_data="usd")
    but_2 = types.InlineKeyboardButton(text="Євро",callback_data="eur")
    but_3 = types.InlineKeyboardButton(text="Фунт стерлінгів",callback_data="gbp")
    but_4 = types.InlineKeyboardButton(text="Всі валюти", callback_data="all")
    key.add(but_1, but_2, but_3, but_4)
    bot.send_message(message.chat.id, "Виберіть або напишіть код", reply_markup=key)
    #key = types.InlineKeyboardMarkup()
    #key.add(types.InlineKeyboardButton(text='кнопка1', callback_data="butt1"))
    #key.add(types.InlineKeyboardButton(text='кнопка2', callback_data="butt2"))  
    #msg=bot.send_message(message.chat.id, 'Нажми кнопку', reply_markup=key)
    #logging.info(message.chat.id)    
    #bot.send_message(message.chat.id, "Введіть позначення валюти, а я покажу поточний курс НБУ")

@bot.message_handler(content_types=["text"])
def nbu_text(message):
    cc=message.text
    if message.text=="Долар США":
        cc="usd"
    elif message.text=="Євро":
        cc="eur"
    elif message.text=="Фунт стерлінгів":
        cc="gbp"
    elif message.text=="Всі валюти":
        cc="all"
    bot.send_message(message.chat.id, nbu(cc))

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://nbu11.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


##if __name__ == "__main__":
##    updater = Updater(TOKEN)
##    # add handlers
##    updater.start_webhook(listen="0.0.0.0",
##                      port=PORT,
##                      url_path=TOKEN)
##    updater.bot.set_webhook("https://<appname>.herokuapp.com/" + TOKEN)
##    updater.idle()
##    #bot.polling()
