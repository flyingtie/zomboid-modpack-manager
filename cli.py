import click
import questionary

from pydantic import AnyUrl
from pathlib import Path
from click_option_group import optgroup, MutuallyExclusiveOptionGroup

from app.core.manager import update, upload
from app.loader import load_settings, save_settings


settings = load_settings()

def prompt_path(prompt: str = None, default: str = None, only_directories: bool = True):
    
    def _callback(ctx, param, value):
        return questionary.path(message=str(prompt), default=str(default), only_directories=only_directories).ask()

    return _callback

@click.group()
def cli():
    pass

@cli.command("update-modpack")
@click.option(
    "--mods-folder", 
    callback=prompt_path("Path to Project Zomboid mods folder", settings.mods_folder, True), 
    type=click.Path(exists=True), 
    help="Path to mods folder",
    is_eager=True
)
@optgroup.group(cls=MutuallyExclusiveOptionGroup)
@optgroup.option("--manifest-url", type=AnyUrl, help="URL to manifest file")
@optgroup.option("--manifest-path", type=Path, help="Path to manifest file")
def update_modpack(mods_folder: Path, manifest_url: AnyUrl, manifest_path: Path):
    """Updates modpack"""
    
    if not (manifest_url and manifest_path):
        choice = questionary.select("Select the manifest source", choices=["url", "path"]).ask()
        
        if choice == "url":
            manifest_url = questionary.text("Enter manifest URL", default=settings.modpack_manifest_url).ask()
        elif choice == "path":
            manifest_path = questionary.path("Enter manifest Path", default=settings.modpack_manifest_path).ask()
        
    settings.mods_folder = mods_folder
    settings.modpack_manifest_url = manifest_url
    settings.modpack_manifest_path = manifest_path
    
    # update(mods_folder, manifest_url, manifest_path)
    
    # save_settings(settings)
    
# @cli.command("upload-modpack")
# @click.option("--folder-id", "-fid", prompt="", default=settings.)
# def upload_modpack(folder_id):
#     """Uploads modpack to google drive"""
    
#     pass #TODO
    

if __name__ == "__main__":
    cli()
    
# TODO:
# Добавить прогресс бар