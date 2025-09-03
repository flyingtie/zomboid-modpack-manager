import logging
import click

from src.updater import update
from src.uploader import upload
from src.loader import settings


logging.basicConfig(logging.INFO)

logger = logging.getLogger(__name__)

click.prompt()
def cli():
    pass

if __name__ == "__main__":
    cli()
