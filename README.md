#  Spotify Voice Control Bot v2.0

A Python-based bot to control your Spotify music playback using voice commands or text inputs, built with a modern, secure, and testable architecture.



## 🚀 Features

-   **Voice Control**: Play songs, artists, or playlists with your voice.
-   **Text Control**: Type commands directly into the UI.
-   **Full Playback Control**: `play`, `pause`, `resume`, `skip`, `previous`.
-   **Library Management**: `volume`, `shuffle`, `repeat`.
-   **Playlist Management**: `create playlist [name]` and `add [song] to playlist [name]`.
-   **Cross-Platform**: Works on Windows, macOS, and Linux.
-   **Real-time Feedback**: Get instant audio and visual feedback for success or errors.
-   **Secure**: Your API keys are kept safe in a `.env` file and never committed.
-   **Robust**: Handles common errors gracefully (e.g., "No active device").

---

## 🔧 Installation & Setup

Follow the [Quick Start Guide](quick_start.md) to get up and running in 5 minutes!

**Short Version:**

1.  **Clone Repo:**
    ```bash
    git clone [https://github.com/Bishesh-ops/Spotify-Voice-Bot.git](https://github.com/Bishesh-ops/Spotify-Voice-Bot.git)
    cd Spotify-Voice-Bot
    ```

2.  **Create Environment & Install:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Get Spotify Credentials:**
    -   Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
    -   Create an app.
    -   Copy your **Client ID** and **Client Secret**.
    -   Click "Edit Settings" and add this **Redirect URI**: `http://localhost:8080`

4.  **Create `.env` File:**
    -   Copy `.env.example` to a new file named `.env`.
    -   Paste your credentials into the `.env` file.
    ```env
    SPOTIPY_CLIENT_ID="YOUR_SPOTIFY_CLIENT_ID"
    SPOTIPY_CLIENT_SECRET="YOUR_SPOTIFY_CLIENT_SECRET"
    SPOTIPY_REDIRECT_URI="http://localhost:8080"
    ```

---

## ▶️ How to Run

1.  Make sure your virtual environment is active.
2.  Make sure Spotify is open on any device (desktop, phone, etc.).
3.  Run the application:
    ```bash
    python UI_improved.py
    ```

4.  **First Time Only:** A browser window will open.
    -   Log in and agree to the permissions.
    -   You'll be redirected to a `localhost:8080` page (it's okay if it says "can't connect").
    -   Copy the **full URL** from your browser's address bar.
    -   Paste it into the terminal where the bot is asking for it and press Enter.

5.  The UI will launch, and you're ready!

---

## 🎧 Available Commands

| Command | Example |
| :--- | :--- |
| **Play Song** | `play happy` |
| **Play Artist** | `play artist queen` |
| **Play Playlist** | `play playlist workout` |
| **Pause** | `pause` |
| **Resume** | `resume` |
| **Skip / Next** | `skip` or `next` |
| **Previous / Back**| `previous` or `back` |
| **Set Volume** | `volume 50` |
| **Shuffle** | `shuffle on` or `shuffle off` |
| **Repeat** | `repeat track` / `repeat context` / `repeat off` |
| **Create Playlist**| `create playlist my new mix` |
| **Add to Playlist**| `add song_name to playlist my new mix` |

---

## 🐛 Troubleshooting

-   **"No active device" Error:**
    -   **Fix:** Open Spotify on your phone or desktop and play any song, then pause it. The API needs to see an "active" device.

-   **"Authentication failed" Error:**
    -   **Fix 1:** Double-check your `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` in your `.env` file.
    -   **Fix 2:** Delete the `.cache` file in your project folder and restart the app.

-   **Voice Not Working:**
    -   **Fix 1:** Make sure your microphone is plugged in and has permission.
    -   **Fix 2:** Try calibrating by running the app in a quiet room first.

---
