import telebot

bot = telebot.TeleBot("8055089822:AAHazUpCih0IH8a94hweLLvkn5GmmukegMw")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به ربات آگهی خوش اومدی 🌟")

bot.polling()
