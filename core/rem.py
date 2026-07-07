from __future__ import annotations

import asyncio
import logging
import typing
from typing import List

import aiohttp
import discord
from discord.ext import commands

from utils import console, getConfig, updateConfig
from utils.config import OWNER_IDS
from utils.database import connect
from utils.discord_compat import install_neutral_embed_policy
from utils.migrations import run_startup_migrations

from .Context import Context

install_neutral_embed_policy()

log = logging.getLogger(__name__)

extensions: List[str] = [
    "cogs"
]


class Rem(commands.AutoShardedBot):

    def __init__(self, *arg, **kwargs):
        intents = discord.Intents.all()
        intents.presences = True
        intents.members = True
        self.session: aiohttp.ClientSession | None = None
        self._synced_app_commands = False
        super().__init__(
            command_prefix=self.get_prefix,
            case_insensitive=True,
            intents=intents,
            status=discord.Status.online,
            strip_after_prefix=True,
            owner_ids=OWNER_IDS,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, replied_user=False, roles=False
            ),
            shard_count=2,
        )

    async def setup_hook(self):
        await run_startup_migrations()
        self.session = aiohttp.ClientSession()
        await self.load_extensions()

    async def load_extensions(self):
        timer = console.LoadTimer("EXT")
        console.section("Loading extensions")
        for extension in extensions:
            try:
                await self.load_extension(extension)
                console.success(f"Loaded {extension}")
                log.info("Loaded extension: %s", extension)
            except Exception as e:
                console.error(f"Failed to load {extension}: {e}")
                log.exception("Failed to load extension %s", extension)
                raise
        timer.finish(f"Loaded {len(extensions)} extension(s)")

    async def _close_cog_resources(self) -> None:
        for cog in self.cogs.values():
            session = getattr(cog, "aiohttp", None)
            if session is not None and hasattr(session, "closed") and not session.closed:
                try:
                    await session.close()
                except Exception:
                    log.exception("Failed to close aiohttp session for %s", type(cog).__name__)

    async def close(self) -> None:
        if self.is_closed():
            return

        await self._close_cog_resources()

        if self.session and not self.session.closed:
            try:
                await self.session.close()
            except Exception:
                log.exception("Failed to close aiohttp session")
            finally:
                self.session = None

        try:
            from db._db import Database
            await Database().close()
        except Exception:
            log.exception("Failed to close shared database connection")

        try:
            await super().close()
        except AttributeError as exc:
            if "_AutoShardedClient__queue" not in str(exc):
                raise
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Error during Discord client shutdown")

    async def on_connect(self):
        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.playing, name=">help | >invite"),
        )

    async def send_raw(
        self, channel_id: int, content: str, **kwargs
    ) -> typing.Optional[discord.Message]:
        return await self.http.send_message(channel_id, content, **kwargs)

    async def invoke_help_command(self, ctx: Context) -> None:
        return await ctx.send_help(ctx.command)

    async def fetch_message_by_channel(
        self, channel: discord.TextChannel, messageID: int
    ) -> typing.Optional[discord.Message]:
        async for msg in channel.history(
            limit=1,
            before=discord.Object(messageID + 1),
            after=discord.Object(messageID - 1),
        ):
            return msg

    async def get_prefix(self, message: discord.Message):
        async with connect("np.db") as db:
            async with db.execute("SELECT id FROM np WHERE id = ?", (message.author.id,)) as cursor:
                row = await cursor.fetchone()

        if message.guild:
            data = await getConfig(message.guild.id)
            prefix = data["prefix"]
            if row:
                return commands.when_mentioned_or(prefix, "")(self, message)
            return commands.when_mentioned_or(prefix)(self, message)

        if row:
            return commands.when_mentioned_or(">", "")(self, message)
        return commands.when_mentioned_or("")(self, message)

    async def on_message_edit(self, before, after):
        ctx: Context = await self.get_context(after, cls=Context)
        if before.content != after.content:
            if after.guild is None or after.author.bot:
                return
            if ctx.command is None:
                return
            if isinstance(ctx.channel, discord.Thread) and ctx.channel.type == discord.ChannelType.public_thread:
                return
            await self.invoke(ctx)


def setup_bot():
    intents = discord.Intents.all()
    bot = Rem(intents=intents)
    return bot