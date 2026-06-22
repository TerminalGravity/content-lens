from __future__ import annotations

from content_lens.apps.base import ContentApp
from content_lens.apps.youtube import YouTubeApp


class AppRegistry:
    def __init__(self, apps: list[ContentApp] | None = None) -> None:
        self._apps = apps or [YouTubeApp()]

    def names(self) -> list[str]:
        return [app.name for app in self._apps]

    def by_name(self, name: str) -> ContentApp:
        for app in self._apps:
            if app.name == name:
                return app
        raise KeyError(f"Unknown app {name!r}; available: {', '.join(self.names())}")

    def for_url(self, url: str) -> ContentApp:
        for app in self._apps:
            if app.can_handle(url):
                return app
        raise KeyError(f"No registered app can handle URL: {url}")
