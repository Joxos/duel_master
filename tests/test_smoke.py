from duel_engine import __version__


def test_version_exists():
    assert isinstance(__version__, str)
    assert __version__ != ""
