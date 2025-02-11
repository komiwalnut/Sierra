import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from src.config import config


class Cache:
    def __init__(self, cache_file: str = "guild_channel_cache.json"):
        self.cache_file = config["CACHE_DIR"] / cache_file
        self.cache_duration = timedelta(minutes=30)
        self._cache: Dict = self._load_cache()
        self._guild_channels: Dict = self._cache.get('guild_channels', {})

    def _load_cache(self) -> Dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'guild_channels': {}}
        return {'guild_channels': {}}

    def _save_cache(self):
        self._cache['guild_channels'] = self._guild_channels
        with open(self.cache_file, 'w') as f:
            json.dump(self._cache, f)

    def get(self, key: str) -> Optional[Dict]:
        if key in self._cache:
            data = self._cache[key]
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time <= self.cache_duration:
                return data['value']
        return None

    def set(self, key: str, value: Dict):
        self._cache[key] = {
            'timestamp': datetime.now().isoformat(),
            'value': value
        }
        self._save_cache()

    def get_weather_channel(self, guild_id: str) -> Optional[int]:
        return self._guild_channels.get(str(guild_id))

    def set_weather_channel(self, guild_id: str, channel_id: int):
        self._guild_channels[str(guild_id)] = channel_id
        self._save_cache()
