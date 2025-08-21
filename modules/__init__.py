import importlib
from pathlib import Path
from loguru import logger


def discover_modules():
    """Discover and import all modules"""
    modules_dir = Path(__file__).parent
    for item in modules_dir.iterdir():
        if item.is_dir() and not item.name.startswith("__"):
            try:
                importlib.import_module(f"modules.{item.name}.handlers")
                logger.info(f"Loaded handlers of module: {item.name}")
            except ImportError as e:
                logger.error(f"Failed to load module {item.name}: {e}")
            except Exception as ex:
                logger.exception(f"Unexpected error loading module {item.name}: {ex}")
