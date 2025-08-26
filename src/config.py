from platformdirs import user_data_dir
from pydantic import AnyUrl, BaseModel, ConfigDict
from pathlib import Path
from typing import Optional


DATA_DIR = Path(user_data_dir("ZomboidModsUpdater"))
CONFIG_PATH = DATA_DIR / "config.toml"

class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)
    
    manifest_url: Optional[AnyUrl] = None
    mods_folder: Optional[Path] = None