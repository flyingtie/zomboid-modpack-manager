from pydantic import BaseModel, ConfigDict, HttpUrl, Field
from pathlib import Path
from typing import List


class BaseMod(BaseModel):
    model_config = ConfigDict(validate_by_alias=True)
    
    name: str
    mod_id: str = Field(validation_alias="id")
    mod_hash: str

class LocalMod(BaseMod):
    path: Path

class RemoteMod(BaseMod):
    mod_url: HttpUrl

class Manifest(BaseModel):
    mods: List[RemoteMod]