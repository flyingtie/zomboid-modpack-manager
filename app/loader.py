import json
import os

from platformdirs import user_data_dir
from pathlib import Path

from app.config import Settings


DATA_DIR = Path(user_data_dir()) / "ZomboidModpackManager"
CONFIG_DATA = DATA_DIR / "config.json"

def save_settings(settings: Settings):
    with CONFIG_DATA.open("w") as file:
        file.write(settings.model_dump_json(indent=4))

def load_settings():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)   
    if CONFIG_DATA.exists():
        with CONFIG_DATA.open("rb") as file:
            data = json.load(file)
        return Settings.model_validate(data)
    return Settings()

#TODO: Сохранять настройки в папке с модами