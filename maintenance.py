import telebot
import src.config as cg

bot = telebot.TeleBot(cg.TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message,
                f"Hi, {message.from_user.first_name} {message.from_user.last_name},\nThis is <b>{bot.get_me().first_name}</b>. Currently our developers are working relentlessy to make me work again. Try reaching out to me later.",
                parse_mode='html'
                )


@bot.message_handler(func=lambda message: True, content_types=['text', 'voice', 'audio'])
def echo_all(message):
        bot.reply_to(message,
                     "Thank you but currently we are under maintenance. Come again later!")


bot.polling()