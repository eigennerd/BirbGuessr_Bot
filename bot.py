import telebot
import src.config as cg
from src.model import *
import logging
from datetime import datetime
from PIL import Image
import requests
import re
import yaml
import base64
import random

random.seed(1)

#
# Settings
#

# init text
with open("src/narrator.yaml", 'r') as stream:
    try:
        text = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# init bot
bot = telebot.TeleBot(cg.TOKEN)
# init logging
logging.basicConfig(filename=f"data/logs.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger(__name__)

#
# Body
#

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    lang = message.from_user.language_code if message.from_user.language_code in ['en', 'ru', 'uk'] else 'en'
    bot.reply_to(message,
                f"""{text[lang]['hi']}, {message.from_user.first_name} {message.from_user.last_name},\n{text[lang]['its_me']}, <b>{bot.get_me().first_name}</b>. {text[lang]['shoot_me_a_msg']}""",
                parse_mode='html')
    logger.info(f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} said hi on {datetime.now()}")


@bot.message_handler(func=lambda message: True, content_types=['text', 'voice', 'audio', 'sticker', 'photo'])
def echo_all(message):
    lang = message.from_user.language_code if message.from_user.language_code in ['en', 'ru', 'uk'] else 'en'
    if message.content_type=='voice':
        try:
            if message.voice.duration < 5:  ## check for audio length
                bot.reply_to(message,
                             f"""{text[lang]['hey']}, {message.from_user.first_name}. {text[lang]['i_require_5s']}"""
                             , parse_mode='markdown')
                logger.warning(f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} sent an incomplete voice on {datetime.now()}")
            else:
                bird_proba, pic_url, sci_name, common_name =read_audio(message, bot)
                warning = '' if bird_proba>0.05 else text[lang]['interference']
                bot.reply_to(message,
                             f"{text[lang]['alright']}, {message.from_user.first_name}. {text[lang]['your_recording']}**{message.voice.duration}** {text[lang]['sec_long']}{warning}{text[lang]['species']}: {sci_name}\n{text[lang]['common_name']}: [{common_name}](http://{message.from_user.language_code}.wikipedia.org/wiki/{re.sub(' ', '_', sci_name)})"
                             ,parse_mode='markdown')
                logger.info(f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} sent a complete voice on {datetime.now()}. Top accuracy was: {bird_proba}. Bird guessed was: {sci_name}")
        except Exception as e:
            bot.reply_to(message,
                         f"{text[lang]['hey']}, {message.from_user.first_name}. {text[lang]['sorry_wrong']} "
                         , parse_mode='markdown')
            logger.error(
                f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} encountered a voice error on {datetime.now()}. Error message: {e}")
            print(f"message.voice issue: {e}")

    elif message.content_type=='audio': #TODO: optimize this, combine with 'voice' section
        try:
            if message.audio.duration < 5: ## check for audio length
                bot.reply_to(message,
                             f"{text[lang]['hey']}, {message.from_user.first_name}. {text[lang]['i_require_5s']}"
                             , parse_mode='markdown')
                logger.warning(f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} sent an incomplete audio on {datetime.now()}")
            elif message.audio.duration >180:
                bot.reply_to(message,
                             f"{text[lang]['hey']}, {message.from_user.first_name}. {text[lang]['long_audio']}"
                             , parse_mode='markdown')
                logger.warning(f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} sent a too large audio file on {datetime.now()}")
            else:
                bird_proba, pic_url, sci_name, common_name = read_audio(message, bot, message_type='audio')
                warning = '' if bird_proba > 0.05 else text[lang]['interference']
                bot.reply_to(message,
                             f"{text[lang]['got_audio']}, {message.from_user.first_name}. **{message.audio.duration}** {text[lang]['sec_long']}. {warning}{text[lang]['species']}: {sci_name}\n{text[lang]['common_name']}: [{common_name}](http://{message.from_user.language_code}.wikipedia.org/wiki/{re.sub(' ', '_', sci_name)})"
                             ,parse_mode='markdown')
                logger.info(
                    f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} sent a complete voice on {datetime.now()}. Top accuracy was: {bird_proba}")
        except Exception as e:
            bot.reply_to(message,
                         f"{text[lang]['hey']}, {message.from_user.first_name}. {text[lang]['sorry_wrong']}"
                         , parse_mode='markdown')
            logger.error(
                f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} encountered a voice error on {datetime.now()}. Error message: {e}")
            print(f"message.audio issue: {e}")
    else:
        bot.reply_to(message,
                     {text[lang]['try_again']})
        logger.warning(
            f"{base64.b64encode(' '.join(str(x) for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.id]).encode())} sent gibberish on {datetime.now()}.")


bot.infinity_polling(timeout=10, long_polling_timeout = 5)
