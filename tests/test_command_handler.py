"""
Unit tests for the CommandHandler class.
These tests use a mocked SpotifyService.
"""
import pytest
from unittest.mock import MagicMock

# Import from conftest
from tests.conftest import command_handler, mock_spotify_service

# Import the service and exceptions
from spotify_service import PlaybackError, SearchError

# --- Re-use mock results from service tests ---
from tests.test_spotify_service import (
    MOCK_TRACK_SEARCH,
    MOCK_ARTIST_SEARCH,
    MOCK_PLAYLIST_SEARCH,
    MOCK_USER_PLAYLISTS
)

# --- Test Cases ---

def test_play_track_command(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test the 'play [song name]' command."""
    # Arrange
    mock_spotify_service.search.return_value = MOCK_TRACK_SEARCH['tracks']['items']
    command_text = "play Test Song"
    
    # Act
    success, message = command_handler.execute(command_text)
    
    # Assert
    assert success is True
    assert "Playing: Test Song by Artist One" in message
    # Verify it called the *service* correctly
    mock_spotify_service.search.assert_called_once_with("test song", search_type='track')
    mock_spotify_service.play_track.assert_called_once_with("spotify:track:123")

def test_play_artist_command(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test the 'play artist [name]' command."""
    mock_spotify_service.search.return_value = MOCK_ARTIST_SEARCH['artists']['items']
    command_text = "play artist Test Artist"
    
    success, message = command_handler.execute(command_text)
    
    assert success is True
    assert "Playing artist: Test Artist" in message
    mock_spotify_service.search.assert_called_once_with("test artist", search_type='artist')
    mock_spotify_service.play_context.assert_called_once_with("spotify:artist:456")

def test_play_playlist_command(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test the 'play playlist [name]' command."""
    mock_spotify_service.get_playlist_by_name.return_value = MOCK_PLAYLIST_SEARCH['playlists']['items'][0]
    command_text = "play playlist Test Playlist"
    
    success, message = command_handler.execute(command_text)
    
    assert success is True
    assert "Playing playlist: Test Playlist" in message
    mock_spotify_service.get_playlist_by_name.assert_called_once_with("test playlist")
    mock_spotify_service.play_context.assert_called_once_with("spotify:playlist:789")

def test_play_command_no_results(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test a play command where the service's search raises an error."""
    mock_spotify_service.search.side_effect = SearchError("No results")
    command_text = "play NonExistentSong"
    
    success, message = command_handler.execute(command_text)
    
    assert success is False
    assert "No results" in message

def test_pause_command(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test the 'pause' command."""
    command_text = "pause"
    
    success, message = command_handler.execute(command_text)
    
    assert success is True
    assert "Playback paused" in message
    mock_spotify_service.pause_playback.assert_called_once()

def test_resume_command(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test the 'resume' command."""
    command_text = "resume"
    
    success, message = command_handler.execute(command_text)
    
    assert success is True
    assert "Playback resumed" in message
    mock_spotify_service.resume_playback.assert_called_once()

def test_volume_command(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test the 'volume [level]' command."""
    command_text = "volume 75"
    
    success, message = command_handler.execute(command_text)
    
    assert success is True
    assert "Volume set to 75" in message
    mock_spotify_service.set_volume.assert_called_once_with(75)

def test_volume_command_invalid(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test 'volume' command with an invalid number."""
    mock_spotify_service.set_volume.side_effect = ValueError("Volume must be 0-100")
    command_text = "volume 200"
    
    success, message = command_handler.execute(command_text)
    
    assert success is False
    assert "Volume must be 0-100" in message

def test_add_to_playlist_command(command_handler: MagicMock, mock_spotify_service: MagicMock):
    """Test the 'add [song] to playlist [name]' command."""
    mock_spotify_service.search.return_value = MOCK_TRACK_SEARCH['tracks']['items']
    mock_spotify_service.add_to_playlist.return_value = True
    command_text = "add Test Song to playlist My Favs"
    
    success, message = command_handler.execute(command_text)
    
    assert success is True
    assert "Added 'Test Song' to playlist 'My Favs'" in message
    mock_spotify_service.search.assert_called_once_with("test song", search_type='track')
    mock_spotify_service.add_to_playlist.assert_called_once_with("my favs", ["spotify:track:123"])

def test_unrecognized_command(command_handler: MagicMock):
    """Test a command that doesn't match any keyword."""
    command_text = "this is not a real command"
    
    success, message = command_handler.execute(command_text)
    
    assert success is False
    assert "Command not recognized" in message