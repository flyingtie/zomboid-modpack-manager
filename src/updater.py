import os
import hashlib
import asyncio
import aiohttp

from loguru import logger

from config import settings


class Updater:
    def __init__(self):
        pass

    def sha256_file(self, path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(settings.chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()

    async def download_file(self, session: aiohttp.ClientSession, url: str, path: str):
        async with session.get(url) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get('Content-Length', 0))
            downloaded = 0

            with open(path, "wb") as f:
                async for chunk in resp.content.iter_chunked(settings.chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    logger.debug(f"{os.path.basename(path)}: {downloaded}/{total} байт")

        logger.success(f"{os.path.basename(path)} скачан полностью!")

    async def process_mod(self, session: aiohttp.ClientSession, fname: str, meta: dict):
        url = meta["url"]
        expected_hash = meta["hash"]
        path = os.path.join(, fname)

        need_download = True
        if os.path.exists(path):
            local_hash = self.sha256_file(path)
            if local_hash == expected_hash:
                logger.info(f"{fname} уже актуален")
                need_download = False
            else:
                logger.warning(f"{fname} устарел → обновляем")

        if need_download:
            logger.info(f"Скачиваем {fname}...")
            await self.download_file(session, url, path)
            # проверка хэша после скачивания
            new_hash = self.sha256_file(path)
            if new_hash != expected_hash:
                logger.error(f"{fname} скачан с ошибкой: хэш не совпадает!")
            else:
                logger.success(f"{fname} обновлён и проверен")

    async def get_manifest(self): 
        async with aiohttp.ClientSession() as session:
            async with session.get(settings) as resp:
                manifest = await resp.json()

            tasks = []
            for fname, meta in manifest["mods"].items():
                tasks.append(self.process_mod(session, fname, meta))

            await asyncio.gather(*tasks)