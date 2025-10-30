"""
Command handler using the Command Pattern for extensibility.
Maps text commands to specific service actions.
"""
import logging
import re
from typing import Dict, Tuple
from .spotify_service import SpotifyService, PlaybackError, SearchError

logger = logging.getLogger(__name__)

class Command:
    """Base command class."""
    def __init__(self, service: SpotifyService):
        self.service = service
    
    def execute(self, command_text: str) -> Tuple[bool, str]:
        """Execute the command. Returns (success, message)"""
        raise NotImplementedError

class PlayCommand(Command):
    """Handle 'play' commands (track, artist, playlist)."""
    def execute(self, command_text: str) -> Tuple[bool, str]:
        text = command_text.lower().replace("play", "", 1).strip() # Use replace with 1
        if not text:
            return False, "Please specify what to play."
        
        try:
            if text.startswith("playlist"):
                # --- FIX 1: Use replace with count 1 ---
                playlist_name = text.replace("playlist", "", 1).strip()
                playlist = self.service.get_playlist_by_name(playlist_name)
                if playlist:
                    self.service.play_context(playlist['uri'])
                    return True, f"Playing playlist: {playlist['name']}"
                return False, f"Playlist '{playlist_name}' not found"
            
            elif text.startswith("artist"):
                # --- FIX 2: Use replace with count 1 ---
                artist_name = text.replace("artist", "", 1).strip()
                results = self.service.search(artist_name, search_type='artist')
                artist = results[0]
                self.service.play_context(artist['uri'])
                return True, f"Playing artist: {artist['name']}"
            
            else:
                results = self.service.search(text, search_type='track')
                track = results[0]
                self.service.play_track(track['uri'])
                artist_names = ', '.join(a['name'] for a in track['artists'])
                return True, f"Playing: {track['name']} by {artist_names}"
                
        except (SearchError, PlaybackError) as e:
            return False, str(e)

class PauseCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        try:
            self.service.pause_playback()
            return True, "Playback paused"
        except PlaybackError as e: return False, str(e)

class ResumeCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        try:
            self.service.resume_playback()
            return True, "Playback resumed"
        except PlaybackError as e: return False, str(e)

class SkipCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        try:
            self.service.next_track()
            return True, "Skipped to next track"
        except PlaybackError as e: return False, str(e)

class PreviousCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        try:
            self.service.previous_track()
            return True, "Went to previous track"
        except PlaybackError as e: return False, str(e)

class VolumeCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        numbers = re.findall(r'\d+', command_text)
        if not numbers:
            return False, "Please specify volume level (0-100)"
        
        try:
            volume = int(numbers[0])
            self.service.set_volume(volume)
            return True, f"Volume set to {volume}%"
        except (ValueError, PlaybackError) as e:
            return False, str(e)

class ShuffleCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        state = "on" in command_text.lower()
        try:
            self.service.toggle_shuffle(state)
            status = "enabled" if state else "disabled"
            return True, f"Shuffle {status}"
        except PlaybackError as e: return False, str(e)

class RepeatCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        text = command_text.lower()
        mode = "off"
        if "track" in text: mode = "track"
        elif "context" in text or "playlist" in text: mode = "context"
        
        try:
            self.service.set_repeat(mode)
            return True, f"Repeat mode set to {mode}"
        except (ValueError, PlaybackError) as e:
            return False, str(e)

class CreatePlaylistCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        name = re.sub(r'create playlist', '', command_text, flags=re.I).strip()
        if not name:
            return False, "Please specify a playlist name"
        
        playlist_id = self.service.create_playlist(name)
        if playlist_id:
            return True, f"Created playlist: {name}"
        return False, "Failed to create playlist"

class AddToPlaylistCommand(Command):
    def execute(self, command_text: str) -> Tuple[bool, str]:
        # Use regex to capture original casing
        match = re.search(r"add (.+?) to playlist (.+)", command_text, flags=re.I)
        
        if not match:
            return False, "Format: 'add [song] to playlist [name]'"
        
        song_name = match.group(1).strip()
        playlist_name = match.group(2).strip()
        
        try:
            # --- THE FIX ---
            # Search using the lowercase version of the song name
            results = self.service.search(song_name.lower(), search_type='track')
            track = results[0]
            
            # Add to playlist using the original cased playlist_name
            # (our service handles its own lowercasing)
            success = self.service.add_to_playlist(playlist_name, [track['uri']])
            
            if success:
                # Use the original cased playlist_name for the message
                return True, f"Added '{track['name']}' to playlist '{playlist_name}'"
            return False, f"Failed to add track (playlist '{playlist_name}' not found?)"
        except (SearchError, PlaybackError) as e:
            return False, str(e)

class CommandHandler:
    """Handles command routing and execution."""
    def __init__(self, service: SpotifyService):
        self.service = service
        self.commands: Dict[str, Command] = {
            'create playlist': CreatePlaylistCommand(service),
            'add': AddToPlaylistCommand(service),
            'play': PlayCommand(service),
            'pause': PauseCommand(service),
            'resume': ResumeCommand(service),
            'skip': SkipCommand(service),
            'next': SkipCommand(service),
            'previous': PreviousCommand(service),
            'back': PreviousCommand(service),
            'volume': VolumeCommand(service),
            'shuffle': ShuffleCommand(service),
            'repeat': RepeatCommand(service),
        }
    
    def execute(self, command_text: str) -> Tuple[bool, str]:
        """Execute a command based on text input."""
        if not command_text:
            return False, "Empty command"
        
        command_lower = command_text.lower().strip()
        
        for keyword, command in self.commands.items():
            if command_lower.startswith(keyword):
                try:
                    # Pass the original cased text to the command
                    return command.execute(command_text)
                except Exception as e:
                    logger.error(f"Command execution error: {e}")
                    return False, f"Error executing command: {str(e)}"
        
        return False, "Command not recognized"