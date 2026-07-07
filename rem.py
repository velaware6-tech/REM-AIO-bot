from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import asyncio
import logging
import os
import signal
import traceback
from threading import Thread

import aiohttp
import discord
from discord.ext import commands
from flask import Flask

from core.axon import axon
from utils.config import COMMAND_LOG_IGNORE_IDS, COMMAND_LOG_WEBHOOK_URL, ENABLE_KEEP_ALIVE, LOG_LEVEL, PORT, TOKEN
from utils.startup import StartupError, validate_startup_config

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("rem")

client = axon()
app = Flask(__name__)
_shutdown_requested = False

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"


@client.event
async def on_ready():
    await client.wait_until_ready()

    log.info("Loaded and online as %s", client.user)
    log.info("Connected to %s guilds and %s cached users", len(client.guilds), len(client.users))

    if client._synced_app_commands:
        return

    try:
        synced = await client.tree.sync()
        client._synced_app_commands = True
        log.info("Synced %s prefix commands and %s slash commands", len(client.commands), len(synced))
    except Exception:
        log.exception("Slash command sync failed")


@client.event
async def on_command_completion(context: commands.Context) -> None:
    if not COMMAND_LOG_WEBHOOK_URL or context.author.id in COMMAND_LOG_IGNORE_IDS:
        return

    full_command_name = context.command.qualified_name
    executed_command = str(full_command_name.split("\n")[0])

    try:
        session = client.session or aiohttp.ClientSession()
        webhook = discord.Webhook.from_url(COMMAND_LOG_WEBHOOK_URL, session=session)
        avatar_url = context.author.display_avatar.url
        embed = discord.Embed(title="Command Executed")
        embed.set_author(name=str(context.author), icon_url=avatar_url)
        embed.add_field(name="Command", value=executed_command, inline=False)
        embed.add_field(name="User", value=f"{context.author} ({context.author.id})", inline=False)

        if context.guild is not None:
            embed.add_field(name="Guild", value=f"{context.guild.name} ({context.guild.id})", inline=False)
            embed.add_field(name="Channel", value=f"{context.channel} ({context.channel.id})", inline=False)

        embed.timestamp = discord.utils.utcnow()
        await webhook.send(embed=embed)

        if client.session is None:
            await session.close()
    except Exception as exc:
        log.warning("Command log webhook failed: %s", exc)
        traceback.print_exc()


@app.route("/")
def home():
    return "REM ALL IN ONE BOT is online"


@app.route("/health")
def health():
    from flask import jsonify
    return jsonify(status="ok", bot_ready=client.is_ready())


def run_keep_alive():
    app.run(host="0.0.0.0", port=PORT, use_reloader=False)


def keep_alive():
    if not ENABLE_KEEP_ALIVE:
        return
    server = Thread(target=run_keep_alive, daemon=True)
    server.start()


def _request_shutdown() -> None:
    global _shutdown_requested
    if _shutdown_requested:
        return
    _shutdown_requested = True
    log.info("Shutdown requested — closing bot connection...")
    asyncio.create_task(client.close())


def _register_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_shutdown)
        except (NotImplementedError, RuntimeError):
            pass


async def main():
    try:
        validate_startup_config()
    except StartupError as exc:
        log.error("%s", exc)
        raise SystemExit(1) from exc

    keep_alive()
    loop = asyncio.get_running_loop()
    _register_signal_handlers(loop)

    async with client:
        await client.load_extension("jishaku")
        await client.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Interrupted — bot stopped.")