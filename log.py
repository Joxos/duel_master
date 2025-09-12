import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time}</green> | {extra[source]} | <level>{message}</level>",
    level="DEBUG",
)
logger = logger.bind(source="main")
