"""Shared affairon plugin selection helpers.

This module reads one root ``pyproject.toml`` and derives dispatcher-specific
plugin subsets for the duel dispatcher and the kernel dispatcher.
"""

from pathlib import Path
import tomllib


PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"
KERNEL_EXECUTION_PLUGINS = {
    "duel_core.kernel.planners",
    "duel_core.kernel.appliers",
}


def local_plugins_from_pyproject(pyproject_path: Path = PYPROJECT_PATH) -> list[str]:
    with open(pyproject_path, "rb") as fh:
        config = tomllib.load(fh)
    return config.get("tool", {}).get("affairon", {}).get("local_plugins", [])


def duel_dispatcher_plugins(pyproject_path: Path = PYPROJECT_PATH) -> list[str]:
    return [
        module
        for module in local_plugins_from_pyproject(pyproject_path)
        if module not in KERNEL_EXECUTION_PLUGINS
    ]


def kernel_dispatcher_plugins(pyproject_path: Path = PYPROJECT_PATH) -> list[str]:
    return [
        module
        for module in local_plugins_from_pyproject(pyproject_path)
        if module in KERNEL_EXECUTION_PLUGINS
    ]
