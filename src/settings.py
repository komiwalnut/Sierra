import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"

NASA_API_BASE_URL = "https://eonet.gsfc.nasa.gov/api/v3"
STORM_BBOX = "110,27,155,0"
STORM_DAYS_LIMIT = 3
STORM_EVENT_LIMIT = 5

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
