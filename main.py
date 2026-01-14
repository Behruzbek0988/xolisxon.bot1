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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- KONFIGURATSIYA ---
# Koyeb'dagi Environment Variable'dan tokenni oladi
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
    "Seni baxtli ko'rish - mening eng katta orzuim. 🌈",
    "Yuragimning har bir urushi 'Seni sevaman' demoqda. ❤️‍🔥",
    "Sen meni qorong'u dunyomdagi eng porloq yulduzimsan. ⭐",
    "Seni sog'inish - bu shirin azob. 🍯",
    "Yoningda bo'lsam ham, seni yana sog'inaveraman. 🥺"
]

POEMS = [
    "Ko'zlaringga boqsam, dunyo unutilar,\nSening sevging bilan dillar yorishar.\nSening borliging - bu baxtim, iqbolim,\nSeni sevish - mening hayotiy yo'lim. ❤️",
    "Sevgi nima? Bu sening kulguing,\nYuragimda qolgan o'chmas tuyg'uing.\nSeni sog'inganda osmon yig'laydi,\nSening sevging meni mangu bog'laydi. 🌹",
    "Xolisxonim, go'zalim, yagonam o'zing,\nShirin so'zing, nurli ko'zing, baxtim o'zing.\nSeni sevishdan hech qachon tolmayman,\nSensiz bu dunyoda yashay olmayman. ✨"
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

def get_stop_only_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⛔ STOP", callback_data="stop_all"))
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
        'no_warnings': True,
        'default_search': 'ytsearch1'
    }
    if not os.path.exists('music'): os.makedirs('music')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        entry = info['entries'][0] if 'entries' in info else info
        filename = ydl.prepare_filename(entry)
        actual_filename = os.path.splitext(filename)[0] + ".mp3"
        return actual_filename, entry.get('title', 'Musiqa')

# --- HANDLERLAR ---

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    chat_id = message.chat.id
    user_states[chat_id] = {"looping": False, "last_msg_id": None}
    welcome_text = "❤️ **Xolisxon Botiga xush kelibsiz!** ❤️\n\nTanlang:"
    await bot.send_message(chat_id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
async def callback_listener(call):
    chat_id = call.message.chat.id
    if call.data == "loop_love":
        user_states[chat_id] = {"looping": True}
        await bot.answer_callback_query(call.id, "Boshlandi... ❤️")
        msg = await bot.send_message(chat_id, "❤️ Oqim...", reply_markup=get_stop_only_keyboard())
        while user_states.get(chat_id, {}).get("looping"):
            try:
                text = f"{random.choice(HEART_EFFECTS)} {random.choice(ROMANTIC_TEXTS)}"
                await bot.edit_message_text(text, chat_id, msg.message_id, reply_markup=get_stop_only_keyboard())
                await asyncio.sleep(5)
            except: break
    elif call.data == "stop_all":
        user_states[chat_id] = {"looping": False}
        await bot.send_message(chat_id, "To'xtatildi.", reply_markup=get_main_keyboard())
    elif call.data == "music_search":
        await bot.send_message(chat_id, "🎵 Musiqa nomini yozing:")
    elif call.data == "poems":
        await bot.send_message(chat_id, random.choice(POEMS), reply_markup=get_main_keyboard())

# Musiqa qidirish xabarlarini tutish
@bot.message_handler(func=lambda m: True)
async def handle_text(message):
    if message.text.startswith('/'): return
    status_msg = await bot.send_message(message.chat.id, "🔍 Qidirilmoqda...")
    try:
        file_path, title = await download_audio(message.text)
        with open(file_path, 'rb') as audio:
            await bot.send_audio(message.chat.id, audio, caption=f"✅ {title}")
        os.remove(file_path)
        await bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception as e:
        await bot.edit_message_text("❌ Topilmadi.", message.chat.id, status_msg.message_id)

# --- RUN ---
async def main():
    logger.info("Bot yondi...")
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    asyncio.run(main())
