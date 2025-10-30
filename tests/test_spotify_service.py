"""
Unit tests for the SpotifyService class.
"""
import pytest
from unittest.mock import MagicMock, patch
from spotipy.exceptions import SpotifyException

# Import from conftest
from tests.conftest import mock_config

# Import the service and exceptions
from spotify_service import SpotifyService, PlaybackError, SearchError, AuthenticationError

# --- Mocks for spotipy results ---
MOCK_TRACK_SEARCH = {
    'tracks': {
        'items': [
            {'name': 'Test Song', 'uri': 'spotify:track:123', 'artists': [{'name': 'Artist One'}]}
        ]
    }
}
MOCK_ARTIST_SEARCH = {
    'artists': {
        'items': [
            {'name': 'Test Artist', 'uri': 'spotify:artist:456'}
        ]
    }
}
MOCK_PLAYLIST_SEARCH = {
    'playlists': {
        'items': [
            {'name': 'Test Playlist', 'uri': 'spotify:playlist:789', 'id': '789'}
        ]
    }
}
MOCK_USER_PLAYLISTS = {
    'items': [
        {'name': 'Test Playlist', 'id': '789', 'uri': 'spotify:playlist:789'},
        {'name': 'Another Playlist', 'id': 'abc', 'uri': 'spotify:playlist:abc'}
    ]
}
MOCK_CURRENT_USER = {'display_name': 'TestUser', 'id': 'test_user_id'}


@pytest.fixture
def service_with_mocks(mock_config: SpotifyConfig) -> Tuple[SpotifyService, MagicMock]:
    """
    Provides a SpotifyService instance where spotipy is mocked.
    This tests the *logic* inside SpotifyService.
    """
    # Patch the two classes that SpotifyService tries to initialize
    with patch('spotify_service.SpotifyOAuth', autospec=True) as mock_oauth:
        with patch('spotify_service.Spotify', autospec=True) as mock_spotify_constructor:
            # Create a mock instance for the client
            mock_sp_client = MagicMock()
            
            # Make the constructor return our mock client
            mock_spotify_constructor.return_value = mock_sp_client
            
            # Initialize the service
            service = SpotifyService(mock_config)
            
            yield service, mock_sp_client

# --- Test Cases ---

def test_check_auth_success(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test successful authentication check."""
    service, mock_sp = service_with_mocks
    mock_sp.current_user.return_value = MOCK_CURRENT_USER
    
    success, username = service.check_auth()
    
    assert success is True
    assert username == "TestUser"
    mock_sp.current_user.assert_called_once()

def test_check_auth_401_error(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test 401 SpotifyException on auth check."""
    service, mock_sp = service_with_mocks
    mock_sp.current_user.side_effect = SpotifyException(401, -1, "Auth error")
    
    success, message = service.check_auth()
    
    assert success is False
    assert "Invalid credentials" in message

def test_search_track_success(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test successful track search."""
    service, mock_sp = service_with_mocks
    mock_sp.search.return_value = MOCK_TRACK_SEARCH
    
    results = service.search("Test Song", search_type='track', limit=1)
    
    assert results is not None
    assert len(results) == 1
    assert results[0]['name'] == 'Test Song'
    mock_sp.search.assert_called_once_with(q="Test Song", type='track', limit=1)

def test_search_no_results(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test SearchError when no results are found."""
    service, mock_sp = service_with_mocks
    mock_sp.search.return_value = {'tracks': {'items': []}}
    
    with pytest.raises(SearchError) as e:
        service.search("NonExistentSong", search_type='track')
    
    assert "No results found" in str(e.value)

def test_play_track_no_device_error(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test PlaybackError for 404 (No active device)."""
    service, mock_sp = service_with_mocks
    mock_sp.start_playback.side_effect = SpotifyException(404, -1, "No device")
    
    with pytest.raises(PlaybackError) as e:
        service.play_track("spotify:track:123")
        
    assert "No active Spotify device" in str(e.value)

def test_play_track_premium_error(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test PlaybackError for 403 (Premium required)."""
    service, mock_sp = service_with_mocks
    mock_sp.start_playback.side_effect = SpotifyException(403, -1, "PREMIUM_REQUIRED")
    
    with pytest.raises(PlaybackError) as e:
        service.play_track("spotify:track:123")
        
    assert "Spotify Premium" in str(e.value)

def test_pause_playback_success(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test successful pause."""
    service, mock_sp = service_with_mocks
    
    service.pause_playback()
    
    mock_sp.pause_playback.assert_called_once()

def test_get_playlist_by_name_success(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test finding a playlist by name (case-insensitive)."""
    service, mock_sp = service_with_mocks
    mock_sp.current_user_playlists.return_value = MOCK_USER_PLAYLISTS
    
    playlist = service.get_playlist_by_name("test playlist") # Lowercase
    
    assert playlist is not None
    assert playlist['name'] == "Test Playlist"
    assert playlist['id'] == "789"

def test_get_playlist_by_name_not_found(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test not finding a playlist by name."""
    service, mock_sp = service_with_mocks
    mock_sp.current_user_playlists.return_value = MOCK_USER_PLAYLISTS
    
    playlist = service.get_playlist_by_name("NonExistent Playlist")
    
    assert playlist is None

def test_add_to_playlist_success(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test successfully adding a track to a playlist."""
    service, mock_sp = service_with_mocks
    # Mock the two service calls this method makes
    mock_sp.current_user_playlists.return_value = MOCK_USER_PLAYLISTS
    mock_sp.playlist_add_items.return_value = None # No return value on success
    
    track_uri = ["spotify:track:123"]
    success = service.add_to_playlist("Test Playlist", track_uri)
    
    assert success is True
    mock_sp.current_user_playlists.assert_called_once()
    mock_sp.playlist_add_items.assert_called_once_with("789", track_uri)

def test_add_to_playlist_not_found(service_with_mocks: Tuple[SpotifyService, MagicMock]):
    """Test adding to a playlist that doesn't exist."""
    service, mock_sp = service_with_mocks
    mock_sp.current_user_playlists.return_value = MOCK_USER_PLAYLISTS
    
    success = service.add_to_playlist("Bad Playlist", ["spotify:track:123"])
    
    assert success is False
    mock_sp.playlist_add_items.assert_not_called() # Never gets to this call