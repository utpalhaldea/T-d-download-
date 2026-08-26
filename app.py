import os
import asyncio
import logging
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from telethon import events
from telethon.tl.functions.bots import SetBotCommandsRequest
from telethon.tl.types import (
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopePeer,
)

from telegram_logic.bot import bot
from telegram_logic.terabox_trad import process_terabox
from telegram_logic.terabox_exp import process_terabox_experimental
from telegram_logic.diskwala import process_diskwala
from telegram_logic.helpers import (
    extract_all_surls,
    extract_all_terabox_url_exp,
)

from diskwalaDL.public_api import (
    extract_all_diskwala_urls,
    get_diskwala_info,
)

from firebase_db.users import track_user, get_user_mode

from dotenv import load_dotenv
load_dotenv()


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
APP_ID = int(os.environ.get("APP_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
STORAGE_GROUP_ID = int(os.environ.get("STORAGE_GROUP_ID", "0"))

PORT = int(os.environ.get("PORT", "3000"))


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)

log = logging.getLogger(__name__)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="DiskWala Video API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================
# During testing this allows your frontend to call the backend.
# Later you can replace "*" with your real website domain.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class DiskwalaRequest(BaseModel):
    url: str


# ============================================================
# URL VALIDATION
# ============================================================

def validate_diskwala_url(url: str) -> bool:
    """
    Only allow DiskWala URLs.
    """

    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        hostname = (parsed.hostname or "").lower()

        if hostname == "diskwala.com":
            return True

        if hostname.endswith(".diskwala.com"):
            return True

        return False

    except Exception:
        return False


# ============================================================
# DISKWALA WEB API
# ============================================================

@app.post("/api/diskwala/resolve")
async def resolve_diskwala(request: DiskwalaRequest):

    url = request.url.strip()

    if not url:
        raise HTTPException(
            status_code=400,
            detail="DiskWala URL is required."
        )

    if not validate_diskwala_url(url):
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid DiskWala URL."
        )

    log.info("Resolving DiskWala URL: %s", url)

    try:
        # get_diskwala_info() uses requests, which is blocking.
        # Run it in a worker thread so FastAPI stays responsive.
        result = await asyncio.to_thread(
            get_diskwala_info,
            url
        )

    except Exception as e:
        log.error(
            "DiskWala resolve failed: %s",
            e,
            exc_info=True,
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to resolve this DiskWala link."
        )

    download_url = result.get("download_url")

    if not download_url:
        raise HTTPException(
            status_code=502,
            detail="No video URL was returned."
        )

    return {
        "success": True,
        "filename": result.get(
            "filename",
            "diskwala_video.mp4"
        ),
        "size": result.get("size", 0),
        "mime_type": result.get(
            "mime_type",
            "video/mp4"
        ),
        "video_url": download_url,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/ping")
async def ping():
    return {
        "status": "ok",
        "service": "DiskWala Video API"
    }


# ============================================================
# GLOBAL USER TRACKER
# ============================================================

@bot.on(events.NewMessage)
async def global_tracker(event):

    username = None

    if getattr(event.sender, "username", None):
        username = event.sender.username

    elif getattr(event.chat, "username", None):
        username = event.chat.username

    try:
        track_user(
            event.chat_id,
            username
        )

    except Exception as e:
        log.error(
            "[global_tracker] track_user error: %s",
            e
        )


# ============================================================
# REGISTER COMMANDS
# ============================================================

import telegram_logic.commands  # noqa: F401


# ============================================================
# WRONG SOURCE MESSAGES
# ============================================================

DISKWALA_IN_TERABOX_MODE = (
    "🔗 That looks like a **Diskwala** link, "
    "but your current mode downloads **TeraBox** videos.\n\n"
    "➡️ Use the **/dw** command:\n"
    "`/dw <link>`"
)

TERABOX_IN_DISKWALA_MODE = (
    "🔗 That looks like a **TeraBox** link, "
    "but your current mode is **dw** (Diskwala).\n\n"
    "➡️ Use **/exp**, **/exphd** or **/get**."
)


# ============================================================
# TELEGRAM MESSAGE HANDLER
# ============================================================

@bot.on(events.NewMessage)
async def handle_message(event):

    text = event.raw_text or ""

    if text.startswith("/"):
        return

    try:
        mode = get_user_mode(event.chat_id)

    except Exception as e:

        log.error(
            "[handle_message] DB error: %s",
            e
        )

        await event.respond(
            "⚠️ Database error. Please try again later."
        )

        return


    # --------------------------------------------------------
    # TERABOX GET
    # --------------------------------------------------------

    if mode == "get":

        surls = extract_all_surls(text)

        if not surls:

            if extract_all_diskwala_urls(text):
                await event.respond(
                    DISKWALA_IN_TERABOX_MODE
                )

            return

        try:

            await asyncio.gather(
                *[
                    process_terabox(
                        event,
                        surl
                    )
                    for surl in surls
                ]
            )

        except Exception as e:

            log.error(
                "GET mode error: %s",
                e
            )


    # --------------------------------------------------------
    # TERABOX EXP
    # --------------------------------------------------------

    elif mode == "exp":

        urls = extract_all_terabox_url_exp(text)

        if not urls:

            if extract_all_diskwala_urls(text):
                await event.respond(
                    DISKWALA_IN_TERABOX_MODE
                )

            return

        try:

            await asyncio.gather(
                *[
                    process_terabox_experimental(
                        event,
                        url
                    )
                    for url in urls
                ]
            )

        except Exception as e:

            log.error(
                "EXP mode error: %s",
                e
            )


    # --------------------------------------------------------
    # TERABOX EXP HD
    # --------------------------------------------------------

    elif mode == "exphd":

        urls = extract_all_terabox_url_exp(text)

        if not urls:

            if extract_all_diskwala_urls(text):
                await event.respond(
                    DISKWALA_IN_TERABOX_MODE
                )

            return

        try:

            await asyncio.gather(
                *[
                    process_terabox_experimental(
                        event,
                        url,
                        is_hd=True
                    )
                    for url in urls
                ]
            )

        except Exception as e:

            log.error(
                "EXPhd mode error: %s",
                e
            )


    # --------------------------------------------------------
    # DISKWALA
    # --------------------------------------------------------

    elif mode == "dw":

        urls = extract_all_diskwala_urls(text)

        if not urls:

            if extract_all_terabox_url_exp(text):
                await event.respond(
                    TERABOX_IN_DISKWALA_MODE
                )

            return

        try:

            await asyncio.gather(
                *[
                    process_diskwala(
                        event,
                        url
                    )
                    for url in urls
                ]
            )

        except Exception as e:

            log.error(
                "DiskWala mode error: %s",
                e
            )


# ============================================================
# TELEGRAM BOT
# ============================================================

async def run_bot():

    if not BOT_TOKEN or not APP_ID or not API_HASH:

        log.error(
            "BOT_TOKEN, APP_ID and API_HASH "
            "must be configured."
        )

        return


    if not STORAGE_GROUP_ID:

        log.warning(
            "STORAGE_GROUP_ID not set. "
            "Caching disabled."
        )


    await bot.start(
        bot_token=BOT_TOKEN
    )


    default_commands = [

        BotCommand(
            command="start",
            description="Start BOT"
        ),

        BotCommand(
            command="exp",
            description="Download TeraBox video"
        ),

        BotCommand(
            command="exphd",
            description="Download HD TeraBox video"
        ),

        BotCommand(
            command="get",
            description="Download TeraBox video"
        ),

        BotCommand(
            command="dw",
            description="Download Diskwala video"
        ),

        BotCommand(
            command="random",
            description="Get a random video"
        ),

        BotCommand(
            command="settings",
            description="View Details"
        ),

        BotCommand(
            command="op",
            description="Send feedback to admin"
        ),
    ]


    await bot(
        SetBotCommandsRequest(
            scope=BotCommandScopeDefault(),
            lang_code="",
            commands=default_commands
        )
    )


    admin_id = int(
        os.environ.get(
            "ADMIN_ID",
            "0"
        )
    )


    if admin_id:

        try:

            admin_peer = await bot.get_input_entity(
                admin_id
            )

            admin_commands = default_commands + [

                BotCommand(
                    command="recent",
                    description="[Admin] Show recent users"
                ),

                BotCommand(
                    command="broadcast",
                    description="[Admin] Broadcast message"
                ),
            ]


            await bot(
                SetBotCommandsRequest(
                    scope=BotCommandScopePeer(
                        peer=admin_peer
                    ),
                    lang_code="",
                    commands=admin_commands
                )
            )

        except Exception as e:

            log.error(
                "Failed to set admin commands: %s",
                e
            )


    log.info(
        "Bot started."
    )

    await bot.run_until_disconnected()


# ============================================================
# FASTAPI LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    bot_task = asyncio.create_task(
        run_bot()
    )

    yield

    bot_task.cancel()

    try:
        await bot_task

    except asyncio.CancelledError:
        pass

    if bot.is_connected():

        await bot.disconnect()

    log.info(
        "Application stopped."
    )


# Replace the earlier FastAPI instance with lifespan-enabled app.
app.router.lifespan_context = lifespan


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT
    )
