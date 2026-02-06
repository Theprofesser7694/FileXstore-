# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport

import asyncio
import os
import random
import sys
import re
import string
import time
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import *
from database.database import *
from database.db_premium import *

BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

# ========================================================= #

async def short_url(client: Client, message: Message, base64_string):
    prem_link = f"https://t.me/{client.username}?start=yu3elk{base64_string}7"

    if not SHORTLINK_API:
        return await message.reply_text(
            "⚠️ <b>Shortlink service disabled.</b>\n\n"
            "Admin ने API KEY set नहीं की है।\n\n"
            f"👇 Direct Link:\n{prem_link}",
            parse_mode=ParseMode.HTML
        )

    try:
        short_link = await get_shortlink(
            SHORTLINK_URL,
            SHORTLINK_API,
            prem_link
        )

        buttons = [
            [
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ", url=short_link),
                InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ", url=TUT_VID)
            ],
            [
                InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
            ]
        ]

        await message.reply_photo(
            photo=SHORTENER_PIC,
            caption=SHORT_MSG,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        print(f"Shortlink Error: {e}")
        await message.reply_text(
            f"❌ Shortlink error.\n\nDirect Link:\n{prem_link}"
        )

# ========================================================= #

@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)

    # User DB me add
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Force Subscribe check
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # Ban check
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ आप इस bot से banned हैं</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    FILE_AUTO_DELETE = await db.get_del_timer()
    text = message.text

    # ===================================================== #
    # START PAYLOAD HANDLING (FIXED PART)
    # ===================================================== #

    if len(text) > 7:
        try:
            basic = text.split(" ", 1)[1]

            if basic.startswith("yu3elk"):
                base64_string = basic[6:-1]
            else:
                base64_string = basic

            if not is_premium and user_id != OWNER_ID and not basic.startswith("yu3elk"):
                await short_url(client, message, base64_string)
                return

            decoded = await decode(base64_string)
            argument = decoded.split("-")
            ids = []

            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)

            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]

            else:
                return await message.reply_text("❌ Invalid Link")

        except Exception as e:
            print(f"Payload Error: {e}")
            return

        temp = await message.reply("<b>Please wait...</b>")

        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await temp.delete()
            print(e)
            return await message.reply_text("❌ File नहीं मिली")

        await temp.delete()

        sent_msgs = []

        for msg in messages:
            caption = msg.caption.html if msg.caption else ""
            if CUSTOM_CAPTION:
                caption += f"\n\n{CUSTOM_CAPTION}"

            try:
                s = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    protect_content=PROTECT_CONTENT
                )
                sent_msgs.append(s)
                await asyncio.sleep(0.5)

            except FloodWait as e:
                await asyncio.sleep(e.x)

        if FILE_AUTO_DELETE > 0:
            note = await message.reply(
                f"<b>यह फाइल {get_exp_time(FILE_AUTO_DELETE)} में delete हो जाएगी</b>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for m in sent_msgs:
                try:
                    await m.delete()
                except:
                    pass

            await note.edit("<b>❌ फाइल delete हो चुकी है</b>")

    # ===================================================== #
    # NORMAL START
    # ===================================================== #

    else:
        buttons = [
            [InlineKeyboardButton("• More Channels •", url="https://t.me/ViralVideos_linkss")],
            [
                InlineKeyboardButton("About", callback_data="about"),
                InlineKeyboardButton("Help", callback_data="help")
            ]
        ]

        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name or "",
                last=message.from_user.last_name or "",
                username=f"@{message.from_user.username}" if message.from_user.username else "N/A",
                mention=message.from_user.mention,
                id=user_id
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
                )
                
