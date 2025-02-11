import os
from dotenv import load_dotenv
import logging
from src.settings import *

load_dotenv()

CACHE_DIR.mkdir(exist_ok=True)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(BASE_DIR / "sierra.log"),
        logging.StreamHandler()
    ]
)

config = {
    'DISCORD_BOT_TOKEN': os.getenv("DISCORD_BOT_TOKEN"),
    'NASA_API_KEY': os.getenv("NASA_API_KEY"),
    'CACHE_DIR': CACHE_DIR,
}

DISCORD_BOT_TOKEN = config['DISCORD_BOT_TOKEN']
NASA_API_KEY = config['NASA_API_KEY']