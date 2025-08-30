from loguru import logger

from src.config_loader import settings
from src.updater import Updater


updater = Updater()

def run():
    updater.run()

if __name__ == "__main__":
    run()
    input("READY")
