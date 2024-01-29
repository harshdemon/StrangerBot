# https://github.com/Imshukla87/SHUKLA-ROBOT
# https://github.com/Imshukla87

# <============================================== IMPORTS =========================================================>
import asyncio
import contextlib
import importlib
import json
import re
import time
import traceback
from platform import python_version
from random import choice

import psutil
import pyrogram
import telegram
import telethon
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import (
    BadRequest,
    ChatMigrated,
    Forbidden,
    NetworkError,
    TelegramError,
    TimedOut,
)
from telegram.ext import (
    ApplicationHandlerStop,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown

import Database.sql.users_sql as sql
from Infamous.karma import *
from Mikobot import (
    BOT_NAME,
    LOGGER,
    OWNER_ID,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    app,
    dispatcher,
    function,
    loop,
    tbot,
)
from Mikobot.plugins import ALL_MODULES
from Mikobot.plugins.helper_funcs.chat_status import is_user_admin
from Mikobot.plugins.helper_funcs.misc import paginate_modules

# <=======================================================================================================>

PYTHON_VERSION = python_version()
PTB_VERSION = telegram.__version__
PYROGRAM_VERSION = pyrogram.__version__
TELETHON_VERSION = telethon.__version__


# <============================================== FUNCTIONS =========================================================>


async def more_ai_handler_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "more_ai_handler":
        await query.answer()
        await query.message.edit_text(
            "*Here's more image gen-related commands*:\n\n"
            "Command: /meinamix\n"
            "  • Description: Generates an image using the meinamix model.\n\n"
            "Command: /darksushi\n"
            "  • Description: Generates an image using the darksushi model.\n\n"
            "Command: /meinahentai\n"
            "  • Description: Generates an image using the meinahentai model.\n\n"
            "Command: /darksushimix\n"
            "  • Description: Generates an image using the darksushimix model.\n\n"
            "Command: /anylora\n"
            "  • Description: Generates an image using the anylora model.\n\n"
            "Command: /cetsumix\n"
            "  • Description: Generates an image using the cetus-mix model.\n\n"
            "Command: /darkv2\n"
            "  • Description: Generates an image using the darkv2 model.\n\n"
            "Command: /creative\n"
            "  • Description: Generates an image using the creative model.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⇦ 𝘽𝘼𝘾𝙆", callback_data="ai_handler"),
                    ],
                ],
            ),
        )


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Mikobot.plugins." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
async def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    await dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )

async def stats_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "insider_":
        uptime = get_readable_time((time.time() - StartTime))
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        text = f"""
𝙎𝙮𝙨𝙩𝙚𝙢 𝙨𝙩𝙖𝙩𝙨 ˹ 𝗦𝙴𝙽𝙾𝚁𝙸𝚃𝙰 ✘ 𝗥𝙾𝙱𝙾 ˼
➖➖➖➖➖➖
UPTIME ➼ {uptime}
CPU ➼ {cpu}%
RAM ➼ {mem}%
DISK ➼ {disk}%

PYTHON ➼ {PYTHON_VERSION}

PTB ➼ {PTB_VERSION}
TELETHON ➼ {TELETHON_VERSION}
PYROGRAM ➼ {PYROGRAM_VERSION}
"""
        await query.answer(text=text, show_alert=True)


async def gitsource_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "git_source":
        source_link = "https://github.com/itzshukla"
        message_text = (
            f"*Here is the link for the public source repo*:\n\n{source_link}"
        )

        # Adding the inline button
        keyboard = [[InlineKeyboardButton(text="◁", callback_data="Miko_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=reply_markup,
        )





async def Miko_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "Miko_":
        uptime = get_readable_time((time.time() - StartTime))
        message_text = (
            f"➲ <b>Ai integration.</b>"
            f"\n➲ <b>Advance management capability.</b>"
            f"\n➲ <b>Anime bot functionality.</b>"
            f"\n\n<b>USERS</b> » {sql.num_users()}"
            f"\n<b>CHATS</b> » {sql.num_chats()}"
            f"\n\n<b>Click on the buttons below for getting help and info about</b> {BOT_NAME}."
        )
        await query.message.edit_text(
            text=message_text,
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ABOUT", callback_data="Miko_support"
                        ),
                        InlineKeyboardButton(text="COMMAND", callback_data="help_back"),
                    ],
                    [
                        InlineKeyboardButton(text="INSIDER", callback_data="insider_"),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="Miko_back"),
                    ],
                ]
            ),
        )
    
