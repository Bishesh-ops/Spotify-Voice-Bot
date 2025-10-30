"""
Spotify service layer with improved error handling.
Wraps all Spotipy calls to provide a clean interface.
"""
import logging
from typing import Optional, List, Dict, Tuple, Any
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from config import SpotifyConfig  # Import from your new config file

logger = logging.getLogger(__name__)

# --- Custom Exceptions ---

class SpotifyServiceError(Exception):
    """Base exception for Spotify service errors."""
    pass

class AuthenticationError(SpotifyServiceError):
    """Authentication related errors."""
    pass

class PlaybackError(SpotifyServiceError):
    """Playback related errors (e.g., no active device)."""
    pass

class SearchError(SpotifyServiceError):
    """Search related errors (e.g., query failed)."""
    pass

# --- Service Class ---

class SpotifyService:
    """Service class for interacting with the Spotify API."""

    def __init__(self, config: SpotifyConfig):
        self.config = config
        self._sp: Optional[Spotify] = None
        try:
            self._initialize_client()
        except Exception as e:
            logger.critical(f"Failed to initialize Spotify client: {e}")
            raise AuthenticationError(f"Failed to initialize Spotipy: {e}")

    def _initialize_client(self) -> None:
        """Initialize Spotify client with OAuth."""
        auth_manager = SpotifyOAuth(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            redirect_uri=self.config.redirect_uri,
            scope=self.config.scope,
            cache_path=".cache"
        )
        self._sp = Spotify(auth_manager=auth_manager)
        logger.info("Spotify client initialized")

    @property
    def sp(self) -> Spotify:
        """Get the authenticated Spotipy client instance."""
        if self._sp is None:
            raise AuthenticationError("Spotify client not initialized")
        return self._sp

    def check_auth(self) -> Tuple[bool, str]:
        """Check if user is authenticated."""
        try:
            current_user = self.sp.current_user()
            if not current_user:
                return False, "Authentication failed: No user returned."
            username = current_user.get('display_name', 'Unknown')
            logger.info(f"Logged in as: {username}")
            return True, username
        except SpotifyException as e:
            if e.http_status == 401:
                return False, "Invalid credentials or expired token."
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def search(self, query: str, search_type: str = 'track', limit: int = 1) -> List[Dict[str, Any]]:
        """Search for tracks, artists, or playlists."""
        try:
            results = self.sp.search(q=query, type=search_type, limit=limit)
            items = results[f"{search_type}s"]['items']
            if not items:
                raise SearchError(f"No results found for: {query}")
            return items
        except SpotifyException as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(f"Search failed: {e}")
        except KeyError:
            raise SearchError("Malformed search result from Spotify.")

    def _handle_playback_error(self, e: SpotifyException, action: str):
        """Helper to parse common Spotify playback errors."""
        if e.http_status == 404:
            raise PlaybackError("No active Spotify device found. Please open Spotify.")
        elif e.http_status == 403:
            if "PREMIUM_REQUIRED" in e.msg:
                raise PlaybackError("This action requires a Spotify Premium account.")
            raise PlaybackError(f"Playback forbidden: {e.msg}")
        raise PlaybackError(f"Failed to {action}: {e}")

    def play_track(self, uri: str):
        """Play a specific track by URI."""
        try:
            self.sp.start_playback(uris=[uri])
            logger.info(f"Playing track: {uri}")
        except SpotifyException as e:
            self._handle_playback_error(e, "play track")

    def play_context(self, context_uri: str):
        """Play a playlist or album by context URI."""
        try:
            self.sp.start_playback(context_uri=context_uri)
            logger.info(f"Playing context: {context_uri}")
        except SpotifyException as e:
            self._handle_playback_error(e, "play context")

    def pause_playback(self):
        """Pause current playback."""
        try:
            self.sp.pause_playback()
            logger.info("Playback paused")
        except SpotifyException as e:
            self._handle_playback_error(e, "pause")

    def resume_playback(self):
        """Resume playback."""
        try:
            self.sp.start_playback()
            logger.info("Playback resumed")
        except SpotifyException as e:
            self._handle_playback_error(e, "resume")

    def next_track(self):
        """Skip to next track."""
        try:
            self.sp.next_track()
            logger.info("Skipped to next track")
        except SpotifyException as e:
            self._handle_playback_error(e, "skip")

    def previous_track(self):
        """Go to previous track."""
        try:
            self.sp.previous_track()
            logger.info("Went to previous track")
        except SpotifyException as e:
            self._handle_playback_error(e, "go back")

    def set_volume(self, volume_percent: int):
        """Set playback volume (0-100)."""
        if not 0 <= volume_percent <= 100:
            raise ValueError("Volume must be between 0 and 100")
        try:
            self.sp.volume(volume_percent)
            logger.info(f"Volume set to {volume_percent}%")
        except SpotifyException as e:
            self._handle_playback_error(e, "set volume")

    def toggle_shuffle(self, state: bool):
        """Toggle shuffle mode."""
        try:
            self.sp.shuffle(state)
            logger.info(f"Shuffle {'enabled' if state else 'disabled'}")
        except SpotifyException as e:
            self._handle_playback_error(e, "toggle shuffle")

    def set_repeat(self, mode: str):
        """Set repeat mode ('track', 'context', or 'off')."""
        if mode not in ['track', 'context', 'off']:
            raise ValueError("Repeat mode must be 'track', 'context', or 'off'")
        try:
            self.sp.repeat(mode)
            logger.info(f"Repeat mode set to {mode}")
        except SpotifyException as e:
            self._handle_playback_error(e, "set repeat")

    def get_user_playlists(self) -> List[Dict[str, Any]]:
        """Get user's playlists."""
        try:
            playlists = self.sp.current_user_playlists()
            return playlists['items'] if playlists else []
        except SpotifyException as e:
            logger.error(f"Failed to fetch playlists: {e}")
            return []

    def get_playlist_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find playlist by name (case-insensitive)."""
        playlists = self.get_user_playlists()
        name_lower = name.lower()
        for playlist in playlists:
            if playlist['name'].lower() == name_lower:
                return playlist
        return None

    def create_playlist(self, name: str, public: bool = True) -> Optional[str]:
        """Create a new playlist."""
        try:
            user_id = self.sp.current_user()['id']
            playlist = self.sp.user_playlist_create(user_id, name, public=public)
            logger.info(f"Created playlist: {name}")
            return playlist['id']
        except (SpotifyException, KeyError) as e:
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