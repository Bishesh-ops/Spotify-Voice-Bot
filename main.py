"""
Main entry point for the Spotify Voice Control Bot.

This script imports and runs the application from the 'spotify_bot' package.
"""
import sys
import logging
import tkinter as tk
from tkinter import messagebox

# We now import *from* our new package
try:
    from spotify_bot.config import AppConfig
    from spotify_bot.ui import SpotifyBotUI
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import modules: {e}\nPlease ensure all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    messagebox.showerror("Fatal Error", f"An unexpected error occurred on startup: {e}")
    sys.exit(1)


if __name__ == "__main__":
    try:
        # 1. Load configuration
        app_config = AppConfig.from_env()
        
        # 2. Initialize and run the UI
        app = SpotifyBotUI(app_config)
        app.mainloop()
        
    except ValueError as e:
        # This catches missing .env variables
        logging.critical(f"Configuration Error: {e}")
        messagebox.showerror("Configuration Error", f"Fatal error on startup: {e}\nPlease check your .env file.")
    except Exception as e:
        # Catchall for any other startup crash
        logging.critical(f"Unhandled exception on startup: {e}", exc_info=True)
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}")