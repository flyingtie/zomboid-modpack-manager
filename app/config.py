import os

from pydantic import HttpUrl, BaseModel, ConfigDict, SecretStr
from pathlib import Path
from typing import Optional


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)
    
    mods_folder: Optional[Path] = _ if (_ := os.path.expanduser("~") / Path("Zomboid/mods")).exists() else None

    modpack_manifest_url: Optional[HttpUrl] = None
    
    modpack_manifest_path: Optional[Path] = None
