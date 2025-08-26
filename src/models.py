from pydantic import BaseModel, ConfigDict, AnyUrl, Field
from pathlib import Path
from typing import Iterable


class BaseMod(BaseModel):
    model_config = ConfigDict(validate_by_alias=True)
    
    name: str
    mod_id: str = Field(validation_alias="id")
    mod_hash: str

class LocalMod(BaseMod):
    path: Path

class Mod(BaseMod):
    mod_url: AnyUrl

class Manifest(BaseModel):
    mods: Iterable[Mod]