import telebot
from telebot import types
import requests
import re

TOKEN = "8055089822:AAHazUpCih0IH8a94hweLLvkn5GmmukegMw"
ADMIN_ID = 1799531729
OWNER_ID = ADMIN_ID
WALLET_ADDRESS = "0x4f670F80357ffC51Cb49D04fe55AA52BaF102c47"
user_data = {}
seller_paid = set()

SUPPORTED_TOKENS = {
    "USDT": "tether",
    "ETH": "ethereum",
    "DEGEN": "degen-base",
    "JWB21": "jamesweb",
    "BBC": "basebitcoin"
}

bot = telebot.TeleBot(TOKEN)

products = {
    "🍅 گوجه محلی": {"price": 50000, "unit": "کیلو"},
    "🥒 خیار محلی": {"price": 30000, "unit": "کیلو"},
    "🥚 تخم‌مرغ محلی": {"price": 10000, "unit": "عدد"},
    "🤖بات تلگرامی": {"price": 5000000, "unit": "پکیج"},
}

def convert_fa_numbers(text):
    fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    return text.translate(fa_to_en)

def get_token_price(symbol):
    try:
        api_id = SUPPORTED_TOKENS[symbol.upper()]
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={api_id}&vs_currencies=usd"
        r = requests.get(url).json()
        return float(r[api_id]['usd'])
    except:
        return None

def verify_transaction(tx_hash):
    url = f"https://api.basescan.org/api?module=transaction&action=gettxreceiptstatus&txhash={tx_hash}&apikey=YourApiKey"
    r = requests.get(url).json()
    return r.get("result", {}).get("status") == "1"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌾 خوش آمدی به فروشگاه هوشمند !")
    for name, info in products.items():
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🛒 خرید", callback_data=f"buy_{name}"))
        msg = f"{name}\nقیمت: {info['price']} تومان ({info['unit']})"
        bot.send_message(message.chat.id, msg, reply_markup=kb)

    kb2 = types.InlineKeyboardMarkup()
    kb2.add(types.InlineKeyboardButton("➕ ثبت آگهی فروشنده", callback_data="seller_add"))
    bot.send_message(message.chat.id, "اگر فروشنده‌ای، روی دکمه زیر بزن:", reply_markup=kb2)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    pname = call.data[4:]
    user_data[call.from_user.id] = {"product": pname}
    bot.send_message(call.message.chat.id, f"چه تعداد «{pname}» می‌خواهید؟")
    bot.register_next_step_handler(call.message, get_quantity)

def get_quantity(message):
    try:
        qty = float(convert_fa_numbers(message.text))
        user_data[message.chat.id]["quantity"] = qty
        bot.send_message(message.chat.id, "📞 شماره تماس رو بفرست:")
        bot.register_next_step_handler(message, get_phone)
    except:
        bot.send_message(message.chat.id, "❗ عدد معتبر وارد کن")
        bot.register_next_step_handler(message, get_quantity)

def get_phone(message):
    user_data[message.chat.id]["phone"] = message.text
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💳 کارت به کارت", callback_data="pay_card"))
    kb.add(types.InlineKeyboardButton("🪙 پرداخت رمزارز", callback_data="pay_crypto"))
    bot.send_message(message.chat.id, "روش پرداخت رو انتخاب کن:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data in ["pay_card", "pay_crypto"])
def handle_payment(call):
    data = user_data.get(call.message.chat.id)
    if not data:
        return bot.send_message(call.message.chat.id, "❌ مشکلی پیش اومده")

    pname = data['product']
    qty = data['quantity']
    price = products[pname]['price']
    total = int(qty * price)

    if call.data == "pay_card":
        msg = f"""💳 پرداخت کارت به کارت:

محصول: {pname}
تعداد: {qty}
قیمت کل: {total:,} تومان

شماره کارت:
 6037-6975-2262-1199
به نام: کاوش نجدی

📸 لطفاً عکس رسید رو بفرست."""
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, receive_receipt)
    else:
        usdt = get_token_price("USDT")
        if not usdt:
            return bot.send_message(call.message.chat.id, "❌ خطا در دریافت قیمت لحظه‌ای")
        usdt_amount = round(total / (usdt * 90000), 2)  # تبدیل تومان به USDT با فرض 90K
        msg = f"""🪙 پرداخت رمزارز:

محصول: {pname}
تعداد: {qty}
مبلغ کل: {total:,} تومان
مبلغ معادل تقریبی: {usdt_amount} USDT

آدرس کیف پول:
{WALLET_ADDRESS}

📤 لطفاً هش تراکنش رو بفرست:"""
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, receive_tx_hash)

def receive_receipt(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❗ لطفاً فقط عکس بفرست")
        bot.register_next_step_handler(message, receive_receipt)
        return
    file_id = message.photo[-1].file_id
    caption = "🧾 رسید پرداخت جدید"
    bot.send_photo(ADMIN_ID, file_id, caption=caption)
    bot.send_message(message.chat.id, "✅ رسید دریافت شد. در حال بررسی سفارش شما هستیم.")

def receive_tx_hash(message):
    tx_hash = message.text.strip()
    if verify_transaction(tx_hash):
        bot.send_message(message.chat.id, "✅ تراکنش تأیید شد. سفارشت ثبت شد.")
    else:
        bot.send_message(message.chat.id, "❌ تراکنش معتبر نیست. دوباره بررسی کن.")

@bot.callback_query_handler(func=lambda call: call.data == "seller_add")
def seller_register(call):
    user_id = call.from_user.id
    if user_id not in seller_paid:
        bot.send_message(call.message.chat.id, "💰 برای ثبت آگهی باید 1 USDT بپردازی. برای اولین بار 70٪ تخفیف داری یعنی فقط 0.3 USDT!")

        msg = f"""🧾 پرداخت برای ثبت آگهی:

آدرس کیف پول:
{WALLET_ADDRESS}

بعد از پرداخت، هش تراکنش رو بفرست:"""
        bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(call.message, verify_seller_payment)
    else:
        bot.send_message(call.message.chat.id, "✏️ عنوان محصولی که می‌خوای آگهی کنی رو بنویس:")

def verify_seller_payment(message):
    tx_hash = message.text.strip()
    if verify_transaction(tx_hash):
        seller_paid.add(message.chat.id)
        bot.send_message(message.chat.id, "✅ پرداخت تأیید شد. عنوان محصول رو بنویس:")
        bot.register_next_step_handler(message, get_seller_product)
    else:
        bot.send_message(message.chat.id, "❌ تراکنش نامعتبره. دوباره تلاش کن.")

def get_seller_product(message):
    pname = message.text
    bot.send_message(ADMIN_ID, f"🛎️ فروشنده جدید محصول ثبت کرد:\n{pname}")
    bot.send_message(message.chat.id, "✅ محصول شما ثبت شد. پس از تأیید نمایش داده خواهد شد.")

bot.infinity_polling()
