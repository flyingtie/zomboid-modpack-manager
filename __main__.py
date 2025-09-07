import logging
import click

from app.cli.commands import update_mods
from app.loader import save_settings, load_settings

from pydantic import AnyUrl
from pathlib import Path


logging.basicConfig(level=logging.INFO)

def run():
    settings = load_settings()
    mods_folder = click.prompt("Path to mods", default=settings.mods_folder, type=Path)
    manifest_url = click.prompt("Manifest URL", default=settings.manifest_url, type=AnyUrl)
    update_mods(mods_folder, manifest_url)
    save_settings(settings)

if __name__ == "__main__":
    run()