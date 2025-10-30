"""
Pytest fixtures for the test suite.
"""
import pytest
from unittest.mock import MagicMock, patch

# Make sure your project root is in the path for imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import your modules
from config import SpotifyConfig, AppConfig
from spotify_service import SpotifyService, PlaybackError, SearchError
from command_handler import CommandHandler

@pytest.fixture
def mock_config() -> SpotifyConfig:
    """Returns a mock SpotifyConfig object."""
    return SpotifyConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8080"
    )

@pytest.fixture
def mock_spotipy() -> MagicMock:
    """Returns a MagicMock for the spotipy.Spotify client."""
    return MagicMock()

@pytest.fixture
def mock_spotify_service(mock_config: SpotifyConfig) -> MagicMock:
    """
    Returns a MagicMock of the SpotifyService.
    We mock the whole service to test the CommandHandler in isolation.
    """
    return MagicMock(spec=SpotifyService)

@pytest.fixture
def command_handler(mock_spotify_service: MagicMock) -> CommandHandler:
    """Returns a CommandHandler instance with a mock service."""
    return CommandHandler(mock_spotify_service)