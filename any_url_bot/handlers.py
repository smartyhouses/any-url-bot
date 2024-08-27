import aiogram
import aiogram.exceptions
import aiogram.types
import pydantic
from aiogram.utils import keyboard
from any_url_bot import url as _url
import subprocess
import sys

def check_and_install(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

check_and_install('g4f')
check_and_install('curl_cffi')
check_and_install('fastapi')
from g4f.client import Client


_START_TEXT = (
    "привет я портал твой облачная система"
    "ага. "
)
_INVALID_URL_TEXT = "The URL you sent is invalid."


router = aiogram.Router()

def no_url(text):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}],
        )
    return response.choices[0].message.content


@router.message(commands="start", content_types=aiogram.types.ContentType.TEXT)
async def handle_start_cmd(msg: aiogram.types.Message):
    return msg.answer(_START_TEXT)


@router.message(content_types=aiogram.types.ContentType.TEXT)
async def handle_url(msg: aiogram.types.Message):
    url = _url.normalize_url(msg.text)  # type: ignore  # msg.text can't be None

    try:
        web_app = _url.WebAppInfo(url=url)
    except pydantic.ValidationError:
        return msg.answer(text=no_url(msg.text))

    kb_builder = keyboard.InlineKeyboardBuilder()
    kb_builder.button(text=msg.text, web_app=web_app)
    await msg.answer(
        text=url, disable_web_page_preview=True, reply_markup=kb_builder.as_markup()
    )
