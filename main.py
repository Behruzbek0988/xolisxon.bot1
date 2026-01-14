mport asyncio
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

# --- KONFIGURATSIYA (Koyeb Variables orqali olinadi) ---
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
        filename = ydl.prepare_filename(info['entries'][0] if 'entries' in info else info)
        return os.path.splitext(filename)[0] + ".mp3", info.get('title', 'Musiqa')

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
            text = f"{random.choice(HEART_EFFECTS)} {random.choice(ROMANTIC_TEXTS)}"
            try:
                await bot.edit_message_text(text, chat_id, msg.message_id)
                await asyncio.sleep(5)
            except: break
    elif call.data == "stop_all":
        user_states[chat_id] = {"looping": False}
        await bot.send_message(chat_id, "To'xtatildi.", reply_markup=get_main_keyboard())

# --- RUN ---
async def main():
    logger.info("Bot ishga tushdi...")
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    asyncio.run(main())
