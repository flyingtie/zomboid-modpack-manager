from .config import Settings, CONFIG_PATH

import tomllib


if CONFIG_PATH.exists():
    with CONFIG_PATH.open("rb", encoding="utf-8") as f:
        data = tomllib.load(f)
    settings = Settings.model_validate(data)
else:
    settings = Settings()
        



