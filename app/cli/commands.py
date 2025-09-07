import click

from pydantic import AnyUrl
from pathlib import Path

from app.core.updater import update


click.command()
click.argument("mods_folder", type=click.Path(exists=True))
click.argument("manifest_url", type=AnyUrl)
def update_mods(mods_folder: Path, manifest_url: AnyUrl):
    update(mods_folder, manifest_url)
          
click.command()
def generate_manifest():
    pass