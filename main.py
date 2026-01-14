import asyncio
import os
import random
import logging
import yt_dlp
from telebot.async_telebot import AsyncTeleBot
from telebot import types

# --- LOGGING KONFIGURATSIYA ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- KONFIGURATSIYA ---
# Koyeb panelidagi Environment Variables qismidan tokenni oladi
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = AsyncTeleBot(BOT_TOKEN)

# User holatini saqlash uchun
user_states = {}

# --- MA'LUMOTLAR ---
ROMANTIC_TEXTS = [
    "Seni birinchi marta ko'rganimdagidek sevaman... ❤️",
    "Sen meni hayotimni mazmunisan, Xolisxonim! ✨",
    "Dunyo to'xtasa ham, senga bo'lgan sevgim to'xtamaydi. 🌏",
    "Har bir nafasimda seni isming bor. 💫",
    "Sen bilan o'tgan har bir soniya men uchun oltindan qimmat. ⏳",
    "Seni baxtli ko'rish - mening eng katta orzuim. 🌈"
]

POEMS = [
    "Ko'zlaringga boqsam, dunyo unutilar,\nSening sevging bilan dillar yorishar. ❤️",
    "Sevgi nima? Bu sening kulguing,\nYuragimda qolgan o'chmas tuyg'uing. 🌹",
    "Xolisxonim, go'zalim, yagonam o'zing,\nShirin so'zing, nurli ko'zing, baxtim o'zing. ✨"
]

HEART_EFFECTS = ["❤️", "💖", "💗", "💓", "💞", "💕", "💘", "💌", "💝", "🎯"]

# --- YORDAMCHI FUNKSIYALAR ---
def get_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("♾ Cheksiz Sevgi Oqimi", callback_data="loop_love")
    btn2 = types.InlineKeyboardButton("🎵 Musiqa Yuklash", callback_data="music_search")
    btn3 = types.InlineKeyboardButton("📝 She’rlar", callback_data="poems")
    btn4 = types.InlineKeyboardButton("🔥 Yurakni Erit", callback_data="melt_heart")
    btn5 = types.InlineKeyboardButton("🌙 Tungi Vasvasa", callback_data="night_voice")
    btn_stop = types.InlineKeyboardButton("⛔ STOP", callback_data="stop_all")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn_stop)
    return markup

async def download_audio(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'music/%(title)s.%(ext)s',
        'quiet': True,
        'default_search': 'ytsearch1'
    }
    if not os.path.exists('music'): os.makedirs('music')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        entry = info['entries'][0] if 'entries' in info else info
        filename = ydl.prepare_filename(entry)
        return os.path.splitext(filename)[0] + ".mp3", entry.get('title', 'Musiqa')

# --- HANDLERLAR ---
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, "❤️ **Xolisxon Botiga xush kelibsiz!**", reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
async def callback_listener(call):
    chat_id = call.message.chat.id
    if call.data == "loop_love":
        user_states[chat_id] = {"looping": True}
        msg = await bot.send_message(chat_id, "❤️ Oqim boshlandi...")
        while user_states.get(chat_id, {}).get("looping"):
            try:
                text = f"{random.choice(HEART_EFFECTS)} {random.choice(ROMANTIC_TEXTS)}"
                await bot.edit_message_text(text, chat_id, msg.message_id)
                await asyncio.sleep(5)
            except: break
    elif call.data == "stop_all":
        user_states[chat_id] = {"looping": False}
        await bot.send_message(chat_id, "⛔ Barcha jarayonlar to'xtatildi.", reply_markup=get_main_keyboard())
    elif call.data == "poems":
        await bot.send_message(chat_id, random.choice(POEMS), reply_markup=get_main_keyboard())
    elif call.data == "music_search":
        await bot.send_message(chat_id, "🎵 Musiqa nomini va xonandasini yozing:")

@bot.message_handler(func=lambda m: True)
async def handle_text(message):
    if message.text.startswith('/'): return
    status_msg = await bot.send_message(message.chat.id, "🔍 Qidirilmoqda...")
    try:
        file_path, title = await download_audio(message.text)
        with open(file_path, 'rb') as audio:
            await bot.send_audio(message.chat.id, audio, caption=f"✅ {title}\n@xolisxon_bot ❤️")
        os.remove(file_path)
        await bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception as e:
        await bot.edit_message_text("❌ Musiqa topilmadi.", message.chat.id, status_msg.message_id)

# --- RUN ---
async def main():
    logger.info("Bot ishga tushdi!")
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    asyncio.run(main())
