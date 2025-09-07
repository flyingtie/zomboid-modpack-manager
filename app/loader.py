import json

from platformdirs import user_data_dir
from pathlib import Path

from app.config import UpdaterSettings, BaseSettings


DATA_DIR = Path(user_data_dir()) / "ZomboidModsUpdater"
CONFIG_DATA = DATA_DIR / "config.json"

def save_settings(settings: BaseSettings):
    with CONFIG_DATA.open("w") as file:
        file.write(settings.model_dump_json(indent=4))

def load_settings():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)   
    if CONFIG_DATA.exists():
        with CONFIG_DATA.open("rb") as file:
            data = json.load(file)
        return UpdaterSettings.model_validate(data)
    return UpdaterSettings()

