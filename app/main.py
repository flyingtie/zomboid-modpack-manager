import logging
import questionary
import time

from pydantic import AnyUrl
from pathlib import Path
from typing import Generator, Optional

from app.core.models import LocalMod, ExportMod, ModpackManifest
from app.models import GoogleDriveMod
from app.loader import load_uploaded_mods, save_uploaded_mods
from app import google_drive
from app.core.manager import get_missing_mods
from app.core.utils.utils import (
    find_mods,
    make_session, 
    delete_dir, 
    download_file, 
    extract_archive,
    make_archive,
    delete_file,
    get_cached_local_mods,
    cache_local_mods
)


logger = logging.getLogger(__name__)


class ManifestSourceNotAssigned(Exception):
    ...


def export_modpack(dest: Path):
    uploaded_mods = load_uploaded_mods()
    
    export_mods = list()
    for mod in uploaded_mods:
        export_mods.append(
            ExportMod(
                name=mod.name,
                mod_id=mod.mod_id,
                mod_hash=mod.mod_hash,
                url=mod.file_info.url
            )
        )
    
    path = dest / f"export_{time.time()}.json"
    
    with path.open("w", encoding="utf-8") as f:
        f.write(ModpackManifest(export_mods).model_dump_json(indent=4))
    

def get_modpack_manifest(url: AnyUrl) -> ModpackManifest:
    with make_session() as session:
        resp = session.get(url)
    return ModpackManifest.model_validate_json(resp.content)


def get_modpack_manifest_from_file(path: Path):
    if not path.exists():
        raise FileNotFoundError
    
    with path.open("r", encoding="utf-8") as f:
        return ModpackManifest.model_validate_json(f.read())
    

def update_modpack(mods_folder: Path, manifest_url: AnyUrl = None, manifest_path: Path = None): # TODO: Перенести сканирование модов на генератор
    if manifest_url: 
        manifest = get_modpack_manifest(manifest_url)
    elif manifest_path: 
        manifest = get_modpack_manifest_from_file(manifest_path)
    else:
        raise ManifestSourceNotAssigned
    
    do_scan = True
    if local_mods := get_cached_local_mods(mods_folder):
        if not questionary.confirm("do re-scan?").ask():
            do_scan = False
    if do_scan:
        local_mods = find_mods(mods_folder, only_enabled=True)
        cache_local_mods(mods_folder, local_mods)

    with make_session() as session:
        for export_mod, local_mod in get_missing_mods(manifest.mods, local_mods):
            if local_mod:
                logger.info(f"{local_mod.mod_id} is bad")
                delete_dir(local_mod.path)
            else:
                logger.info(f"{export_mod.mod_id} is missing")
                
            mod_path = download_file(export_mod.url, mods_folder, session)
            extract_archive(mod_path)
            
            logger.info(f"{export_mod.mod_id} downloaded")            


def upload_modpack(mods_folder: Path, client_secrets_path: Path, folder_id: str = None):
    found_mods = find_mods(mods_folder, only_enabled=True)
    
    if not (uploaded_mods := load_uploaded_mods()):
        uploaded_mods = list()
        
    gauth = google_drive.auth(client_secrets_path)
    
    with save_uploaded_mods() as save:
        
        for mod in found_mods:
            upload_mod = True
            
            for upld_mod in uploaded_mods: 
                if mod.mod_id != upld_mod.mod_id:
                    continue
                
                if mod.mod_hash != upld_mod.mod_hash:
                    google_drive.delete_googledrive_file(upld_mod.file_info.fileid, gauth)
                    
                    uploaded_mods.remove(upld_mod)
                    
                    save(uploaded_mods)
                    
                    break
                
                upload_mod = False
                
                break
            
            if not upload_mod:
                continue
            
            path_to_archive = make_archive(mod.path)
            
            file_info = google_drive.upload_file(
                path=path_to_archive, 
                auth=gauth, 
                folder_id=folder_id
            )
            
            delete_file(path_to_archive)
            
            uploaded_mod = GoogleDriveMod(
                name=mod.name,
                mod_id=mod.mod_id,
                mod_hash=mod.mod_hash,
                file_info=file_info
            )
            
            uploaded_mods.append(uploaded_mod)
            
            save(uploaded_mods)




# TODO:
# Профили 
# Разделить на модули