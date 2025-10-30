"""Spotify service layer with improved error handling."""
import logging
from typing import Optional, List, Dict, Tuple
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from config import SpotifyConfig

logger = logging.getLogger(__name__)

class SpotifyServiceError(Exception):
    """Base exception for Spotify service errors."""
    pass

class AuthenticationError(SpotifyServiceError):
    """Authentication related errors."""
    pass

class PlaybackError(SpotifyServiceError):
    """Playback related errors."""
    pass

class SearchError(SpotifyServiceError):
    """Search related errors."""
    pass

class SpotifyService:
    """Service class for interacting with Spotify API."""

    def __init__(self, config: SpotifyConfig):
        self.config = config
        self._sp: Optional[Spotify] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Spotify client with OAuth."""
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                redirect_uri=self.config.redirect_uri,
                scope=self.config.scope
            )
            self._sp = Spotify(auth_manager=auth_manager)
            logger.info("Spotify client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            raise AuthenticationError(f"Failed to initialize: {e}")

    @property
    def sp(self) -> Spotify:
        """Get Spotify client instance."""
        if self._sp is None:
            raise AuthenticationError("Spotify client not initialized")
        return self._sp

    def check_auth(self) -> Tuple[bool, Optional[str]]:
        """Check if user is authenticated."""
        try:
            current_user = self.sp.current_user()
            username = current_user['display_name']
            logger.info(f"Logged in as: {username}")
            return True, username
        except SpotifyException as e:
            if e.http_status == 401:
                return False, "Invalid credentials"
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def search(self, query: str, search_type: str = 'track', limit: int = 1) -> Optional[List[Dict]]:
        """Search for tracks, artists, or playlists."""
        try:
            results = self.sp.search(q=query, type=search_type, limit=limit)
            items = results[f"{search_type}s"]['items']
            if not items:
                logger.info(f"No results found for: {query}")
                return None
            return items
        except SpotifyException as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(f"Search failed: {e}")

    def play_track(self, uri: str) -> bool:
        """Play a specific track by URI."""
        try:
            self.sp.start_playback(uris=[uri])
            logger.info(f"Playing track: {uri}")
            return True
        except SpotifyException as e:
            if e.http_status == 404:
                raise PlaybackError("No active Spotify device found. Please open Spotify on a device.")
            elif e.http_status == 403:
                raise PlaybackError("Playback forbidden. Check your Spotify premium status.")
            raise PlaybackError(f"Playback error: {e}")

    def play_context(self, context_uri: str) -> bool:
        """Play a playlist or album by context URI."""
        try:
            self.sp.start_playback(context_uri=context_uri)
            logger.info(f"Playing context: {context_uri}")
            return True
        except SpotifyException as e:
            if e.http_status == 404:
                raise PlaybackError("No active Spotify device found")
            raise PlaybackError(f"Playback error: {e}")

    def pause_playback(self) -> bool:
        """Pause current playback."""
        try:
            self.sp.pause_playback()
            logger.info("Playback paused")
            return True
        except SpotifyException as e:
            raise PlaybackError(f"Failed to pause: {e}")

    def resume_playback(self) -> bool:
        """Resume playback."""
        try:
            self.sp.start_playback()
            logger.info("Playback resumed")
            return True
        except SpotifyException as e:
            raise PlaybackError(f"Failed to resume: {e}")

    def next_track(self) -> bool:
        """Skip to next track."""
        try:
            self.sp.next_track()
            logger.info("Skipped to next track")
            return True
        except SpotifyException as e:
            raise PlaybackError(f"Failed to skip: {e}")

    def previous_track(self) -> bool:
        """Go to previous track."""
        try:
            self.sp.previous_track()
            logger.info("Went to previous track")
            return True
        except SpotifyException as e:
            raise PlaybackError(f"Failed to go back: {e}")

    def set_volume(self, volume_percent: int) -> bool:
        """Set playback volume (0-100)."""
        if not 0 <= volume_percent <= 100:
            return False
        try:
            self.sp.volume(volume_percent)
            logger.info(f"Volume set to {volume_percent}%")
            return True
        except SpotifyException as e:
            raise PlaybackError(f"Failed to set volume: {e}")

    def toggle_shuffle(self, state: bool) -> bool:
        """Toggle shuffle mode."""
        try:
            self.sp.shuffle(state)
            logger.info(f"Shuffle {'enabled' if state else 'disabled'}")
            return True
        except SpotifyException as e:
            raise PlaybackError(f"Failed to toggle shuffle: {e}")

    def set_repeat(self, mode: str) -> bool:
        """Set repeat mode ('track', 'context', or 'off')."""
        if mode not in ['track', 'context', 'off']:
            return False
        try:
            self.sp.repeat(mode)
            logger.info(f"Repeat mode set to {mode}")
            return True
        except SpotifyException as e:
            raise PlaybackError(f"Failed to set repeat: {e}")

    def get_user_playlists(self) -> List[Dict]:
        """Get user's playlists."""
        try:
            playlists = self.sp.current_user_playlists()
            return playlists['items']
        except SpotifyException as e:
            logger.error(f"Failed to fetch playlists: {e}")
            return []

    def get_playlist_by_name(self, name: str) -> Optional[Dict]:
        """Find playlist by name."""
        playlists = self.get_user_playlists()
        for playlist in playlists:
            if playlist['name'].lower() == name.lower():
                return playlist
        return None

    def create_playlist(self, name: str, public: bool = True) -> Optional[str]:
        """Create a new playlist."""
        try:
            user_id = self.sp.current_user()['id']
            playlist = self.sp.user_playlist_create(user_id, name, public=public)
            logger.info(f"Created playlist: {name}")
            return playlist['id']
        except SpotifyException as e:
            logger.error(f"Failed to create playlist: {e}")
            return None

    def add_to_playlist(self, playlist_name: str, track_uris: List[str]) -> bool:
        """Add tracks to a playlist by name."""
        playlist = self.get_playlist_by_name(playlist_name)
        if not playlist:
            logger.error(f"Playlist '{playlist_name}' not found")
            return False
        try:
            self.sp.playlist_add_items(playlist['id'], track_uris)
            logger.info(f"Added {len(track_uris)} track(s) to '{playlist_name}'")
            return True
        except SpotifyException as e:
            logger.error(f"Failed to add tracks: {e}")
            return False