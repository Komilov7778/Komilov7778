import os
import nest_asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1086444553

TEMP_VIDEOS = {}

def log(message):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")

if not os.path.exists("media"):
    os.makedirs("media")

nest_asyncio.apply()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log("/start buyrug'i olindi")
    await update.message.reply_text("Assalomu alaykum kino izlovchi botga xush kelibsiz!")
    await update.message.reply_text("Kinoni olish uchun kodni yuboring.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log(f"Video olindi - foydalanuvchi: {user_id}")

    if user_id != ADMIN_ID:
        await update.message.reply_text("Kechirasiz, siz admin emassiz.")
        log("Foydalanuvchi admin emas.")
        return

    video = update.message.video or update.message.document
    if not video:
        await update.message.reply_text("Faqat video yuboring.")
        log("Video object None.")
        return

    try:
        file = await context.bot.get_file(video.file_id)
        temp_path = f"media/temp_{user_id}.mp4"
        await file.download_to_drive(temp_path)
        TEMP_VIDEOS[user_id] = temp_path
        await update.message.reply_text("Video qabul qilindi. Kodni yuboring:")
        log(f"Video saqlandi: {temp_path}")
    except Exception as e:
        log(f"Xatolik: {str(e)}")

async def handle_admin_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    log(f"Kod: {text} | foydalanuvchi: {user_id}")

    if user_id != ADMIN_ID or user_id not in TEMP_VIDEOS:
        await send_movie(update, context)
        return

    try:
        code = int(text)
        new_path = f"media/{code}.mp4"
        os.rename(TEMP_VIDEOS[user_id], new_path)
        del TEMP_VIDEOS[user_id]
        await update.message.reply_text(f"Kino saqlandi: {new_path}")
        log(f"Video saqlandi: {new_path}")
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {str(e)}")
        log(f"Xatolik: {str(e)}")

async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        code = int(update.message.text.strip())
        file_path = f"media/{code}.mp4"
        if os.path.exists(file_path):
            await update.message.reply_video(video=open(file_path, 'rb'))
            log(f"Kino yuborildi: {file_path}")
        else:
            await update.message.reply_text("Kino topilmadi.")
            log(f"Kod topilmadi: {file_path}")
    except ValueError:
        await update.message.reply_text("Faqat raqam yuboring.")
        log("Noto‘g‘ri format.")

if __name__ == "__main__":
    log("Bot ishga tushmoqda...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_code))
    print("✅ Kino bot ishga tushdi!")
    app.run_polling()
