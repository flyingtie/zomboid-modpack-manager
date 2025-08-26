import os
import hashlib
import checksumdir
import requests
import pathlib
import json

from loguru import logger
from pathlib import Path
from pydantic import AnyUrl

from src.models import Manifest, LocalMod, Mod
from src.config_loader import settings, CONFIG_PATH


class Updater:
 
    def run(self):
        self.request_settings()
        self.save_config()
        
    def get_manifest(self) -> Manifest:
        with requests.Session() as session:
            resp = session.get(settings.manifest_url)
        return Manifest.model_validate_json(resp.content)
        
    def scan_mods(self) -> list[LocalMod]:
        mods = []
        
        for sub_dir in [x for x in settings.mods_folder.iterdir() if x.is_dir()]:
            if not (mod_info := sub_dir / "mod.info").exists():
                continue
            with mod_info.open("r", encoding="utf-8") as file:
                info_dict = {}
                for line in file.readlines():
                    if "=" not in line:
                        continue
                    key, value = line.split("=", maxsplit=1)
                    if key not in ("name", "id"):
                        continue
                    info_dict[key.strip()] = value.strip()
            
            mod_hash = checksumdir.dirhash(sub_dir, hashfunc="sha256")
            
            mod = LocalMod(**info_dict, path=sub_dir, mod_hash=mod_hash)
            
            mods.append(mod)
        
        return mods
        
    
        
    def download_mods(self):
        pass
    
    @staticmethod
    def save_config():
        with CONFIG_PATH.open("w") as file:
            file.write(settings.model_dump_json(indent=4))
    
    @staticmethod
    def request_settings():
        if not settings.manifest_url:
            try:
                settings.manifest_url = input("Manifest URL: ")
            except ValueError:
                raise ValueError("Invalid Manifest URL")
                
        if not settings.mods_folder:
            settings.mods_folder = input("Path to mods: ")
            if not os.path.exists(settings.mods_folder):
                raise ValueError("Invalid path")