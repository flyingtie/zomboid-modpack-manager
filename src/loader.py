import json

from platformdirs import user_data_dir
from pathlib import Path

from config import BaseSettings, UpdaterSettings, UploaderSettings


DATA_DIR = Path(user_data_dir()) / "ZomboidModsUpdater"
UPDATER_DATA = DATA_DIR / "updater.json"
UPLOADER_DATA = DATA_DIR / "uploader.json"

def save_data(path: Path, settings: BaseSettings):
    with path.open("w") as file:
        file.write(settings.model_dump_json(indent=4))

def request_updater_settings():
    pass

def request_uploader_settings():
    pass

def request_common_settings():
    mods_folder = input("Path to mods: ")
    
def load_updater():
    load(UPDATER_DATA, UpdaterSettings)
    
def load_uploader():
    load(UPLOADER_DATA, UploaderSettings)

def load(data_file: Path, settings_class: BaseSettings):
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)   
    if data_file.exists():
        with data_file.open("rb") as file:
            data = json.load(file)
        settings = settings_class.model_validate(data)
    else:
        settings = request_settings()
        save_data(data_file, settings) 

