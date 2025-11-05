import json
import os
import logging

from platformdirs import user_data_dir
from pydantic import ValidationError
from pathlib import Path
from contextlib import contextmanager
from json import JSONDecodeError

from app.models import UploadCache, CliCache, GoogleDriveMod


logger = logging.getLogger(__name__)


DATA_PATH = Path(user_data_dir()) / "ZomboidModpackManager"
CLI_CACHE_PATH = DATA_PATH / "clicache.json"
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