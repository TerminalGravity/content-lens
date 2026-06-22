from content_lens.apps.registry import AppRegistry


def test_registry_finds_youtube():
    app = AppRegistry().for_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert app.name == "youtube"


def test_registry_lists_apps():
    assert "youtube" in AppRegistry().names()
