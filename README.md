<p align="center">
  <img src="remaio.png" alt="REM ALL IN ONE BOT" width="100%">
</p>

# REM ALL IN ONE BOT

All-in-one Discord bot for moderation, security, music, tickets, giveaways, utilities, games, welcome systems, logging, and server management — with clean Components V2 panels.

## Quick Start

```bash
pip install -r requirements.txt
copy .env.example .env
python rem.py
```

Set `TOKEN` and `OWNER_IDS` in `.env` before starting.

## Features

| Area | Highlights |
| --- | --- |
| **Panels** | Components V2 help, utility, and music UIs |
| **Music** | Lavalink / Wavelink playback with player controls |
| **Moderation** | Ban, kick, timeout, warn, lock, hide, role, purge, snipe |
| **Security** | Antinuke listeners + automod (spam, caps, links, invites) |
| **Server** | Tickets, giveaways, logging, welcome, autorole, custom roles |
| **Utility** | Stats, botinfo, AFK, translate, QR, emoji sync, maps |
| **Games** | Chess, RPS, Wordle, 2048, blackjack, slots, and more |
| **Admin** | No-prefix, global actions, owner tools, emergency controls |

## Requirements

- Python **3.11+**
- Discord bot token with **Message Content** intent
- **Server Members** intent (moderation, welcome, autorole, antinuke)
- **Lavalink** node for music (optional but recommended)

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create your environment file:

```bash
copy .env.example .env
```

3. Fill in `.env` (never commit this file):

```env
TOKEN=your_discord_bot_token
BOT_NAME=REM ALL IN ONE BOT
OWNER_IDS=123456789012345678
LAVALINK_ENABLED=true
LAVALINK_URI=http://127.0.0.1:2333
LAVALINK_PASSWORD=youshallnotpass
```

4. Run the bot:

```bash
python rem.py
```

On startup you should see the REM console banner, cog load lines, shard connections, and a ready summary.

## Environment

| Key | Required | Purpose |
| --- | --- | --- |
| `TOKEN` | Yes | Discord bot token |
| `OWNER_IDS` | Yes | Comma-separated owner user IDs |
| `BOT_NAME` | No | Display name in panels (default: REM ALL IN ONE BOT) |
| `BYPASS_IDS` | No | Users that bypass security checks (defaults to owners) |
| `COMMAND_LOG_WEBHOOK_URL` | No | Webhook for command usage logs |
| `LAVALINK_URI` / `LAVALINK_PASSWORD` | For music | Lavalink node connection |
| `GUILD_JOIN_LOG_CHANNEL_ID` | No | Channel ID for guild join logs |
| `GUILD_LEAVE_LOG_CHANNEL_ID` | No | Channel ID for guild leave logs |
| `OPENAI_API_KEY` | No | Optional AI/chat features |
| `SPOTIFY_CLIENT_ID` / `SECRET` | No | Optional Spotify link resolution |
| `GIPHY_TOKEN`, `PEXELS_API_KEY`, etc. | No | Optional fun/utility API keys |

See `.env.example` for the full list.

## Permissions

Invite the bot with **Administrator**, or configure these permissions manually:

- Manage Server, Roles, Channels, Messages
- Ban / Kick / Moderate Members, View Audit Log
- Send Messages, Embed Links, Attach Files, Use External Emojis
- Connect, Speak (for music)

Setup commands (antinuke, automod, tickets, emergency, etc.) are restricted to owners, bypass users, server owners, or administrators.

## Music

Configure Lavalink in `.env`:

```env
LAVALINK_ENABLED=true
LAVALINK_IDENTIFIER=main
LAVALINK_URI=http://your-host:2333
LAVALINK_PASSWORD=your_password
LAVALINK_PRECHECK=true
```

Restart `python rem.py` fully after music or code changes — hot reload will not update a running process.

## Project Layout

```text
rem.py              Entry point
core/rem.py         Rem bot class (AutoShardedBot)
core/Context.py     Custom command context
cogs/commands/      User-facing command cogs
cogs/rem/           Help category panel cogs
cogs/moderation/    Moderation action cogs
cogs/antinuke/      Antinuke event listeners
cogs/automod/       Automod event listeners
cogs/events/        Guild & error event listeners
utils/              Config, database, console, UI helpers
db/                 Per-feature SQLite databases
data/               Runtime assets and generated media
games/              Standalone game engines
```

## Development

Syntax check:

```bash
python -m compileall rem.py cogs utils core
```

Health endpoint (when keep-alive is enabled):

```text
GET http://127.0.0.1:8080/health
```

## Security

- Regenerate your bot token if it is ever exposed.
- Keep `.env`, databases, and logs out of git.
- Limit `OWNER_IDS` and `BYPASS_IDS` to trusted users.
- Restart after permission, security, or environment changes.

## Logs

Console output uses the REM anime-style logger. Full debug logs are also written to:

```text
logs/rem.log
```

## License

MIT License — Copyright (c) 2026 **devrock**

See [LICENSE](LICENSE) for full terms.

## Credits

**REM ALL IN ONE BOT** — created by **devrock**