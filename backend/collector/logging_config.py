import logging
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIR / "collector.log"


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,

        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),

        handlers=[
            logging.StreamHandler(),

            logging.FileHandler(
                LOG_FILE,
                encoding="utf-8",
            ),
        ],
    )
