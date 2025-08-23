import os
import hashlib
import json
import aiohttp
from datetime import datetime
from loguru import logger

from config import settings


class Manifest:
    def __init__(self):
        pass

    @classmethod
    def __sha256_file(cls, path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(settings.chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()

    def generate(self):
        logger.info("Generating manifest.json...")
        mods = {}
        for fname in os.listdir(self.mods_folder):
            if fname.endswith(".zip"):
                path = os.path.join(self.mods_folder, fname)
                file_hash = self.sha256_file(path)
                url = self.drive_links.get(fname, "")
                mods[fname] = {"hash": file_hash, "url": url}
                logger.info(f"{fname} → {file_hash[:12]}...")

        manifest = {
            "version": datetime.now().strftime("%Y.%m.%d_%H%M"),
            "mods": mods,
        }

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.success(f"manifest.json создан → {self.output_file}")
       
    # def 
    #            async with aiohttp.ClientSession() as session:
    #         async with session.get(settings) as resp:
    #             manifest = await resp.json()

    #         tasks = []
    #         for fname, meta in manifest["mods"].items():
    #             tasks.append(self.process_mod(session, fname, meta))

    #         await asyncio.gather(*tasks)


