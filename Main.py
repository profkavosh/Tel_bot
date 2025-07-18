import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# مراحل گفتگو
PRODUCT_NAME, PRODUCT_PHOTO, PRODUCT_PRICE, CONTACT_INFO, ACCOUNT_NUMBER, FREE_SHIPPING = range(6)

# کانفیگ لاگ‌ها
logging.basicConfig(level=logging.INFO)

# آی‌دی گروهی که آگهی‌ها باید به آن ارسال شوند
TARGET_GROUP_ID = -1002045444046  # جایگزین با آیدی گروه خودت

# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋\nبرای ثبت آگهی لطفاً نام محصول را وارد کنید:")
    return PRODUCT_NAME

# مرحله ۱: نام محصول
async def product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("عکس محصول را بفرستید:")
    return PRODUCT_PHOTO

# مرحله ۲: عکس
async def product_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    context.user_data['photo'] = photo.file_id
    await update.message.reply_text("قیمت محصول را وارد کنید:")
    return PRODUCT_PRICE

# مرحله ۳: قیمت
async def product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    await update.message.reply_text("اطلاعات تماس (مثلاً شماره یا آیدی) را وارد کنید:")
    return CONTACT_INFO

# مرحله ۴: تماس
async def contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact'] = update.message.text
    await update.message.reply_text("شماره کارت یا حساب برای پرداخت را وارد کنید:")
    return ACCOUNT_NUMBER

# مرحله ۵: شماره کارت
async def account_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['account'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("✅ بله", callback_data="yes")],
        [InlineKeyboardButton("❌ خیر", callback_data="no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("آیا ارسال رایگان دارید؟", reply_markup=reply_markup)
    return FREE_SHIPPING

# مرحله ۶: ارسال رایگان؟
async def free_shipping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['shipping'] = "دارد" if query.data == "yes" else "ندارد"

    user = query.from_user
    data = context.user_data

    caption = (
        f"🛍️ *{data['name']}*\n"
        f"💰 قیمت: {data['price']}\n"
        f"📞 تماس: {data['contact']}\n"
        f"💳 شماره حساب: {data['account']}\n"
        f"🚚 ارسال رایگان: {data['shipping']}\n"
        f"👤 ارسال‌کننده: @{user.username if user.username else user.first_name}"
    )

    await context.bot.send_photo(
        chat_id=TARGET_GROUP_ID,
        photo=data['photo'],
        caption=caption,
        parse_mode="Markdown"
    )

    await query.edit_message_text("✅ آگهی با موفقیت ارسال شد!")
    return ConversationHandler.END

# لغو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرآیند ثبت آگهی لغو شد.")
    return ConversationHandler.END

# اجرای برنامه
if __name__ == '__main__':
    import os
    TOKEN = os.getenv("BOT_TOKEN")  # توکن رو از Secret ها می‌خونه

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_name)],
            PRODUCT_PHOTO: [MessageHandler(filters.PHOTO, product_photo)],
            PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_price)],
            CONTACT_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_info)],
            ACCOUNT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, account_number)],
            FREE_SHIPPING: [CallbackQueryHandler(free_shipping)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
