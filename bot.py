"""
TezWeb Editor Bot — Matn tahrirlovchi bot
Guruhda teg qilib matn yuboring — bot grammatikani tuzatadi va 5-6 variant beradi
"""

import os
import logging
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN     = os.environ.get("EDITOR_BOT_TOKEN", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """Sen o'zbek tili grammatika ekspertisan. Foydalanuvchi matn yuborsa:

1. Matnni grammatik jihatdan to'g'irla
2. Imlo xatolarini tuzat
3. Tinish belgilarini to'g'irla
4. 5 xil uslubda qayta yoz:
   - Rasmiy (official) uslub
   - Oddiy (sodda) uslub
   - Ijodiy (creative) uslub
   - Qisqa (brief) uslub
   - Professional uslub

Javobni aniq quyidagi formatda ber:

✅ TUZATILGAN MATN:
[tuzatilgan matn]

📝 XATOLAR:
[qanday xatolar bor edi, qisqacha]

🎨 5 VARIANT:

1️⃣ Rasmiy uslub:
[matn]

2️⃣ Oddiy uslub:
[matn]

3️⃣ Ijodiy uslub:
[matn]

4️⃣ Qisqa uslub:
[matn]

5️⃣ Professional uslub:
[matn]

Faqat o'zbek tilida javob ber."""


async def check_and_edit(text: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": f"Quyidagi matnni tekshirib to'g'irla:\n\n{text}"}],
        system=SYSTEM_PROMPT
    )
    return msg.content[0].text


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = context.bot.username
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Guruhga qo'shish", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("📢 @tezweb_uz", url="https://t.me/tezweb_uz"),
         InlineKeyboardButton("🌐 tezweb.uz", url="https://tezweb.uz")],
        [InlineKeyboardButton("💬 Yaratuvchi", url="https://t.me/Shohdollar22")],
    ])
    text = (
        "✍️ <b>TezWeb Matn Tahrirlovchi Bot</b>\n\n"
        "Men o'zbek tili grammatikasini tekshiruvchi aqlli botman!\n\n"
        "🔹 <b>Nima qila olaman:</b>\n"
        "• Grammatik xatolarni topaman va tuzataman\n"
        "• Imlo va tinish belgilarini tekshiraman\n"
        "• 5 xil uslubda variant taqdim etaman\n"
        "• Rasmiy, oddiy, ijodiy, qisqa, professional\n\n"
        "🔹 <b>Qanday ishlatish:</b>\n"
        "💬 <b>Shaxsiy xabarda:</b> Matnni yuboring\n"
        "👥 <b>Guruhda:</b> @botni teg qilib matn yuboring\n"
        "<code>@tezweb_editor_bot Salom, men bugun ishlayapman</code>\n\n"
        "🔹 <b>Misol:</b>\n"
        "<i>Tekshirib to'g'irlab ber: Bu kun men do'konga bordim va narsa sotib oldim</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🤖 <b>TezWeb.uz botlari:</b>\n"
        "• ✍️ Matn tahrirlovchi — siz hozir\n"
        "• 🌡 Ob-havo va kurs boti\n"
        "• 🛡 Antispam boti — @TezWebBot_Antispam\n\n"
        "📩 Muammo yoki taklif: @Shohdollar22\n"
        "🌐 tezweb.uz | 📢 @tezweb_uz"
    )
    await update.message.reply_text(text, parse_mode="HTML",
                                    reply_markup=keyboard,
                                    disable_web_page_preview=True)


async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = context.bot.username
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Guruhga qo'shish", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("👥 Do'stlarga tavsiya", url=f"https://t.me/share/url?url=https://t.me/{bot_username}&text=O'zbek tili grammatikasini tekshiruvchi aqlli bot!")],
    ])
    text = (
        "ℹ️ <b>Bot haqida</b>\n\n"
        "✍️ <b>TezWeb Matn Tahrirlovchi Bot</b>\n\n"
        "🧠 <b>Texnologiya:</b> Claude AI (Anthropic)\n"
        "👨‍💻 <b>Yaratuvchi:</b> @Shohdollar22\n"
        "🏢 <b>Kompaniya:</b> TezWeb.uz\n"
        "🌐 <b>Sayt:</b> tezweb.uz\n\n"
        "📋 <b>Funksiyalar:</b>\n"
        "✅ O'zbek tili grammatikasini tekshirish\n"
        "✅ Imlo xatolarini tuzatish\n"
        "✅ 5 xil uslubda variant berish\n"
        "✅ Guruhda teg orqali ishlash\n"
        "✅ Shaxsiy xabarda ishlash\n\n"
        "📢 <b>Kanal:</b> @tezweb_uz\n"
        "💬 <b>Bog'lanish:</b> @Shohdollar22"
    )
    await update.message.reply_text(text, parse_mode="HTML",
                                    reply_markup=keyboard,
                                    disable_web_page_preview=True)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text
    chat_type = update.effective_chat.type
    bot_username = context.bot.username

    # Guruhda faqat teg qilinganda ishlaydi
    if chat_type in ("group", "supergroup"):
        if not (f"@{bot_username}" in text):
            # Reply to bot message ham ishlaydi
            if not (message.reply_to_message and
                    message.reply_to_message.from_user and
                    message.reply_to_message.from_user.username == bot_username):
                return
        # Teg nomini olib tashlash
        text = text.replace(f"@{bot_username}", "").strip()

    if not text or len(text) < 5:
        await message.reply_text(
            "✍️ Iltimos, tekshirilishi kerak bo'lgan matnni yuboring.\n"
            "Minimal 5 ta belgi bo'lishi kerak."
        )
        return

    if len(text) > 3000:
        await message.reply_text(
            "⚠️ Matn juda uzun! Maksimal 3000 belgi.\n"
            f"Sizning matningiz: {len(text)} belgi."
        )
        return

    # Yozmoqda ko'rsatish
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    logger.info("Matn tekshirilmoqda: %s belgi", len(text))

    try:
        result = await check_and_edit(text)

        # Telegram 4096 belgi limitini tekshirish
        if len(result) > 4000:
            # Ikki qismga bo'lib yuborish
            mid = result[:4000].rfind("\n\n")
            if mid == -1:
                mid = 4000
            await message.reply_text(result[:mid])
            await message.reply_text(result[mid:].strip() + "\n\n━━━━━━━━━━━━━━━━━━━\n🌐 tezweb.uz | 📢 @tezweb_uz")
        else:
            await message.reply_text(
                result + "\n\n━━━━━━━━━━━━━━━━━━━\n"
                "🌐 tezweb.uz | 📢 @tezweb_uz | 📩 @Shohdollar22"
            )

        logger.info("Javob yuborildi")

    except Exception as e:
        logger.error("Xato: %s", e)
        await message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.\n"
            "Muammo davom etsa: @Shohdollar22"
        )


def main():
    if not BOT_TOKEN:
        print("EDITOR_BOT_TOKEN ni Railway Variables ga kiriting!")
        return
    if not ANTHROPIC_KEY:
        print("ANTHROPIC_API_KEY ni Railway Variables ga kiriting!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("info",  cmd_info))
    app.add_handler(CommandHandler("help",  cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("TezWeb Editor Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
