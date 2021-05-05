import telebot
import src.config as cg
from src.model import *
from PIL import Image
import requests
import re
bot = telebot.TeleBot(cg.TOKEN)



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message,
                f"Hi, {message.from_user.first_name} {message.from_user.last_name},\nIt's me, <b>{bot.get_me().first_name}</b>. Try sending me a voice message or an audio file of at least 5 second length and i will guess the bird species. \n\nWorry not, I do not store your data and will delete all traces of your audiofile swiftly after processing. ",
                parse_mode='html'
                )


@bot.message_handler(func=lambda message: True, content_types=['text', 'voice', 'audio'])
def echo_all(message):
    if message.content_type=='voice':
        ebird_code, pic_url, sci_name, common_name =read_audio(message, bot)
        bot.reply_to(message,
                     f"Alright, {message.from_user.first_name}. Here's what your recording sounds to me\n\n\nSpecies name: {sci_name}\nCommon name: [{common_name}](http://en.wikipedia.org/wiki/{re.sub(' ', '_', sci_name)})\nDuration: **{message.voice.duration}** sec"
                     ,parse_mode='markdown')
        img = Image.open(requests.get(pic_url, stream=True).raw)
        bot.send_photo(message.chat.id, img)

    elif message.content_type=='audio':
        try:
            if message.audio.duration < 181: ## check for audio length
                ebird_code, pic_url, sci_name, common_name = read_audio(message, bot, message_type='audio')
                bot.reply_to(message,
                             f"Got your audio, {message.from_user.first_name}. Here's what it sounds to me\n\n\nSpecies name: {sci_name}\nCommon name: [{common_name}](http://en.wikipedia.org/wiki/{re.sub(' ', '_', sci_name)})\nDuration: **{message.audio.duration}** sec"
                             ,parse_mode='markdown')
                img = Image.open(requests.get(pic_url, stream=True).raw)
                bot.send_photo(message.chat.id, img)
            else:
                bot.reply_to(message,
                             f"Hey, {message.from_user.first_name}. I am sorry, but your audio file exceeds 3 minute limit. Please send me a shorter file"
                             , parse_mode='markdown')
        except:
            bot.reply_to(message,
                         f"Hey, {message.from_user.first_name}. I am sorry, but something went wrong and i cannot process your file for whatever reason. Hold on, i have already notified my maker."
                         , parse_mode='markdown')
            print('Input audio file issue')
    else:
        bot.reply_to(message,
                     "Thank you but I'd rather you sent me a voice recording or an audio file. Try again!")


bot.polling()