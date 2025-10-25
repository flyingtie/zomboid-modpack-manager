import logging
import questionary

from pathlib import Path
from pydantic import AnyUrl

from app.core.models import LocalMod, ExportMod, ModpackManifest
from app.core.utils.utils import (
    get_local_mods,
    make_session,
    get_missing_mods, 
    delete_mod, 
    download_file, 
    extract_mod,
    get_cached_local_mods,
    cache_local_mods
)


logger = logging.getLogger(__name__)

def get_modpack_manifest(url: AnyUrl) -> ModpackManifest:
    with make_session() as session:
        resp = session.get(url)
    return ModpackManifest.model_validate_json(resp.content)

def get_modpack_manifest_from_file(path: Path):
    if not path.exists():
        raise FileNotFoundError
    
    with path.open("r", encoding="utf-8") as f:
        return ModpackManifest.model_validate_json(f.read())

def generate_manifest(mods_folder: Path, mods_ids: list[str]) -> ModpackManifest:
    
    #TODO 
    return ModpackManifest()

def scan_mods(path) -> list[LocalMod]:
    do_scan = True
    
    if local_mods := get_cached_local_mods(path):
        if not questionary.confirm("do re-scan?").ask():
            do_scan = False
            
    if do_scan:
        local_mods = get_local_mods(path)
        cache_local_mods(path, local_mods)
        
    return local_mods

def update(mods_folder: Path, manifest_url: AnyUrl = None, manifest_path: Path = None): # TODO: Перенести сканирование модов на генератор
    if manifest_url: 
        get_modpack_manifest(manifest_url)
    if manifest_path: 
        get_modpack_manifest_from_file(manifest_path)
    
    local_mods = scan_mods(mods_folder)

    with make_session() as session:
        for export_mod, local_mod in get_missing_mods(manifest.mods, local_mods):
            if local_mod:
                logger.info(f"{local_mod.mod_id} is bad")
                delete_mod(local_mod.path)
            else:
                logger.info(f"{export_mod.mod_id} is missing")
                
            mod_path = download_file(export_mod.url, mods_folder, session)
            extract_mod(mod_path)
            
            logger.info(f"{export_mod.mod_id} downloaded")            

def upload(mods_folder: Path, only_enabled: bool = True):
    pass
    
# TODO:
# Профили для локальных модов и для аплоадера