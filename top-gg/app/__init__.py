import datetime
import json
import logging
import os

import aiohttp
import aiosqlite
import pytz
from dotenv import load_dotenv
from quart import Quart, request

load_dotenv()

log = logging.getLogger(__name__)
app = Quart(__name__)

BOT_TOKEN = os.getenv("TOKEN", "").strip()
TOPGG_AUTH = os.getenv("TOPGG_WEBHOOK_AUTH", "").strip()
TOPGG_VOTE_WEBHOOK = os.getenv("TOPGG_VOTE_WEBHOOK_URL", "").strip()
TOPGG_BOT_ID = os.getenv("TOPGG_BOT_ID", "1144179659735572640").strip()


@app.before_serving
async def setup_database():
    async with aiosqlite.connect("votes.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                user_id TEXT PRIMARY KEY,
                total_votes INTEGER NOT NULL DEFAULT 0,
                streak INTEGER NOT NULL DEFAULT 0,
                last_vote_time TEXT
            )
        """)
        await db.commit()


@app.route("/")
async def index():
    return {"webhook": "rem-aio-topgg", "status": "ok"}


@app.route("/health")
async def health():
    return {"status": "ok"}, 200


async def get_user_avatar(user_id: str) -> str | None:
    if not BOT_TOKEN:
        return None
    url = f"https://discord.com/api/v10/users/{user_id}"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return None
            user_data = await response.json()
            avatar = user_data.get("avatar")
            if avatar:
                return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png"
            default_avatar_id = int(user_id) % 5
            return f"https://cdn.discordapp.com/embed/avatars/{default_avatar_id}.png"


@app.route("/topgg/", methods=["POST"])
async def topgg():
    if not TOPGG_AUTH or not TOPGG_VOTE_WEBHOOK or not BOT_TOKEN:
        log.error("Top.gg webhook is not fully configured in environment variables.")
        return {"error": "Webhook not configured"}, 503

    authorization = request.headers.get("Authorization")
    if authorization != TOPGG_AUTH:
        return {"error": "401 Unauthorized"}, 401

    data = json.loads(await request.data)
    user_id = str(data["user"])
    avatar_url = await get_user_avatar(user_id)

    if not avatar_url:
        return {"error": "Failed to fetch avatar"}, 500

    current_time = datetime.datetime.now(datetime.timezone.utc)

    async with aiosqlite.connect("votes.db") as db:
        cursor = await db.execute(
            "SELECT total_votes, streak, last_vote_time FROM votes WHERE user_id = ?",
            (user_id,),
        )
        user_data = await cursor.fetchone()
        await cursor.close()

        if user_data:
            total_votes, streak, last_vote_time = user_data
            last_vote_time = datetime.datetime.fromisoformat(last_vote_time)
            time_difference = (current_time - last_vote_time).total_seconds()
            streak = streak + 1 if time_difference <= 43200 else 1
        else:
            total_votes = 0
            streak = 1

        total_votes += 1
        await db.execute(
            """
            INSERT INTO votes (user_id, total_votes, streak, last_vote_time)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                total_votes = excluded.total_votes,
                streak = excluded.streak,
                last_vote_time = excluded.last_vote_time
            """,
            (user_id, total_votes, streak, current_time.isoformat()),
        )
        await db.commit()

    timestamp = (current_time + datetime.timedelta(hours=12)).timestamp()
    india_tz = pytz.timezone("Asia/Kolkata")
    footer_time = current_time.astimezone(india_tz).strftime("%d/%m/%Y %I:%M %p")

    webhook_data = {
        "username": "REM ALL IN ONE BOT",
        "content": f"<@{user_id}> voted for <@{TOPGG_BOT_ID}>!",
        "embeds": [
            {
                "description": (
                    f"**[Voted REM ALL IN ONE BOT](https://top.gg/bot/{TOPGG_BOT_ID})**\n"
                    "Thank you for voting on Top.gg!"
                ),
                "fields": [
                    {"name": "Time left to vote again:", "value": f"<t:{int(timestamp)}:R>\n", "inline": True},
                    {"name": "Total votes:", "value": f"{total_votes}", "inline": True},
                    {"name": "Current Streak:", "value": f"{streak}", "inline": True},
                ],
                "footer": {
                    "text": f"Voter ID: {user_id} | REM ALL IN ONE BOT | {footer_time}",
                },
                "thumbnail": {"url": avatar_url},
                "color": 0xFF0000,
            }
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(TOPGG_VOTE_WEBHOOK, json=webhook_data) as response:
            if response.status >= 400:
                log.error("Vote webhook failed with status %s", response.status)
                return {"error": "Failed to post vote webhook"}, 502

    return {"message": "Vote registered successfully!"}