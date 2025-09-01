from platformdirs import user_data_dir
from .config import Settings
from pathlib import Path

import json


DATA_DIR = Path(user_data_dir()) / "ZomboidModsUpdater"
CONFIG_PATH = DATA_DIR / "config.json"

def save_config(settings: Settings):
    with CONFIG_PATH.open("w") as file:
        file.write(settings.model_dump_json(indent=4))

def request_settings() -> Settings:
    manifest_url = input("Manifest URL: ")
    mods_folder = input("Path to mods: ")
    
    return Settings(
        manifest_url=manifest_url,
        mods_folder=mods_folder
    )

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True)
if CONFIG_PATH.exists():
    with CONFIG_PATH.open("rb") as file:
        data = json.load(file)
    settings = Settings.model_validate(data)
else:
    settings = request_settings()
    save_config(settings)


