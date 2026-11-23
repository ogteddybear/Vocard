"""MIT License

Copyright (c) 2023 - present Vocard Development

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

from .enums import SearchType

load_dotenv()


def _env_or_setting(env_name: str, settings: Dict[str, Any], key: str) -> Optional[str]:
    value = os.getenv(env_name)
    if value:
        return value
    value = settings.get(key)
    if isinstance(value, str) and value.startswith("YOUR_"):
        return None
    return value


class Config:
    _instance: Optional['Config'] = None
    WORKING_DIR: Path = Path(__file__).resolve().parent.parent
    LAST_SESSION_FILE_DIR: str = WORKING_DIR / "last-session.json"

    def __new__(cls, settings: Dict[str, Any] = None) -> 'Config':
        if settings is not None:
            instance = super(Config, cls).__new__(cls)
            instance.__init__(settings)
            cls._instance = instance
            return instance
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, settings: Dict[str, Any] = None) -> None:
        if hasattr(self, 'initialized'):
            return
        settings = settings or {}

        self.token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN") or _env_or_setting("TOKEN", settings, "token")
        client_id = os.getenv("CLIENT_ID") or settings.get("client_id", 0)
        try:
            self.client_id = int(client_id)
        except (TypeError, ValueError):
            self.client_id = 0

        self.genius_token = _env_or_setting("GENIUS_TOKEN", settings, "genius_token")
        self.mongodb_url = os.getenv("MONGODB_URL") or _env_or_setting("MONGODB_URL", settings, "mongodb_url")
        self.mongodb_name = os.getenv("MONGODB_NAME") or _env_or_setting("MONGODB_NAME", settings, "mongodb_name")
        self.invite_link: str = "https://discord.gg/wRCgB7vBQv"

        self.nodes: Dict[str, Dict[str, Union[str, int, bool]]] = {
            name: dict(node) for name, node in settings.get("nodes", {}).items()
        }
        default_node = self.nodes.setdefault("DEFAULT", {})
        if os.getenv("LAVALINK_HOST"):
            default_node["host"] = os.getenv("LAVALINK_HOST")
        if os.getenv("LAVALINK_PORT"):
            default_node["port"] = int(os.getenv("LAVALINK_PORT"))
        if os.getenv("LAVALINK_SERVER_PASSWORD"):
            default_node["password"] = os.getenv("LAVALINK_SERVER_PASSWORD")
        elif os.getenv("LAVALINK_PASSWORD"):
            default_node["password"] = os.getenv("LAVALINK_PASSWORD")
        if os.getenv("LAVALINK_SECURE"):
            default_node["secure"] = os.getenv("LAVALINK_SECURE", "false").lower() in ("1", "true", "yes")

        self.max_queue: int = settings.get("default_max_queue", 1000)
        self.search_platform: SearchType = SearchType.from_platform(settings.get("default_search_platform", "youtube")) or SearchType.YOUTUBE
        self.bot_prefix: str = settings.get("prefix", "")
        self.activity: List[Dict[str, str]] = settings.get("activity", [{"listen": "/help"}])
        self.logging: Dict[str, Any] = settings.get("logging", {})
        self.embed_color: int = int(settings.get("embed_color", "0xb3b3b3"), 16)
        self.bot_access_user: List[int] = settings.get("bot_access_user", [])
        self.sources_settings: Dict[str, Dict[str, str]] = settings.get("sources_settings", {})
        self.cooldowns_settings: Dict[str, List[int]] = settings.get("cooldowns", {})
        self.aliases_settings: Dict[str, List[str]] = settings.get("aliases", {})
        self.controller: Dict[str, Dict[str, Any]] = settings.get("default_controller", {})
        self.voice_status_template: str = settings.get("default_voice_status_template", "")
        self.lyrics_platform: str = settings.get("lyrics_platform", "A_ZLyrics").lower()
        self.ipc_client: Dict[str, Union[str, bool, int]] = settings.get("ipc_client", {})
        self.playlist_settings: Dict[str, Union[str, int]] = settings.get("playlist_settings", {})
        self.timer_settings: Dict[str, int] = settings.get("timer_settings", {})
        self.version: str = settings.get("version", "")
        self.initialized = True

    @classmethod
    def get_source_config(cls, source: str, type: str) -> Union[str, None]:
        if not isinstance(source, str) or not isinstance(type, str):
            return None
        normalized_source = source.lower().strip().replace(" ", "")
        source_settings = cls._instance.sources_settings.get(
            normalized_source, cls._instance.sources_settings.get("others", {})
        )
        return source_settings.get(type)

    @classmethod
    def get_playlist_config(cls) -> tuple[int, int, str]:
        config = cls._instance.playlist_settings
        return (
            config.get("max_playlists", 5),
            config.get("max_tracks_per_playlist", 500),
            config.get("default_playlist_name", "Favourite"),
        )
