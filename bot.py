from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import os

# مراحل گفتگو
ASK_INGREDIENTS, SHOW_OPTIONS = range(2)

# دیتابیس غذاها (۱۵ غذای ایرانی)
recipes = [
    {
        "name": "املت گوجه",
        "ingredients": ["تخم‌مرغ", "گوجه", "روغن", "نمک"],
        "substitutes": {"گوجه": ["رب", "گوجه‌فرنگی له‌شده"]},
        "instructions": "تخم‌مرغ‌ها رو با گوجه‌های خردشده در روغن سرخ کن. نمک بزن و هم بزن تا ببنده.",
        "calories": "۲۵۰ کیلوکالری"
    },
    {
        "name": "عدس‌پلو",
        "ingredients": ["عدس", "برنج", "روغن", "پیاز", "نمک"],
        "substitutes": {"پیاز": ["پودر پیاز", "سیر"]},
        "instructions": "عدس رو بپز، با برنج و پیاز داغ مخلوط کن و دم کن.",
        "calories": "۴۰۰ کیلوکالری"
    },
    {
        "name": "ماکارونی با سس قرمز",
        "ingredients": ["ماکارونی", "رب", "پیاز", "روغن", "نمک"],
        "substitutes": {"رب": ["گوجه له‌شده"], "پیاز": ["پودر پیاز", "سیر"]},
        "instructions": "پیاز رو سرخ کن، رب اضافه کن، سس رو با ماکارونی مخلوط کن و بپز.",
        "calories": "۵۰۰ کیلوکالری"
    },
    {
        "name": "کوکو سبزی",
        "ingredients": ["سبزی", "تخم‌مرغ", "روغن", "نمک", "زردچوبه"],
        "substitutes": {"سبزی": ["سبزی خشک"], "زردچوبه": ["ادویه کاری"]},
        "instructions": "سبزی‌ها رو با تخم‌مرغ و ادویه مخلوط کن، در روغن سرخ کن تا طلایی بشه.",
        "calories": "۳۰۰ کیلوکالری"
    },
    {
        "name": "خوراک لوبیا",
        "ingredients": ["لوبیا", "پیاز", "روغن", "رب", "نمک"],
        "substitutes": {"پیاز": ["سیر"], "رب": ["گوجه له‌شده"]},
        "instructions": "لوبیا رو بپز، با پیاز داغ و رب مخلوط کن و بذار جا بیفته.",
        "calories": "۳۵۰ کیلوکالری"
    },
    {
        "name": "کتلت گوشت",
        "ingredients": ["گوشت چرخ‌کرده", "سیب‌زمینی", "تخم‌مرغ", "پیاز", "نمک"],
        "substitutes": {"پیاز": ["پودر پیاز"], "گوشت": ["سویا"]},
        "instructions": "همه مواد رو مخلوط کن، شکل بده و در روغن سرخ کن.",
        "calories": "۵۵۰ کیلوکالری"
    },
    {
        "name": "آش رشته",
        "ingredients": ["رشته", "سبزی آش", "لوبیا", "عدس", "کشک"],
        "substitutes": {"کشک": ["ماست غلیظ"], "سبزی": ["سبزی خشک"]},
        "instructions": "حبوبات رو بپز، سبزی و رشته اضافه کن، کشک رو آخر بریز.",
        "calories": "۴۵۰ کیلوکالری"
    },
    {
        "name": "خورشت قیمه",
        "ingredients": ["گوشت", "لپه", "رب", "پیاز", "سیب‌زمینی"],
        "substitutes": {"گوشت": ["سویا"], "رب": ["گوجه له‌شده"]},
        "instructions": "گوشت و لپه رو با پیاز و رب بپز، سیب‌زمینی رو جدا سرخ کن.",
        "calories": "۶۰۰ کیلوکالری"
    },
    {
        "name": "خورشت سبزی",
        "ingredients": ["سبزی", "گوشت", "لوبیا", "پیاز", "روغن"],
        "substitutes": {"گوشت": ["سویا"], "سبزی": ["سبزی خشک"]},
        "instructions": "سبزی رو سرخ کن، با گوشت و لوبیا بپز تا جا بیفته.",
        "calories": "۵۵۰ کیلوکالری"
    },
    {
        "name": "مرغ شکم‌پر",
        "ingredients": ["مرغ", "سبزی", "برنج", "پیاز", "ادویه"],
        "substitutes": {"سبزی": ["سبزی خشک"], "ادویه": ["زردچوبه"]},
        "instructions": "داخل مرغ رو با مواد پر کن، در فر یا قابلمه بپز.",
        "calories": "۶۵۰ کیلوکالری"
    },
    {
        "name": "لوبیاپلو",
        "ingredients": ["لوبیا سبز", "برنج", "گوشت", "پیاز", "روغن"],
        "substitutes": {"گوشت": ["سویا"], "پیاز": ["پودر پیاز"]},
        "instructions": "لوبیا و گوشت رو بپز، با برنج مخلوط کن و دم کن.",
        "calories": "۵۰۰ کیلوکالری"
    },
    {
        "name": "خوراک بادمجان",
        "ingredients": ["بادمجان", "گوجه", "پیاز", "روغن", "نمک"],
        "substitutes": {"گوجه": ["رب"], "پیاز": ["سیر"]},
        "instructions": "بادمجان‌ها رو سرخ کن، با گوجه و پیاز بپز تا جا بیفته.",
        "calories": "۳۵۰ کیلوکالری"
    },
    {
        "name": "شامی کباب",
        "ingredients": ["گوشت", "تخم‌مرغ", "پیاز", "آرد نخودچی", "نمک"],
        "substitutes": {"آرد نخودچی": ["آرد سویا"]},
        "instructions": "مواد رو مخلوط کن، شکل بده و سرخ کن.",
        "calories": "۵۵۰ کیلوکالری"
    },
    {
        "name": "برنج ساده با تخم‌مرغ",
        "ingredients": ["برنج", "تخم‌مرغ", "روغن", "نمک"],
        "substitutes": {},
        "instructions": "برنج رو بپز، تخم‌مرغ رو نیمرو کن و با برنج سرو کن.",
        "calories": "۴۰۰ کیلوکالری"
    },
    {
        "name": "سوپ جو",
        "ingredients": ["جو", "هویج", "سیب‌زمینی", "پیاز", "آب مرغ"],
        "substitutes": {"آب مرغ": ["آب گوشت", "آب سبزیجات"]},
        "instructions": "همه مواد رو با آب مرغ بپز تا نرم و غلیظ بشه.",
        "calories": "۳۵۰ کیلوکالری"
    }
]

