import os
import sys
from dotenv import load_dotenv
import logging
from src.settings import *

load_dotenv()

CACHE_DIR.mkdir(exist_ok=True)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

file_handler = logging.FileHandler(BASE_DIR / "sierra.log", encoding='utf-8')
console_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.root.setLevel(logging.INFO)
logging.root.addHandler(file_handler)
logging.root.addHandler(console_handler)

config = {
    'DISCORD_BOT_TOKEN': os.getenv("DISCORD_BOT_TOKEN"),
    'NASA_API_KEY': os.getenv("NASA_API_KEY"),
    'CACHE_DIR': CACHE_DIR,
}

DISCORD_BOT_TOKEN = config['DISCORD_BOT_TOKEN']
NASA_API_KEY = config['NASA_API_KEY']