import checksumdir
import xxhash
import logging
import shutil
import requests

from pathlib import Path
from pydantic import HttpUrl
from email.message import EmailMessage
from collections.abc import Generator
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from app.core.models import LocalMod, RemoteMod


logger = logging.getLogger(__name__)

def scan_mods(path: Path) -> list[LocalMod]:
    mods = []
    
    for sub_dir in [x for x in path.iterdir() if x.is_dir()]:
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
        
        mod_hash = hashdir(sub_dir)
        
        mod = LocalMod(**info_dict, path=sub_dir, mod_hash=mod_hash)
        
        mods.append(mod)
        logger.info(f"{mod.mod_id} loaded")
    
    return mods

def extract_mod(path: Path):
    shutil.unpack_archive(path, extract_dir=path.parent)
    path.unlink()

def download_file(url: HttpUrl, destination: Path, session: requests.Session) -> Path:
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

def delete_mod(path: Path):
    if path.exists():
        shutil.rmtree(path)
    
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

def hashdir(path: Path) -> str:
    hashvalues = []
    
    for root, _, files in path.walk():
        for file in files:
            hashvalues.append(checksumdir._filehash(root / file, xxhash.xxh3_64))
    
    hashvalues.sort()
    
    return checksumdir._reduce_hash(hashvalues, xxhash.xxh3_64)