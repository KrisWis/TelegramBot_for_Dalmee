from aiogram.types import Message, CallbackQuery
import logging.handlers
import logging
import os
import aiogram
from aiogram.utils import executor
import dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import googleapiclient.discovery

channel_id = "UChMN4C4ZLFfr313x2KZRCbg"

youtube = googleapiclient.discovery.build(
    "youtube", "v3", developerKey="AIzaSyAskIzatMxeTKd-Y1jcyViO4XZcoczXvfk")


async def playlist_keyboard_creating():

    request = youtube.playlists().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50
    )
    response = request.execute()

    playlists = []
    while request is not None:
        response = request.execute()
        playlists += [{"playlist_name": i["snippet"]["title"],
                       "playlist_id": i["id"]} for i in response["items"]]
        request = youtube.playlists().list_next(request, response)

    playlists_keyboard = InlineKeyboardMarkup()
    for i in playlists:
        playlist_id = i["playlist_id"]

        playlists_keyboard.add(InlineKeyboardButton(
            text=i["playlist_name"],
            callback_data=f"playlist_{playlist_id}"
        ))

    return playlists_keyboard


async def videos_keyboard_creating(playlist_id):

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )

    response = request.execute()

    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += [{"video_name": i["snippet"]["title"], "video_url": f"https://www.youtube.com/watch?v={i['snippet']['resourceId']['videoId']}&list={playlist_id}"}
                           for i in response["items"]]  # "video_image": i["snippet"]["thumbnails"]["high"]["url"]
        request = youtube.playlistItems().list_next(request, response)

    videos_keyboard = InlineKeyboardMarkup()
    for i in playlist_items:

        videos_keyboard.add(InlineKeyboardButton(
            text=i["video_name"],
            url=i["video_url"]
        ))

    videos_keyboard.add(InlineKeyboardButton(
        text="Назад 🔙",
        callback_data="Назад 🔙"
    ))

    return videos_keyboard


dotenv.load_dotenv()  # Загружаем файл .env

# Логирование.
logger = logging.getLogger(__name__)

# Записываем в переменную результат логирования
os.makedirs("Logs", exist_ok=True)


# Cоздаёт все промежуточные каталоги, если они не существуют.
logging.basicConfig(  # Чтобы бот работал успешно, создаём конфиг с базовыми данными для бота
    level=logging.INFO,
    format="[%(levelname)-8s %(asctime)s at           %(funcName)s]: %(message)s",
    datefmt="%d.%d.%Y %H:%M:%S",
    handlers=[logging.handlers.RotatingFileHandler("Logs/     TGBot.log", maxBytes=10485760, backupCount=0), logging.StreamHandler()])


# Создаём Telegram бота и диспетчер:
Bot = aiogram.Bot(os.environ["TOKEN"])
DP = aiogram.Dispatcher(Bot)


# КОГДА ПОЛЬЗОВАТЕЛЬ ПИШЕТ /start
@DP.message_handler(commands=["start"])
async def start(msg: Message):

    await msg.answer("Привет 👋 \n Я - официальный телеграм бот ютубера Dalmee. Я буду отправлять тебе уведомления о выходе новых роликов, а также многое другое!")


@DP.message_handler(commands=["videos"])
async def videos_command_playlistChoice(msg: Message):
    await msg.answer("Выбери интересующий тебя плейлист:", reply_markup=await playlist_keyboard_creating())


@DP.callback_query_handler()
async def videos_command_videoChoice(call: CallbackQuery):
    if call.data.startswith("playlist_"):
        await call.message.edit_text("Выбери интересующее тебя видео:", reply_markup=await videos_keyboard_creating(call.data[9:]))

    elif call.data == "Назад 🔙":
        await call.message.edit_text("Выбери интересующий тебя плейлист:", reply_markup=await playlist_keyboard_creating())

if __name__ == "__main__":  # Если файл запускается как самостоятельный, а не как модуль
    # В консоле будет отоброжён процесс запуска бота
    logger.info("Запускаю бота...")
    executor.start_polling(  # Бот начинает работать
        dispatcher=DP,  # Передаем в функцию диспетчер
        # (диспетчер отвечает за то, чтобы сообщения пользователя доходили до бота)
        on_startup=logger.info("Загрузился успешно!"), skip_updates=True)
    # Если бот успешно загрузился, то в консоль выведется сообщение
