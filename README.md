# Spotify Voice Control Bot

A Python-based Spotify bot that allows users to control their music playback through voice commands or text inputs, all within a sleek Tkinter GUI. This bot leverages Spotify's API to offer seamless control over playback, playlists, and volume, providing both visual and audio feedback for a more interactive experience.

## Features

- **Voice Control**: 
  - Play songs, artists, or playlists.
  - Control playback with commands like `pause`, `resume`, `skip`, `shuffle`, `volume`, etc.
  - Manage playlists by creating and adding songs.
  
- **Manual Control**:
  - Submit commands via a text input field.
  
- **Feedback**:
  - Real-time logging of activities and status updates.
  - Visual feedback in the GUI with dynamic status labels and log entries.
  - Audio feedback with success or failure sounds.

## Commands

Here are some voice commands the bot supports:

- **Playback Controls**:
  - `Play [song name]` - Play a specific song.
  - `Play playlist [playlist name]` - Play a specific playlist.
  - `Play artist [artist name]` - Play a specific artist.
  - `Pause` - Pause the current track.
  - `Resume` - Resume playback.
  - `Skip` - Skip to the next track.
  - `Shuffle on/off` - Toggle shuffle mode.
  - `Repeat track/context/off` - Set repeat mode.

- **Volume Control**:
  - `Volume [level]` - Set volume level (0-100).

- **Playlist Management**:
  - `Create playlist [name]` - Create a new playlist.
  - `Add to playlist [playlist name] [song name]` - Add a song to a playlist.

## Requirements

- Python 3.x
- Tkinter (for GUI)
- pyttsx3 (for text-to-speech)
- Spotipy (for Spotify API integration)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/spotify-voice-control-bot.git
