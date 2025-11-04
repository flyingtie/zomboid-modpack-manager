import json
import os

from platformdirs import user_data_dir
from pathlib import Path
from contextlib import contextmanager

from app.models import UploadCache, CliCache, GoogleDriveMod


DATA_PATH = Path(user_data_dir()) / "ZomboidModpackManager"
CONFIG_PATH = DATA_PATH / "config.json"
UPLOAD_CACHE_PATH = DATA_PATH / "uploadcache.json"
GOOGLE_CREDS_PATH = DATA_PATH / "creds.json"


def save_cli_cache(settings: CliCache):
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        f.write(settings.model_dump_json(indent=4))


def load_cli_cache() -> CliCache:
    if not DATA_PATH.exists():
        DATA_PATH.mkdir(parents=True)   
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r") as f:
            data = json.loads(f.read())
        return CliCache.model_validate(data)
    return CliCache()


@contextmanager
def save_uploaded_mods():
    with UPLOAD_CACHE_PATH.open("w", encoding="utf-8") as f:
        upld_mods: list[GoogleDriveMod] = None
        
        def _save(uploaded_mods: list[GoogleDriveMod]):
            nonlocal upld_mods
            upld_mods = uploaded_mods
            
        try:
            yield _save
        finally:
            upload_cache = UploadCache(upld_mods)
            f.write(upload_cache.model_dump_json(indent=4))


def load_uploaded_mods() -> list[GoogleDriveMod] | None:
    if not UPLOAD_CACHE_PATH.exists():
        return None
    with UPLOAD_CACHE_PATH.open("r", encoding="utf-8") as f:
        data = json.loads(f.read())
        return UploadCache.model_validate(data).mods
    
        