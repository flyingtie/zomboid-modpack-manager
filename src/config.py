from pydantic import HttpUrl, BaseModel, ConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)
    
    manifest_url: Optional[HttpUrl] = None
    mods_folder: Optional[Path] = None