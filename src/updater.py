import os
import hashlib
import checksumdir
import requests
import pathlib
import json
import shutil

from loguru import logger
from pathlib import Path
from pydantic import AnyUrl
from typing import Generator, Optional, Union, Iterator
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from email.message import EmailMessage

from src.models import Manifest, LocalMod, RemoteMod
from src.config_loader import settings, CONFIG_PATH


class Updater:
 
    def run(self):
        self.request_settings()
        self.save_config()
        self.update()
    
    def update(self):
        manifest = self.get_manifest()
        local_mods = self.scan_mods()
        self.sync_mods(manifest.mods, local_mods)
    
    def sync_mods(self, remote_mods: list[RemoteMod], local_mods: list[LocalMod]):
        with requests.Session() as session:
            for remote_mod, local_mod in self.get_missing_mods(remote_mods, local_mods):
                if local_mod:
                    self.delete_mod(local_mod.path)
                mod_path = self.download_file(remote_mod.mod_url, settings.mods_folder, session)
                self.extract_mod(mod_path)
    
    @staticmethod
    def get_manifest() -> Manifest:
        with requests.Session() as session:
            resp = session.get(settings.manifest_url)
        return Manifest.model_validate_json(resp.content)
    
    @staticmethod    
    def scan_mods() -> list[LocalMod]:
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
                    if key not in ("id", "name"):
                        continue
                    info_dict[key.strip()] = value.strip()
            
            mod_hash = checksumdir.dirhash(sub_dir, hashfunc="sha256")
            
            mod = LocalMod(**info_dict, path=sub_dir, mod_hash=mod_hash)
            
            mods.append(mod)
            logger.info(f"{mod.mod_id} found")
        
        return mods
    
    @staticmethod
    def extract_mod(path: Path):
        shutil.unpack_archive(path, extract_dir=path.parent)
        path.unlink()
    
    @staticmethod
    def download_file(url: AnyUrl, destination: Path, session: requests.Session) -> Path:
        with session.get(url, stream=True) as r:
            r.raise_for_status()

            msg = EmailMessage()
            msg["Content-Disposition"] = r.headers["Content-Disposition"]
            filename = msg.get_filename()
            
            path = destination / filename
            
            with open(path, "wb") as file:
                file.write(r.content)
        logger.info(f"{filename} downloaded") 
        return path
    
    @staticmethod
    def make_session() -> requests.Session:
        session = requests.Session()
        
        retries = Retry(
            total=5,
            connect=5,      
            read=5,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(["HEAD","GET"])
        )
        
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))
        
        return session
    
    @staticmethod
    def delete_mod(path: Path):
        if path.exists():
            shutil.rmtree(path)
        
    @staticmethod    
    def get_missing_mods(remote_mods: list[RemoteMod], local_mods: list[LocalMod]) -> Generator[tuple[RemoteMod, Optional[LocalMod]], None, None]:
        for remote_mod in remote_mods:
            is_missing = True
            
            for local_mod in local_mods:
                if remote_mod.mod_id != local_mod.mod_id:
                    continue
                if remote_mod.mod_hash == local_mod.mod_hash: 
                    is_missing = False
                    break
                is_missing = False
                yield remote_mod, local_mod
                break
            
            if is_missing:
                yield remote_mod, None        
                  
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