import json
import checksumdir
import xxhash
import logging
import shutil
import requests
import re

from pathlib import Path
from pydantic import HttpUrl
from email.message import EmailMessage
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from app.core.models import LocalMod, ExportMod


logger = logging.getLogger(__name__)


def get_enabled_mods(path: Path) -> list[str|None]:
    file_path = path / "default.txt"
    
    if not file_path.exists():
        return []
    with file_path.open("r", encoding="utf-8") as file:
        return re.findall(r"mod = (.+?),", file.read())
  
        
def find_mods(path: Path, only_enabled: bool = True) -> list[LocalMod]:
    mods = []
    
    if only_enabled:
        enabled_mods = get_enabled_mods(path)
    
    for sub_dir in [x for x in path.iterdir() if x.is_dir()]:
        if not (mod_info := sub_dir / "mod.info").exists():
            continue
        with mod_info.open("r", encoding="utf-8") as f:
            info_dict = {}
            for line in f.readlines():
                if "=" not in line:
                    continue
                key, value = line.split("=", maxsplit=1)
                if key not in ("id", "name"):
                    continue
                info_dict[key.strip()] = value.strip()
        
        if only_enabled:
            if info_dict["id"] not in enabled_mods:
                continue
            
        mod_hash = hashdir(sub_dir)
        
        mod = LocalMod(**info_dict, path=sub_dir, mod_hash=mod_hash)
        
        mods.append(mod)
        
        logger.info(f"{mod.id} found")
    
    return mods


def extract_archive(path: Path):
    shutil.unpack_archive(path, extract_dir=path.parent)
    
    delete_file(path)
   
    
def make_archive(path: Path) -> Path:
    """Сreates archive

    Args:
        path (Path)

    Returns:
        str: Path to archive
    """
    
    return Path(
        shutil.make_archive(
            base_name=path, 
            format="zip", 
            root_dir=path.parent, 
            base_dir=path.name
        )
    )


def download_file(url: HttpUrl, destination: Path, session: requests.Session) -> Path:
    with session.get(url, stream=True) as r:
        r.raise_for_status()

        msg = EmailMessage()
        msg["Content-Disposition"] = r.headers["Content-Disposition"]
        filename = msg.get_filename()
        
        path = destination / filename
        
        with open(path, "wb") as file:
            file.write(r.content)
    return path


def delete_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
   
        
def delete_file(path: Path):
    path.unlink(missing_ok=True)


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
        
# TODO: 
# Разделить на модули