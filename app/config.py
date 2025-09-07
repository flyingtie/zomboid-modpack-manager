from pydantic import HttpUrl, BaseModel, ConfigDict, SecretStr
from pathlib import Path
from typing import Optional


class BaseSettings(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)
    
    mods_folder: Optional[Path] = None

class UpdaterSettings(BaseSettings):
    manifest_url: Optional[HttpUrl] = None

    
