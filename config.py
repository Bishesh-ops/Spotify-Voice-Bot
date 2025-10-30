"""Configuration management for Spotify Voice Control Bot."""
import os
import json
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

@dataclass
class SpotifyConfig:
    """Spotify API configuration."""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8080"
    scope: str = "user-library-read user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private"

@dataclass
class UIConfig:
    """UI configuration settings."""
    window_width: int = 700
    window_height: int = 600
    speech_rate: int = 150
    background_color: str = "#121212"
    primary_color: str = "#1DB954"
    secondary_color: str = "#1c1c1c"
    text_color: str = "white"

@dataclass
class AppConfig:
    """Main application configuration."""
    log_level: str = "INFO"
    log_file: str = "spotify_bot.log"
    max_log_size: int = 1024 * 1024
    log_backup_count: int = 5
    enable_audio_feedback: bool = True
    enable_voice_feedback: bool = True
    spotify: SpotifyConfig = None
    ui: UIConfig = None

    def __post_init__(self):
        if self.spotify is None:
            self.spotify = SpotifyConfig()
        if self.ui is None:
            self.ui = UIConfig()

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables."""
        spotify_config = SpotifyConfig(
            client_id=os.getenv("SPOTIPY_CLIENT_ID", ""),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET", ""),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8080")
        )
        return cls(log_level=os.getenv("LOG_LEVEL", "INFO"), spotify=spotify_config, ui=UIConfig())

    def validate(self) -> bool:
        """Validate configuration."""
        return bool(self.spotify.client_id and self.spotify.client_secret)