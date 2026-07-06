import os

DEFAULT_OWNER_IDS = [767979794411028491, 912362112620331029, 1297508239029698695, 1010057368287068222]


def _csv_ints(name: str, default: list[int]) -> list[int]:
    raw = os.environ.get(name, "")
    if not raw.strip():
        return default

    values: list[int] = []
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part.isdigit():
            values.append(int(part))
    return values or default


TOKEN = os.environ.get("TOKEN")
NAME = os.environ.get("BOT_NAME", "REM ALL IN ONE BOT")
server = os.environ.get("SUPPORT_SERVER", "https://discord.com/invite/codexdev")
ch = os.environ.get("SUPPORT_CHANNEL", "https://discord.com/channels/699587669059174461/1271825678710476911")
OWNER_IDS = _csv_ints("OWNER_IDS", DEFAULT_OWNER_IDS)
BYPASS_IDS = _csv_ints("BYPASS_IDS", OWNER_IDS)
COMMAND_LOG_IGNORE_IDS = _csv_ints("COMMAND_LOG_IGNORE_IDS", OWNER_IDS[:1])
BotName = NAME
serverLink = server
