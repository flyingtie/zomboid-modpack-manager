from platformdirs import user_data_dir
from .config import Settings
from pathlib import Path

import json


DATA_DIR = Path(user_data_dir()) / "ZomboidModsUpdater"
CONFIG_PATH = DATA_DIR / "config.json"

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True)
if CONFIG_PATH.exists():
    with CONFIG_PATH.open("rb") as file:
        data = json.load(file)
    settings = Settings.model_validate(data)
else:
    settings = Settings()
        



