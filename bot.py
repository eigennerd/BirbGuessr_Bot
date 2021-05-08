import telebot
import src.config as cg
from src.model import *
import logging
from datetime import datetime
from PIL import Image
import requests
import re
bot = telebot.TeleBot(cg.TOKEN)

logging.basicConfig(filename=f"data/logs.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
                f"Hi, {message.from_user.first_name} {message.from_user.last_name},\nIt's me, <b>{bot.get_me().first_name}</b>. Try sending me a voice message or an audio file of at least 5 second length and i will guess the bird species. \n\nWorry not, I do not store your data and will delete all traces of your audiofile swiftly after processing. ",
                parse_mode='html')
    logger.info(f"{hash(message.from_user)} said hi on {datetime.now()}")


@bot.message_handler(func=lambda message: True, content_types=['text', 'voice', 'audio', 'sticker', 'photo'])
def echo_all(message):
    if message.content_type=='voice':
        try:
            if message.voice.duration < 5:  ## check for audio length
                bot.reply_to(message,
                             f"Hey, {message.from_user.first_name}. I need a sample larger than 5 seconds, could you send me another one?"
                             , parse_mode='markdown')
                logger.warning(f"{hash(message.from_user)} sent an incomplete voice on {datetime.now()}")
            else:
                bird_proba, pic_url, sci_name, common_name =read_audio(message, bot)
                warning = '' if bird_proba>0.05 else '\nInterference detected: noise or other non-bird patterns may decrease the accuracy of bird detection. \n'
                bot.reply_to(message,
                             f"Alright, {message.from_user.first_name}. Your recording is **{message.voice.duration}** sec long. {warning}Here's what it sounds to me\n\n\nSpecies: {sci_name}\nCommon name: [{common_name}](http://en.wikipedia.org/wiki/{re.sub(' ', '_', sci_name)})"
                             ,parse_mode='markdown')
                logger.info(f"{hash(message.from_user)} sent a complete voice on {datetime.now()}. Top accuracy was: {bird_proba}")
        except Exception as e:
            bot.reply_to(message,
                         f"Hey, {message.from_user.first_name}. I am sorry, but something went wrong and i cannot process your recording for whatever reason. My maker has been notified \n "
                         , parse_mode='markdown')
            logger.error(
                f"{hash(message.from_user)} encountered a voice error on {datetime.now()}. Error message: {e}")
            print(f"message.voice issue: {e}")

    elif message.content_type=='audio': #TODO: optimize this, combine with 'voice' section
        try:
            if message.audio.duration < 5: ## check for audio length
                bot.reply_to(message,
                             f"Hey, {message.from_user.first_name}. I need a sample larger than 5 seconds, could you send me another one?"
                             , parse_mode='markdown')
                logger.warning(f"{hash(message.from_user)} sent an incomplete audio on {datetime.now()}")
            elif message.audio.duration >180:
                bot.reply_to(message,
                             f"Hey, {message.from_user.first_name}. I am sorry, but your audio file exceeds 3 minute limit. Please send me a shorter file"
                             , parse_mode='markdown')
                logger.warning(f"{hash(message.from_user)} sent a too large audio file on {datetime.now()}")
            else:
                bird_proba, pic_url, sci_name, common_name = read_audio(message, bot, message_type='audio')
                warning = '' if bird_proba > 0.05 else '\nInterference detected: noise or other non-bird patterns may decrease the accuracy of bird detection. \n'
                bot.reply_to(message,
                             f"Got your audio, {message.from_user.first_name}. It is **{message.audio.duration}** sec long. {warning}Here's what it sounds to me\n\n\nSpecies: {sci_name}\nCommon name: [{common_name}](http://en.wikipedia.org/wiki/{re.sub(' ', '_', sci_name)})"
                             ,parse_mode='markdown')
                logger.info(
                    f"{hash(message.from_user)} sent a complete voice on {datetime.now()}. Top accuracy was: {bird_proba}")
        except Exception as e:
            bot.reply_to(message,
                         f"Hey, {message.from_user.first_name}. I am sorry, but something went wrong and i cannot process your file for whatever reason. My maker has been notified. \n "
                         , parse_mode='markdown')
            logger.error(
                f"{hash(message.from_user)} encountered a voice error on {datetime.now()}. Error message: {e}")
            print(f"message.audio issue: {e}")
    else:
        bot.reply_to(message,
                     "Thank you but I'd rather you sent me a voice recording or an audio file. Try again!")
        logger.warning(
            f"{hash(message.from_user)} sent gibberish on {datetime.now()}.")


bot.polling()