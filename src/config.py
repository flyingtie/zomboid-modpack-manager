from pydantic import HttpUrl, BaseModel, ConfigDict, SecretStr
from pathlib import Path
from typing import Optional


class BaseSettings(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)
    
    mods_folder: Optional[Path] = None


class UpdaterSettings(BaseSettings):
    google_drive_token: SecretStr


class UploaderSettings(BaseSettings):
    manifest_url: Optional[HttpUrl] = None

    
