import json
import os
import logging

from platformdirs import user_data_dir
from pydantic import ValidationError
from pathlib import Path
from contextlib import contextmanager
from json import JSONDecodeError

from app.models import UploadCache, CliCache, GoogleDriveMod, LocalModsCache, LocalMod


logger = logging.getLogger(__name__)


DATA_PATH = Path(user_data_dir()) / "ZomboidModpackManager"
CLI_CACHE_PATH = DATA_PATH / "clicache.json"
MODS_CACHE_PATH = DATA_PATH / "cache.json"
UPLOAD_CACHE_PATH = DATA_PATH / "uploadcache.json"
GOOGLE_CREDS_PATH = DATA_PATH / "creds.json"


if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)  


def save_cli_cache(settings: CliCache):
    with CLI_CACHE_PATH.open("w", encoding="utf-8") as f:
        f.write(settings.model_dump_json(indent=4))


def load_cli_cache() -> CliCache: 
    if CLI_CACHE_PATH.exists():
        with CLI_CACHE_PATH.open("r", encoding="utf-8") as f:
            try:
                return CliCache.model_validate_json(f.read())
            except ValidationError as ex:
                logger.warning(ex)
    return CliCache()


def save_uploaded_mods(uploaded_mods: list[GoogleDriveMod]):
    if not uploaded_mods:
        return
    
    upload_cache = UploadCache(mods=uploaded_mods)
    with UPLOAD_CACHE_PATH.open("w", encoding="utf-8") as f:
        f.write(upload_cache.model_dump_json(indent=4))


def load_uploaded_mods() -> list[GoogleDriveMod] | None:
    if not UPLOAD_CACHE_PATH.exists():
        return None
    with UPLOAD_CACHE_PATH.open("r", encoding="utf-8") as f:
        try:
            return UploadCache.model_validate_json(f.read()).mods
        except ValidationError as ex:
            logger.warning(ex)
    return None


def load_cached_local_mods() -> list[LocalMod] | None:
    if not MODS_CACHE_PATH.exists():
        return None
    
    with MODS_CACHE_PATH.open("rb") as f:
        cache = LocalModsCache.model_validate(json.load(f))
    
    return cache.mods


def save_local_mods_cache(local_mods: list[LocalMod]):
    with MODS_CACHE_PATH.open("w", encoding="utf-8") as f:
        f.write(LocalModsCache(mods=local_mods).model_dump_json())