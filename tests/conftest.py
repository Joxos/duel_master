from hypothesis import settings, Verbosity
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_configure(config):
    # Register a simple profile for CI/local runs: no deadline to avoid flakiness
    settings.register_profile("ci", deadline=None, verbosity=Verbosity.normal)
    settings.load_profile("ci")
