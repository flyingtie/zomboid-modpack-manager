import os

from pydantic import HttpUrl, BaseModel, ConfigDict, SecretStr
from pathlib import Path
from typing import Optional

from app.core.models import BaseMod, LocalMod


class CliCache(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)
    
    mods_folder: Optional[Path] = _ if (_ := os.path.expanduser("~") / Path("Zomboid/mods")).exists() else None

    modpack_manifest_url: Optional[HttpUrl] = None
    
    modpack_manifest_path: Optional[Path] = None

 
class GoogleDriveFileInfo(BaseModel):
    fileid: str
    filename: str
    url: str
    filesize: str
    folder_id: Optional[str]

 
class GoogleDriveMod(BaseMod):
    file_info: GoogleDriveFileInfo
    
    
class UploadCache(BaseModel):
    mods: list[GoogleDriveMod]
    
    
class LocalModsCache(BaseModel):
    mods: list[LocalMod]
    