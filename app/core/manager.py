from app.core.models import LocalMod, ExportMod, ModpackManifest
from typing import Optional, Generator


def get_missing_mods(remote_mods: list[ExportMod], local_mods: list[LocalMod]) -> Generator[tuple[ExportMod, Optional[LocalMod]], None, None]:
    for export_mod in remote_mods:
        is_missing = True
        
        for local_mod in local_mods:
            if export_mod.id != local_mod.id:
                continue
            if export_mod.mod_hash == local_mod.mod_hash: 
                is_missing = False
                break
            is_missing = False
            yield export_mod, local_mod
            break
        
        if is_missing:
            yield export_mod, None