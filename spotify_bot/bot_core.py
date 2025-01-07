import os
import logging
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import speech_recognition as sr

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8080")
SCOPE = "user-library-read user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private"


# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Spotipy with OAuth manager
sp = Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                       client_secret=CLIENT_SECRET,
                                       redirect_uri=REDIRECT_URI,
                                       scope=SCOPE))


def check_auth():
    """Check if the user is authenticated and print the current user's name."""
    try:
        current_user = sp.current_user()
        logging.info(f"Logged in as: {current_user['display_name']}")
    except Exception as e:
        logging.error(f"Authentication failed: {e}")


def list_playlists():
    """List the user's playlists."""
    try:
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            logging.info(f"Playlist: {playlist['name']} - {playlist['tracks']['total']} tracks")
    except Exception as e:
        logging.error(f"Error fetching playlists: {e}")


def list_user_playlists():
    """Fetch the user's playlists."""
    try:
        playlists = sp.current_user_playlists()
        playlist_names = [playlist['name'] for playlist in playlists['items']]
        return playlist_names
    except Exception as e:
        logging.error(f"Error fetching playlists: {e}")
        return []

def add_tracks_to_playlist_by_name(playlist_name, track_uris):
    """Add tracks to a playlist by its name."""
    try:
        # Get the current user's playlists
        playlists = sp.current_user_playlists()
        playlist_id = None

        # Search for the playlist by name
        for playlist in playlists['items']:
            if playlist['name'].lower() == playlist_name.lower():
                playlist_id = playlist['id']
                break

        if not playlist_id:
            logging.error(f"Playlist '{playlist_name}' does not exist.")
            return f"Error: Playlist '{playlist_name}' does not exist."

        # Add the tracks to the playlist
        sp.playlist_add_items(playlist_id, track_uris)
        logging.info(f"Added tracks to playlist '{playlist_name}'.")
        return f"Successfully added tracks to playlist '{playlist_name}'."
    except Exception as e:
        logging.error(f"Error adding tracks to playlist: {e}")
        return f"Error adding tracks to playlist: {e}"


def create_playlist(name, public=True):
    """Create a new playlist with the given name."""
    try:
        user_id = sp.current_user()['id']
        sp.user_playlist_create(user_id, name, public=public)
        logging.info(f"Playlist '{name}' created.")
    except Exception as e:
        logging.error(f"Error creating playlist: {e}")


def add_tracks_to_playlist(playlist_id, track_uris):
    """Add tracks to the given playlist by URI."""
    try:
        sp.playlist_add_items(playlist_id, track_uris)
        logging.info(f"Added tracks to playlist {playlist_id}.")
    except Exception as e:
        logging.error(f"Error adding tracks to playlist: {e}")


def toggle_shuffle(state=True):
    """Enable or disable shuffle mode."""
    try:
        sp.shuffle(state)
        status = "enabled" if state else "disabled"
        logging.info(f"Shuffle mode {status}.")
    except Exception as e:
        logging.error(f"Error toggling shuffle: {e}")


def toggle_repeat(mode="off"):
    """Set repeat mode to 'track', 'context', or 'off'."""
    try:
        sp.repeat(mode)
        logging.info(f"Repeat mode set to {mode}.")
    except Exception as e:
        logging.error(f"Error setting repeat mode: {e}")


def add_to_queue(track_uri):
    """Add a track to the queue by its URI."""
    try:
        sp.add_to_queue(track_uri)
        logging.info(f"Added to queue: {track_uri}")
    except Exception as e:
        logging.error(f"Error adding to queue: {e}")


def search_and_play(query, search_type='track'):
    """Search for a track, artist, or playlist and play it."""
    try:
        results = sp.search(q=query, type=search_type, limit=1)
        if results[search_type + 's']['items']:
            item = results[search_type + 's']['items'][0]
            uri = item['uri']
            logging.info(f"Found {search_type}: {item['name']} by {', '.join(artist['name'] for artist in item['artists'])}")
            play_music(uri)
        else:
            logging.info(f"No results found for {query}")
    except Exception as e:
        logging.error(f"Error searching for {query}: {e}")



