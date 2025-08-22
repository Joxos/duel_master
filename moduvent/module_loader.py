# src/modular_events/module_loader.py
import importlib
from .log import logger
from pathlib import Path
from .event_manager import EventManager


class ModuleLoader:
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.loaded_modules = set()

    def discover_modules(self, modules_dir: str = "modules"):
        modules_path = Path(modules_dir)

        if not modules_path.exists():
            logger.warning(f"Module directory does not exist: {modules_dir}")
            return

        for item in modules_path.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                try:
                    module_name = f"{modules_dir}.{item.name}"
                    self.load_module(module_name)
                except ImportError as e:
                    logger.error(f"Failed to load module {item.name}: {e}")
                except Exception as ex:
                    logger.exception(
                        f"Unexpected error occurred while loading module {item.name}: {ex}"
                    )

    def load_module(self, module_name: str):
        if module_name in self.loaded_modules:
            logger.debug(f"Module already loaded: {module_name}")
            return

        try:
            importlib.import_module(module_name)
            self.loaded_modules.add(module_name)
            logger.info(f"Successfully loaded module: {module_name}")

        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            raise
