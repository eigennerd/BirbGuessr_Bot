import telebot
import config as cg

bot = telebot.TeleBot(cg.TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message,
                f"Hi, {message.from_user.first_name} {message.from_user.last_name},\nIt's me, <b>{bot.get_me().first_name}</b>. Try sending me a voice message or an audio file. Soon i will be able to tell a bird from that noise that surrounds you.",
                parse_mode='html'
                )

@bot.message_handler(func=lambda message: True, content_types=['text', 'voice', 'audio'])
def echo_all(message):
    if message.content_type=='voice':
        bot.reply_to(message,
                     f"Wow, thanks for sending me your beautiful voice sample. Although i cannot do much with it just yet - but my developer is planning to serve a real bird recognition model right here. \n\nAnyway, I will be happy to wake up tomorrow with realization that someone believes in me!\n\nThis is what your recording looks like from my side:\nDuration: <b>{message.voice.duration}</b> sec\nSent by: <b>{message.from_user.last_name}</b>"
                     ,parse_mode='html')
    elif message.content_type=='audio':
        bot.reply_to(message,
                     f"Splendid! Thank you for sending me this audio sample. I cant do much with it just yet!\n\nBut i can tell your file looks like from my side:\nDuration: {message.audio.duration} sec"
                     ,parse_mode='html')
    else:
        bot.reply_to(message,
                     "Thank you but I'd rather you sent me a voice recording or an audio file. Try again!")


bot.polling()