"""
Configuration management for Spotify Voice Control Bot.
Uses dataclasses and loads from environment variables.
"""
import os
import logging
from dataclasses import dataclass, field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass
class SpotifyConfig:
    """Spotify API configuration."""
    # Add default values to satisfy strict type checker for default_factory
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8080"
    scope: str = (
        "user-library-read user-read-playback-state "
        "user-modify-playback-state playlist-modify-public "
        "playlist-modify-private"
    )

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
    max_log_size: int = 1024 * 1024  # 1 MB
    log_backup_count: int = 5

    # --- THE FIX ---
    # The default_factory now correctly creates an instance
    # of the SpotifyConfig class, matching the type hint.
    spotify: SpotifyConfig = field(default_factory=SpotifyConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """
        Load configuration from environment variables.
        
        Raises:
            ValueError: If essential environment variables are missing.
        """
        load_dotenv()  # Load from .env file
        
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8080")
        
        if not client_id:
            raise ValueError("SPOTIPY_CLIENT_ID not set in environment")
        if not client_secret:
            raise ValueError("SPOTIPY_CLIENT_SECRET not set in environment")

        spotify_config = SpotifyConfig(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )
        
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log_level = "INFO"
            
        return cls(
            log_level=log_level,
            spotify=spotify_config,
            ui=UIConfig()
        )

    def validate(self) -> bool:
        """Validate that essential configuration is present."""
        # This check works perfectly, as it checks the fields
        # of the default or populated SpotifyConfig object.
        return bool(self.spotify.client_id and self.spotify.client_secret)