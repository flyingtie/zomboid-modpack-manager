import logging

from pathlib import Path
from pydantic import HttpUrl

from app.core.manifest import get_manifest
from app.core.utils import (
    scan_mods,
    make_session,
    get_missing_mods, 
    delete_mod, 
    download_file, 
    extract_mod
)


def update(mods_folder: Path, manifest_url: HttpUrl):
    manifest = get_manifest(manifest_url)
    local_mods = scan_mods(mods_folder)
    
    with make_session() as session:
        for remote_mod, local_mod in get_missing_mods(manifest.mods, local_mods):
            if local_mod:
                delete_mod(local_mod.path)
            mod_path = download_file(remote_mod.mod_url, mods_folder, session)
            extract_mod(mod_path)