# شروع گفتگو
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام رفیق خوش‌خوراک! 😋\nبگو ببینم الان توی خونه چه مواد غذایی داری؟ (مثلاً: تخم‌مرغ، گوجه، برنج)"
    )
    return ASK_INGREDIENTS

# بررسی مواد و پیشنهاد غذا
async def ask_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.replace("،", ",").split(",")
    user_ingredients = [i.strip() for i in user_input if i.strip()]
    context.user_data["ingredients"] = user_ingredients

    suggestions, similar, buy_suggestions = [], [], []

    for recipe in recipes:
        required = recipe["ingredients"]
        available = [i for i in required if i in user_ingredients]
        missing = [i for i in required if i not in user_ingredients]
        match_ratio = len(available) / len(required)

        if match_ratio >= 0.7:
            suggestions.append((recipe, missing))
        elif match_ratio >=
elif match_ratio >= 0.5:
            similar.append((recipe, missing))
        elif len(missing) == 1:
            buy_suggestions.append((recipe, missing))

    if suggestions:
        text = "🍽️ با موادت می‌تونیم این غذاها رو درست کنیم:\n"
        for r, missing in suggestions:
            text += f"• {r['name']}"
            for m in missing:
                subs = r.get("substitutes", {}).get(m)
                if subs:
                    text += f" (نداری {m}؟ می‌تونی از {', '.join(subs)} استفاده کنی)"
            text += "\n"
        text += "\nهر کدوم رو انتخاب کنی، آموزش پخت و کالریش رو بهت می‌دم 😍"
        context.user_data["options"] = [r["name"] for r, _ in suggestions]
        await update.message.reply_text(text)
        return SHOW_OPTIONS

    elif buy_suggestions:
        text = "🛒 اگه یه خرید کوچیک انجام بدی، این غذاها برات باز می‌شن:\n"
        for r, missing in buy_suggestions:
            text += f"• {r['name']} ← فقط لازمه بخری: {', '.join(missing)}\n"
        await update.message.reply_text(text)
        return ConversationHandler.END

    elif similar:
        text = "🤔 با مواد فعلی‌ات غذاهای مشابه اینا رو می‌تونی درست کنی:\n"
        for r, missing in similar:
            text += f"• {r['name']} (کم داری: {', '.join(missing)})\n"
        await update.message.reply_text(text)
        return ConversationHandler.END

    else:
        await update.message.reply_text("متأسفم رفیق، با این مواد غذایی چیزی پیدا نکردم. می‌خوای یه لیست دیگه بدی؟")
        return ASK_INGREDIENTS

# انتخاب غذا و نمایش دستور پخت
async def show_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    selected = next((r for r in recipes if r["name"] == choice), None)

    if not selected or choice not in context.user_data.get("options", []):
        await update.message.reply_text("لطفاً یکی از غذاهای پیشنهادی رو انتخاب کن عزیز.")
        return SHOW_OPTIONS

    await update.message.reply_text(
        f"👨‍🍳 آموزش پخت {selected['name']}:\n{selected['instructions']}\n\n🔥 انرژی: {selected['calories']}\n\nنوش جونت رفیق! ❤️",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# لغو گفتگو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔ گفتگو لغو شد. هر وقت خواستی دوباره بپرس، من اینجام! 🤗", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# اجرای ربات
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ingredients)],
            SHOW_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_recipe)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
