import asyncio
import aiohttp

from loguru import logger

from src.config import settings
from src.app import App


async def run_async():
    app = App()
    app.update_mods()

if __name__ == "__main__":
    asyncio.run(run_async())
