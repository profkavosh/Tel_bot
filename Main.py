
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8055089822:AAHazUpCih0IH8a94hweLLvkn5GmmukegMw")
GROUP_ID = int(os.getenv("GROUP_ID"))  # مثلاً -1001234567890

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام! دوست عزیز، فقط نام محصولت رو بنویس تا برات آگهی ثبت کنم."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    product_name = update.message.text.strip()
    if not product_name:
        return  # حذف پیام خالی

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🛒 فروش", url=f"https://t.me/{context.bot.username}")
    ]])

    text = f"📢 آگهی جدید توسط <b>{user.first_name}</b>:\n\n🛍️ <b>{product_name}</b>"
    await context.bot.send_message(chat_id=GROUP_ID, text=text,
                                   parse_mode="HTML", reply_markup=keyboard)
    await update.message.reply_text("✅ آگهی ثبت شد و در گروه منتشر شد. ممنون از همراهیت ♥️")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
