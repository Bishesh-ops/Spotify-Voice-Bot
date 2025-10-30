"""Command handler using command pattern for better extensibility."""
import logging
import re
from typing import Optional, Callable, Dict
from spotify_service import SpotifyService, PlaybackError, SearchError

logger = logging.getLogger(__name__)

class Command:
    """Base command class."""
    
    def __init__(self, service: SpotifyService):
        self.service = service
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        """Execute the command. Returns (success, message)"""
        raise NotImplementedError

class PlayCommand(Command):
    """Handle play commands."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        text = command_text.lower().replace("play", "").strip()
        
        if not text:
            return False, "Please specify what to play"
        
        # Check for playlist
        if "playlist" in text:
            playlist_name = text.replace("playlist", "").strip()
            playlist = self.service.get_playlist_by_name(playlist_name)
            if playlist:
                try:
                    self.service.play_context(playlist['uri'])
                    return True, f"Playing playlist: {playlist['name']}"
                except PlaybackError as e:
                    return False, str(e)
            else:
                return False, f"Playlist '{playlist_name}' not found"
        
        # Check for artist
        elif "artist" in text:
            artist_name = text.replace("artist", "").strip()
            try:
                results = self.service.search(artist_name, search_type='artist')
                if results:
                    artist = results[0]
                    self.service.play_context(artist['uri'])
                    return True, f"Playing artist: {artist['name']}"
                else:
                    return False, f"Artist '{artist_name}' not found"
            except (SearchError, PlaybackError) as e:
                return False, str(e)
        
        # Default: search for track
        else:
            try:
                results = self.service.search(text, search_type='track')
                if results:
                    track = results[0]
                    self.service.play_track(track['uri'])
                    artist_names = ', '.join(a['name'] for a in track['artists'])
                    return True, f"Playing: {track['name']} by {artist_names}"
                else:
                    return False, f"Track '{text}' not found"
            except (SearchError, PlaybackError) as e:
                return False, str(e)

class PauseCommand(Command):
    """Handle pause command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        try:
            self.service.pause_playback()
            return True, "Playback paused"
        except PlaybackError as e:
            return False, str(e)

class ResumeCommand(Command):
    """Handle resume command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        try:
            self.service.resume_playback()
            return True, "Playback resumed"
        except PlaybackError as e:
            return False, str(e)

class SkipCommand(Command):
    """Handle skip command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        try:
            self.service.next_track()
            return True, "Skipped to next track"
        except PlaybackError as e:
            return False, str(e)

class PreviousCommand(Command):
    """Handle previous track command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        try:
            self.service.previous_track()
            return True, "Went to previous track"
        except PlaybackError as e:
            return False, str(e)

class VolumeCommand(Command):
    """Handle volume command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        numbers = re.findall(r'\d+', command_text)
        if not numbers:
            return False, "Please specify volume level (0-100)"
        
        volume = int(numbers[0])
        if not 0 <= volume <= 100:
            return False, "Volume must be between 0 and 100"
        
        try:
            self.service.set_volume(volume)
            return True, f"Volume set to {volume}%"
        except PlaybackError as e:
            return False, str(e)

class ShuffleCommand(Command):
    """Handle shuffle command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        state = "on" in command_text.lower()
        try:
            self.service.toggle_shuffle(state)
            status = "enabled" if state else "disabled"
            return True, f"Shuffle {status}"
        except PlaybackError as e:
            return False, str(e)

class RepeatCommand(Command):
    """Handle repeat command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        text = command_text.lower()
        if "track" in text:
            mode = "track"
        elif "context" in text or "playlist" in text:
            mode = "context"
        else:
            mode = "off"
        
        try:
            self.service.set_repeat(mode)
            return True, f"Repeat mode set to {mode}"
        except PlaybackError as e:
            return False, str(e)

class CreatePlaylistCommand(Command):
    """Handle create playlist command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        name = command_text.lower().replace("create playlist", "").strip()
        if not name:
            return False, "Please specify a playlist name"
        
        playlist_id = self.service.create_playlist(name)
        if playlist_id:
            return True, f"Created playlist: {name}"
        else:
            return False, "Failed to create playlist"

class AddToPlaylistCommand(Command):
    """Handle add to playlist command."""
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        text = command_text.lower()
        
        # Try pattern: "add to playlist X song Y"
        pattern1 = r"add to playlist (.+?) (?:song|track) (.+)"
        match = re.search(pattern1, text)
        
        if match:
            playlist_name = match.group(1).strip()
            song_name = match.group(2).strip()
        else:
            # Try pattern: "add X to playlist Y"
            pattern2 = r"add (.+?) to playlist (.+)"
            match = re.search(pattern2, text)
            if match:
                song_name = match.group(1).strip()
                playlist_name = match.group(2).strip()
            else:
                return False, "Format: 'add [song] to playlist [name]'"
        
        try:
            results = self.service.search(song_name, search_type='track')
            if not results:
                return False, f"Track '{song_name}' not found"
            
            track = results[0]
            success = self.service.add_to_playlist(playlist_name, [track['uri']])
            
            if success:
                return True, f"Added '{track['name']}' to playlist '{playlist_name}'"
            else:
                return False, f"Failed to add track to playlist"
        except SearchError as e:
            return False, str(e)

class CommandHandler:
    """Handles command routing and execution."""
    
    def __init__(self, service: SpotifyService):
        self.service = service
        self.commands: Dict[str, Command] = {
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
            'create playlist': CreatePlaylistCommand(service),
            'add': AddToPlaylistCommand(service),
        }
    
    def execute(self, command_text: str) -> tuple[bool, str]:
        """Execute a command based on text input."""
        if not command_text:
            return False, "Empty command"
        
        command_lower = command_text.lower().strip()
        
        for keyword, command in self.commands.items():
            if keyword in command_lower:
                try:
                    return command.execute(command_text)
                except Exception as e:
                    logger.error(f"Command execution error: {e}")
                    return False, f"Error executing command: {str(e)}"
        
        return False, "Command not recognized. Try 'play [song]', 'pause', 'skip', etc."
    
    def get_available_commands(self) -> list[str]:
        """Get list of available commands."""
        return [
            "play [song/artist/playlist name]",
            "pause",
            "resume",
            "skip / next",
            "previous / back",
            "volume [0-100]",
            "shuffle on/off",
            "repeat track/context/off",
            "create playlist [name]",
            "add [song] to playlist [name]",
        ]