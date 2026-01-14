import asyncio
import os
import random
import logging
import yt_dlp
from telebot.async_telebot import AsyncTeleBot
from telebot import types
# --- LOGGING KONFIGURATSIYA (Serverda kuzatish uchun) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
# --- KONFIGURATSIYA ---
BOT_TOKEN = "8454365381:AAGZFBMBaxpEpX4iMMtnUzawxR0JU7qm9j4"
bot = AsyncTeleBot(8454365381:AAGZFBMBaxpEpX4iMMtnUzawxR0JU7qm9j4)
# User holatini saqlash uchun
user_states = {} # {chat_id: {"looping": bool, "last_msg_id": int}}
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
    
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4, btn5)
    markup.add(btn_stop)
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
    
    if not os.path.exists('music'):
        os.makedirs('music')
        
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            entry = info['entries'][0]
            filename = ydl.prepare_filename(entry)
            title = entry.get('title', 'Unknown Title')
        else:
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Unknown Title')
        
        actual_filename = os.path.splitext(filename)[0] + ".mp3"
        return actual_filename, title
# --- HANDLERLAR ---
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    chat_id = message.chat.id
    user_states[chat_id] = {"looping": False, "last_msg_id": None}
    
    welcome_text = (
        "❤️ **Xolisxon Botiga xush kelibsiz!** ❤️\n\n"
        "Ushbu bot sizga cheksiz sevgi izhorlari, romantik she'rlar va "
        "istalgan musiqani qidirib topishda yordam beradi.\n\n"
        "Pastdagi tugmalardan birini tanlang:"
    )
    await bot.send_message(chat_id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
@bot.callback_query_handler(func=lambda call: True)
async def callback_listener(call):
    chat_id = call.message.chat.id
    
    if call.data == "loop_love":
        if chat_id not in user_states:
            user_states[chat_id] = {"looping": False, "last_msg_id": None}
            
        if user_states[chat_id]["looping"]:
            await bot.answer_callback_query(call.id, "Oqim allaqachon yoqilgan! ✅")
            return
            
        user_states[chat_id]["looping"] = True
        await bot.answer_callback_query(call.id, "Cheksiz sevgi oqimi boshlandi... ❤️")
        
        msg = await bot.send_message(chat_id, "❤️ Oqim boshlanmoqda...", reply_markup=get_stop_only_keyboard())
        user_states[chat_id]["last_msg_id"] = msg.message_id
        
        while user_states.get(chat_id, {}).get("looping"):
            try:
                text = random.choice(ROMANTIC_TEXTS)
                heart = random.choice(HEART_EFFECTS)
                full_text = f"{heart} {text} {heart}\n\n[Hamma narsani to'xtatish uchun STOP ni bosing]"
                
                await bot.edit_message_text(
                    text=full_text,
                    chat_id=chat_id,
                    message_id=user_states[chat_id]["last_msg_id"],
                    reply_markup=get_stop_only_keyboard()
                )
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Loop error for chat {chat_id}: {e}")
                await asyncio.sleep(5)
                
    elif call.data == "stop_all":
        if chat_id in user_states:
            user_states[chat_id]["looping"] = False
        
        await bot.answer_callback_query(call.id, "Hammasi to'xtatildi! ⛔")
        await bot.send_message(chat_id, "Barcha jarayonlar to'xtatildi. Asosiy menyu:", reply_markup=get_main_keyboard())
    elif call.data == "poems":
        poem = random.choice(POEMS)
        await bot.send_message(chat_id, poem, reply_markup=get_main_keyboard())
        await bot.answer_callback_query(call.id)
    elif call.data == "melt_heart":
        text = "🔥 Sen mening borlig'imsan. Har bir kulguing bilan dunyomni yoritganing uchun rahmat! ❤️"
        await bot.send_message(chat_id, text, reply_markup=get_main_keyboard())
        await bot.answer_callback_query(call.id)
    elif call.data == "night_voice":
        text = "🌙 Tun bo'yi seni o'ylayman... Shirin tushlar ko'r, mening farishtam. ✨"
        await bot.send_message(chat_id, text, reply_markup=get_main_keyboard())
        await bot.answer_callback_query(call.id)
    elif call.data == "music_search":
        await bot.send_message(chat_id, "🎵 Qaysi musiqani qidirmoqchisiz? Iltimos, nomi va xonandasini yozing:")
        bot.register_next_step_handler_by_chat_id(chat_id, process_music_search)
        await bot.answer_callback_query(call.id)
async def process_music_search(message):
    chat_id = message.chat.id
    query = message.text
    
    if query.startswith('/'):
        return
        
    status_msg = await bot.send_message(chat_id, f"🔍 '{query}' qidirilmoqda... kuting.")
    
    try:
        file_path, title = await download_audio(query)
        
        with open(file_path, 'rb') as audio:
            await bot.send_audio(
                chat_id, 
                audio, 
                caption=f"✅ {title}\n\n@xolisxon_bot ❤️",
                reply_markup=get_main_keyboard()
            )
        
        os.remove(file_path)
        await bot.delete_message(chat_id, status_msg.message_id)
        
    except Exception as e:
        logger.error(f"Music download error: {e}")
        await bot.edit_message_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.", chat_id, status_msg.message_id, reply_markup=get_main_keyboard())
# --- RUN ---
async def main():
    logger.info("Bot serverda ishga tushirildi...")
    await bot.polling(non_stop=True)
if __name__ == "__main__":
    asyncio.run(main())
