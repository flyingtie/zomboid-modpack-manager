import click
import logging
import questionary

from pydantic import HttpUrl
from typing import Optional, Literal
from pathlib import Path
from click_option_group import optgroup, MutuallyExclusiveOptionGroup

from app.main import update_modpack, upload_modpack, export_modpack
from app.loader import load_cli_cache, save_cli_cache


logging.basicConfig(level=logging.INFO)

cli_cache = load_cli_cache()


def prompt_path(prompt: str = "", default: str = "", only_directories: bool = False):
    
    def _callback(ctx, param, value):
        if not value:
            return Path(questionary.path(
                message=str(prompt), 
                default=str(default), 
                only_directories=only_directories
            ).ask())

    return _callback


def empty_str_if_none(value: Optional[str]) -> Literal[""] | str:
    if not isinstance(value, (type(None), str)):
        raise TypeError(f"Expected {str} or {type(None)}, got {type(value)} instead")
    
    if value:
        return value
    return ""


@click.group()
def cli():
    pass


@cli.command("update")
@click.option(
    "--mods-folder", 
    callback=prompt_path("Path to mods folder:", cli_cache.mods_folder, True), 
    type=click.Path(exists=True), 
    help="Path to mods folder"
)
@optgroup.group(cls=MutuallyExclusiveOptionGroup)
@optgroup.option("--manifest-url", type=HttpUrl, help="Url to manifest file")
@optgroup.option("--manifest-path", type=Path, help="Path to manifest file")
def update(mods_folder: Path, manifest_url: HttpUrl, manifest_path: Path):
    """Updates modpack"""
    
    if not (manifest_url or manifest_path):
        choice = questionary.select(
            "Select the manifest source:", 
            choices=["url", "path"]
        ).ask()
        
        if choice == "url":
            manifest_url = questionary.text(
                "Enter manifest url:", 
                default=empty_str_if_none(str(cli_cache.modpack_manifest_url))
            ).ask()
        elif choice == "path":
            manifest_path = Path(questionary.path(
                "Enter manifest path:", 
                default=empty_str_if_none(str(cli_cache.modpack_manifest_path))
            ).ask())
        
    cli_cache.mods_folder = mods_folder
    cli_cache.modpack_manifest_url = manifest_url
    cli_cache.modpack_manifest_path = manifest_path
    
    update_modpack(mods_folder, manifest_url, manifest_path)
    
    save_cli_cache(cli_cache)
    
    
@cli.command("upload")
@click.option(
    "--mods-folder", 
    callback=prompt_path("Path to mods folder:", cli_cache.mods_folder, True), 
    type=click.Path(exists=True), 
    help="Path to mods folder"
)
@click.option(
    "--client-secrets-path", 
    callback=prompt_path("Path to client_secrets.json:"),
    type=click.Path(exists=True),
    help="Path to client_secrets.json"
)
@click.option("--folder-id", help="Google Drive folder id")
def upload(mods_folder: Path, client_secrets_path: Path, folder_id: Optional[str]):
    """Uploads modpack to google drive"""
    
    cli_cache.mods_folder = mods_folder
    
    upload_modpack(mods_folder, client_secrets_path, folder_id)
    
    save_cli_cache(cli_cache)


@cli.command("export")
@click.option(
    "--dest",
    callback=prompt_path("Specify where to save the export file:", only_directories=True),
    type=click.Path(exists=True),
    help="Export file destination"
)
def export(dest: Path):
    export_modpack(dest)


if __name__ == "__main__":
    cli()
    
# TODO:
# Добавить прогресс бар