def play_music(uri):
    """Play a specific track or playlist using its URI."""
    try:
        if 'playlist' in uri:
            # For playlists, we use the 'context' parameter instead of 'uris'
            sp.start_playback(context_uri=uri)
            logging.info(f"Now playing playlist: {uri}")
        else:
            # For tracks, we use the 'uris' parameter as before
            sp.start_playback(uris=[uri])
            logging.info(f"Now playing: {uri}")
    except Exception as e:
        logging.error(f"Error playing track/playlist: {e}")


def get_playlist_uri_by_name(playlist_name):
    """Get the URI of a playlist by name."""
    try:
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            if playlist_name.lower() == playlist['name'].lower():
                return playlist['uri']  # The correct format is 'spotify:playlist:{playlist_id}'
        logging.error(f"Playlist '{playlist_name}' not found.")
        return None
    except Exception as e:
        logging.error(f"Error fetching playlist URI: {e}")
        return None

def voice_control():
    """Use voice commands to control playback."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        logging.info("Listening for voice command...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            logging.info(f"Heard command: {command}")

            # Add to playlist command
            if "add to playlist" in command:
                parts = command.replace("add to playlist", "").strip().split(" with ")
                if len(parts) == 2:
                    playlist_name = parts[0].strip()
                    track_query = parts[1].strip()
                    # Search for the track
                    results = sp.search(q=track_query, type='track', limit=1)
                    if results['tracks']['items']:
                        track_uri = results['tracks']['items'][0]['uri']
                        result_message = add_tracks_to_playlist_by_name(playlist_name, [track_uri])
                        logging.info(result_message)
                    else:
                        logging.error(f"Track '{track_query}' not found.")
                        logging.info("Error: Track not found.")
                else:
                    logging.error("Please specify both a playlist and a track to add.")
            elif "create playlist" in command:
                name = command.replace("create playlist", "").strip()
                if name:  # Ensure there is a name
                    create_playlist(name)
                else:
                    logging.info("Please specify a playlist name after 'create playlist'.")
            # Other commands...
            elif "play" in command:
                # Check if the user wants to play a specific playlist
                if "playlist" in command:
                    playlist_name = command.replace("play playlist", "").strip()
                    playlists = list_user_playlists()  # Fetch the user's playlists
                    matching_playlists = [playlist for playlist in playlists if
                                          playlist_name.lower() in playlist.lower()]
                    if matching_playlists:
                        playlist_to_play = matching_playlists[0]  # Play the first match
                        logging.info(f"Playing playlist: {playlist_to_play}")
                        # Search and play the first track of the found playlist
                        playlist_uri = get_playlist_uri_by_name(playlist_to_play)
                        play_music(playlist_uri)
                    else:
                        logging.error(f"Playlist '{playlist_name}' not found.")
                else:
                    search_and_play(command.replace("play", "").strip(), search_type='track')
            elif "pause" in command:
                sp.pause_playback()
                logging.info("Paused playback.")
            elif "resume" in command:
                sp.start_playback()
                logging.info("Resumed playback.")
            elif "skip" in command:
                sp.next_track()
                logging.info("Skipped to next track.")
            elif "shuffle" in command:
                toggle_shuffle(state="on" in command)
            elif "repeat" in command:
                if "track" in command:
                    toggle_repeat("track")
                elif "context" in command:
                    toggle_repeat("context")
                else:
                    toggle_repeat("off")
            elif "volume" in command:
                volume_level = [int(s) for s in command.split() if s.isdigit()]
                if volume_level:
                    sp.volume(volume_level[0])
                    logging.info(f"Volume set to {volume_level[0]}%.")
            else:
                logging.info("Command not recognized.")
        except sr.UnknownValueError:
            logging.error("Could not understand audio.")
        except sr.RequestError as e:
            logging.error(f"Could not request results; {e}")


if __name__ == "__main__":
    check_auth()
    list_playlists()
    track_uri = 'spotify:track:0VjIjW4GlUZAMYd2vXMi3b'  # Example URI
    add_to_queue(track_uri)
    search_and_play("Best Song ever", search_type='track')
    voice_control()
