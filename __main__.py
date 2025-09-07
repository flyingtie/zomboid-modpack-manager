import logging
import click

from app.core.updater import update
from app.loader import save_settings, load_settings

from pydantic import AnyUrl
from pathlib import Path


logging.basicConfig(level=logging.INFO)

def run():
    settings = load_settings()
    mods_folder = settings.mods_folder = click.prompt("Path to mods", default=settings.mods_folder, type=Path)
    manifest_url = settings.manifest_url = click.prompt("Manifest URL", default=settings.manifest_url, type=AnyUrl)
    update(mods_folder, manifest_url)
    save_settings(settings)

if __name__ == "__main__":
    run()