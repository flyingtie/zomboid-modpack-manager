from pydantic import BaseModel, ConfigDict, AnyUrl, Field
from pathlib import Path
from typing import List, Literal, Optional


class BaseMod(BaseModel):
    name: str
    id: str
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