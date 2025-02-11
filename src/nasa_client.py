import json
from pathlib import Path
import aiohttp
import logging
from src.config import config

logger = logging.getLogger(__name__)


class NASAClient:
    async def fetch_severe_storms(self):
        async with aiohttp.ClientSession() as session:
            url = "https://eonet.gsfc.nasa.gov/api/v3/events?source=JTWC&status=open&limit=5&days=3&bbox=110,27,155,0&category=severeStorms"
            headers = {"Authorization": f"Bearer {config.get('NASA_API_KEY')}"}
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("events", [])
                else:
                    return []