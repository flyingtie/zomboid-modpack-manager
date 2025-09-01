import logging
import requests

from pydantic import HttpUrl
from pathlib import Path

from models import Manifest
from network import make_session


logger = logging.getLogger(__name__)

def get_manifest(manifest_url: HttpUrl) -> Manifest:
    with make_session() as session:
        resp = session.get(manifest_url)
    return Manifest.model_validate_json(resp.content)

def generate_manifest(mods_folder: Path) -> Manifest:
    pass

