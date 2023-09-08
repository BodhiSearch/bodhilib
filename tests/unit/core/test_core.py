from bodhilib.core import __version__


def test_version_is_generated():
    assert __version__ != ""
