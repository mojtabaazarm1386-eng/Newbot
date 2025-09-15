import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

# مراحل گفتگو
(
    ASK_MODEL, ASK_COLOR, ASK_SIZE, ASK_GENDER,
    ASK_NAME, ASK_PHONE, ASK_ADDRESS
) = range(7)

# مدل‌ها و رنگ‌ها
models = ["کفش اسپرت ۱", "کفش اسپرت ۲", "کفش رسمی ۱", "کفش رسمی ۲", "کفش پیاده‌روی", "کفش ورزشی"]
colors = ["سفید", "آبی", "سبز"]
sizes = [str(i) for i in range(36, 46)]
genders = ["خانم", "آقا"]

# شروع سفارش
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([models], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("مدل کفش مورد نظر را انتخاب کنید:", reply_markup=reply_markup)
    return ASK_MODEL

# انتخاب مدل
async def ask_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["model"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([colors], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("رنگ کفش را انتخاب کنید:", reply_markup=reply_markup)
    return ASK_COLOR

# انتخاب رنگ
async def ask_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["color"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([sizes[i:i+5] for i in range(0, len(sizes), 5)], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("سایز کفش را انتخاب کنید:", reply_markup=reply_markup)
    return ASK_SIZE

# انتخاب جنسیت
async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["size"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([genders], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("جنسیت را انتخاب کنید:", reply_markup=reply_markup)
    return ASK_GENDER

# دریافت نام
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text("نام و نام خانوادگی را وارد کنید:")
    return ASK_NAME

# دریافت شماره
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("شماره تلفن را وارد کنید:")
    return ASK_PHONE

# دریافت آدرس و نمایش سفارش
async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("آدرس کامل را وارد کنید:")
    return ASK_ADDRESS

# پایان سفارش
async def finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    data = context.user_data

    await update.message.reply_text(
        f"✅ سفارش ثبت شد:\n"
        f"مدل کفش: {data['model']}\n"
        f"رنگ: {data['color']}\n"
        f"سایز: {data['size']}\n"
        f"جنسیت: {data['gender']}\n"
        f"نام: {data['name']}\n"
        f"شماره تلفن: {data['phone']}\n"
        f"آدرس: {data['address']}"
    )
    return ConversationHandler.END

# لغو سفارش
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سفارش لغو شد ❌")
    return ConversationHandler.END

# اجرای ربات
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # دریافت توکن از محیط امن
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("order", start_order)],
        states={
            ASK_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_color)],
            ASK_COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_size)],
            ASK_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
            ASK_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
