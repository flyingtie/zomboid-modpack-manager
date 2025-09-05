import logging

from pathlib import Path
from pydantic import HttpUrl

from models import Manifest, LocalMod, RemoteMod
from manifest import get_manifest
from utils import (
    scan_mods,
    make_session,
    get_missing_mods, 
    delete_mod, 
    download_file, 
    extract_mod
)


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