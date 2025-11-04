from pydantic import BaseModel, ConfigDict, AnyUrl, Field
from pathlib import Path
from typing import List, Literal, Optional


class BaseMod(BaseModel):
    model_config = ConfigDict(validate_by_alias=True)
    
    name: str
    mod_id: str = Field(validation_alias="id")
    mod_hash: str


class LocalMod(BaseMod):
    path: Path
    
    
class ExportMod(BaseMod):
    url: AnyUrl


class ModpackManifest(BaseModel):
    mods: List[ExportMod]

        
class LocalModsCache(BaseModel):
    version: Literal["1.0"] = "1.0"
    
    mods: list[LocalMod]