import telebot

bot = telebot.TeleBot("توکن_ربات_تو_اینجا")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به ربات آگهی خوش اومدی 🌟")

bot.polling()
