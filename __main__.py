import logging

from src.updater import update
from src.config_loader import settings


logging.basicConfig(logging.INFO)

logger = logging.getLogger(__name__)

def run():
    logger.info("Start updating")
    update()
    logger.info("Program finished")

if __name__ == "__main__":
    run()
    input()
