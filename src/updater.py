import checksumdir
import requests
import shutil
import logging

from pathlib import Path
from pydantic import HttpUrl
from typing import Generator, Optional
from email.message import EmailMessage

from models import Manifest, LocalMod, RemoteMod
from manifest import get_manifest
from network import make_session


logger = logging.getLogger(__name__)

def update(manifest_url: HttpUrl, mods_folder: Path):
    manifest = get_manifest(manifest_url)
    local_mods = scan_mods(mods_folder)
    sync_mods(mods_folder, manifest.mods, local_mods)

def sync_mods(path: Path, remote_mods: list[RemoteMod], local_mods: list[LocalMod]):
    with make_session() as session:
        for remote_mod, local_mod in get_missing_mods(remote_mods, local_mods):
            if local_mod:
                delete_mod(local_mod.path)
            mod_path = download_file(remote_mod.mod_url, path, session)
            extract_mod(mod_path)
            
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
        
        mod_hash = checksumdir.dirhash(sub_dir, hashfunc="sha256")
        
        mod = LocalMod(**info_dict, path=sub_dir, mod_hash=mod_hash)
        
        mods.append(mod)
        logger.info(f"{mod.mod_id} found")
    
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
                

            