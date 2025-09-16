from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import uuid

# دیتابیس ساده کاربران
users = {}  # user_id: {ref_code, inviter_id, balance, invites}

# ثبت‌نام با پرداخت فرضی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in users:
        await update.message.reply_text("✅ قبلاً ثبت‌نام کردی.\nلینک دعوت اختصاصی شما:\n" +
            f"https://t.me/{context.bot.username}?start={users[user_id]['ref_code']}")
        return

    # پرداخت فرضی ۲۰٬۰۰۰ تومان
    users[user_id] = {
        "ref_code": str(uuid.uuid4())[:8],
        "inviter_id": None,
        "balance": 0,
        "invites": 0
    }

    await update.message.reply_text(
        "🎉 ثبت‌نام موفق! لینک اختصاصی شما:\n" +
        f"https://t.me/{context.bot.username}?start={users[user_id]['ref_code']}"
    )

# بررسی لینک دعوت
async def referral_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if user_id in users:
        await update.message.reply_text("شما قبلاً ثبت‌نام کردید.")
        return

    inviter_id = None
    if args:
        ref_code = args[0]
        for uid, data in users.items():
            if data["ref_code"] == ref_code:
                inviter_id = uid
                break

    users[user_id] = {
        "ref_code": str(uuid.uuid4())[:8],
        "inviter_id": inviter_id,
        "balance": 0,
        "invites": 0
    }

    if inviter_id:
        users[inviter_id]["balance"] += 10000
        users[inviter_id]["invites"] += 1
        await update.message.reply_text("🎉 ثبت‌نام با لینک دعوت انجام شد!")
    else:
        await update.message.reply_text("🎉 ثبت‌نام انجام شد!")

    await update.message.reply_text(
        "لینک اختصاصی شما:\n" +
        f"https://t.me/{context.bot.username}?start={users[user_id]['ref_code']}"
    )

# نمایش موجودی و تعداد دعوت‌شده‌ها
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        await update.message.reply_text("❌ هنوز ثبت‌نام نکردی. اول /start رو بزن.")
        return

    data = users[user_id]
    await update.message.reply_text(
        f"👤 پروفایل شما:\n"
        f"موجودی هدیه: {data['balance']} تومان\n"
        f"تعداد دعوت‌شده‌ها: {data['invites']}\n"
        f"لینک اختصاصی:\nhttps://t.me/{context.bot.username}?start={data['ref_code']}"
    )

# اجرای ربات
def main():
    import os
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", referral_check))
    app.add_handler(CommandHandler("profile", profile))

    app.run_polling()

if __name__ == "__main__":
    main()
