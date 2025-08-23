from manifest import Manifest
from updater import Updater


class App:
    def __init__(self):
        self.manifest = Manifest()
        self.updater = Updater()
    
    def update_mods(self):
        ...
    