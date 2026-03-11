from hypothesis import settings, Verbosity


def pytest_configure(config):
    # Register a simple profile for CI/local runs: no deadline to avoid flakiness
    settings.register_profile("ci", deadline=None, verbosity=Verbosity.normal)
    settings.load_profile("ci")
