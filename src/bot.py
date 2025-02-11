import discord
from discord import app_commands
import logging
import asyncio
from datetime import datetime, time, timedelta
import pytz
from src.config import config
from src.nasa_client import NASAClient
from src.visualization import StormVisualizer
from src.cache import Cache

logger = logging.getLogger(__name__)


class WeatherBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.nasa_client = NASAClient()
        self.visualizer = StormVisualizer()
        self.cache = Cache()
        self.ph_timezone = pytz.timezone('Asia/Manila')

        @self.tree.command(name="weather", description="Get Philippines Weather Updates.")
        async def weather(interaction: discord.Interaction):
            await interaction.response.defer()
            logger.info(f"/weather command used in channel: {interaction.channel.name}")

            weather_channel = await self._get_or_create_weather_channel(interaction.guild)
            await self._send_weather_update(weather_channel, interaction.user)
            await interaction.followup.send(f"Weather update has been posted in {weather_channel.mention}")

    async def _get_or_create_weather_channel(self, guild: discord.Guild) -> discord.TextChannel:
        channel_id = self.cache.get_weather_channel(str(guild.id))
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                return channel

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        channel = await guild.create_text_channel(
            '🇵🇭-weather',
            topic="Philippine Weather Updates",
            overwrites=overwrites,
            reason="Created for weather updates (read-only for users, bot can send messages)"
        )
        self.cache.set_weather_channel(str(guild.id), channel.id)
        logger.info(f"Created new weather channel in guild {guild.name} (ID: {guild.id})")
        return channel

    async def _send_weather_update(self, channel: discord.TextChannel, user=None):
        events = await self.nasa_client.fetch_severe_storms()
        if events:
            image_path = await self.visualizer.plot_storm_path(events)

            mention = f"{user.mention} - " if user else ""
            if len(events) == 1:
                message_content = f"{mention}Weather Alert: {events[0]['title']}"
            else:
                storm_names = ", ".join(event['title'] for event in events)
                message_content = f"{mention}Weather Alert: Multiple storms detected ({storm_names})"

            if image_path:
                await channel.send(content=message_content, file=discord.File(image_path))
            else:
                await channel.send(content=f"{message_content} (No visualization available)")
        else:
            mention = f"{user.mention} - " if user else ""
            await channel.send(f"{mention}No weather updates available.")

    async def scheduled_weather_update(self):
        while True:
            try:
                now = datetime.now(self.ph_timezone)
                target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
                if now >= target_time:
                    target_time += timedelta(days=1)
                delta = (target_time - now).total_seconds()
                await asyncio.sleep(delta)
                for guild in self.guilds:
                    channel_id = self.cache.get_weather_channel(str(guild.id))
                    if channel_id:
                        channel = guild.get_channel(channel_id)
                        if channel:
                            logger.info(f"Sending scheduled weather update to {guild.name}")
                            await self._send_weather_update(channel)
                        else:
                            logger.warning(f"Weather channel not found in guild {guild.name}")
            except Exception as e:
                logger.error(f"Error in scheduled weather update: {e}")
                await asyncio.sleep(300)

    async def setup_hook(self):
        await self.tree.sync()
        logger.info("Synced commands globally")
        self.bg_task = self.loop.create_task(self.scheduled_weather_update())
        logger.info("Started scheduled weather updates task")

    async def close(self):
        if hasattr(self, 'bg_task'):
            self.bg_task.cancel()
        await super().close()


if __name__ == "__main__":
    discord_bot_token = config.get('DISCORD_BOT_TOKEN')
    if not discord_bot_token:
        logger.critical("Discord bot token not found. Check your config.")
    else:
        bot = WeatherBot()
        bot.run(discord_bot_token)
