import logging
from src.bot import WeatherBot
from src.config import DISCORD_BOT_TOKEN

logger = logging.getLogger(__name__)


def main():
    if not DISCORD_BOT_TOKEN:
        logger.error("Discord bot token not found")
        return

    bot = WeatherBot()
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.exception("Failed to run bot.", e)


if __name__ == "__main__":
    main()
