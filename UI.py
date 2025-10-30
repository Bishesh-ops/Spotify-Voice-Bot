import tkinter as tk
from tkinter import ttk, messagebox
import threading
from spotify_bot import voice_control, list_playlists, search_and_play
import logging
import winsound
import pyttsx3  # Text-to-speech library
import queue
import time


class SpotifyBotUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spotify Voice Control Bot")
        self.geometry("700x600")
        self.configure(bg="#121212")

        self.queue = queue.Queue()

        self.engine = pyttsx3.init()  # Initialize the text-to-speech engine
        self.engine.setProperty('rate', 150)  # Adjust speech rate

        # Status label for dynamic updates
        self.status_label = tk.Label(self, text="Welcome to Spotify Bot", font=("Helvetica", 14), anchor="w",
                                     bg="#1DB954", fg="white", relief="flat")
        self.status_label.pack(fill="x", padx=5, pady=5)

        # Voice control button with improved styling
        self.voice_button = tk.Button(self, text="🎤 Voice Command", command=self.start_voice_control,
                                      font=("Helvetica", 12, "bold"), bg="#1DB954", fg="white", relief="raised",
                                      borderwidth=3)
        self.voice_button.pack(pady=10)

        # Command entry for manual typing
        command_frame = tk.Frame(self, bg="#121212")
        command_frame.pack(padx=10, pady=5)

        self.command_entry = tk.Entry(command_frame, font=("Helvetica", 12), width=40)
        self.command_entry.pack(side="left", padx=5)

        self.submit_button = tk.Button(command_frame, text="Submit Command", command=self.submit_command,
                                       font=("Helvetica", 10, "bold"), bg="#1DB954", fg="white")
        self.submit_button.pack(side="left", padx=5)

        # Logging frame for real-time feedback
        log_frame = tk.Frame(self, bg="#1c1c1c")
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_text = tk.Text(log_frame, font=("Consolas", 10), bg="#0d0d0d", fg="white", wrap="word",
                                state="disabled", height=12)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)
        self.log_scrollbar.pack(side="right", fill="y")

        # Frame for instructions
        instructions_frame = tk.Frame(self, bg="#121212")
        instructions_frame.pack(padx=10, pady=10)

        self.instructions_text = ("Available Voice Commands:\n"
                                  "- 'Play [song name]' to play a track\n"
                                  "- 'Play playlist [playlist name]' to play your playlist\n"
                                  "- 'Play artist [artist name]' to play an artist\n"
                                  "- 'Pause' to pause playback\n"
                                  "- 'Resume' to resume playback\n"
                                  "- 'Skip' to skip to the next track\n"
                                  "- 'Shuffle on/off' to toggle shuffle mode\n"
                                  "- 'Repeat track/context/off' to set repeat mode\n"
                                  "- 'Volume [level]' to set volume\n"
                                  "- 'Create playlist [name]' to create a playlist\n"
                                  "- 'Add to playlist [playlist name] [song name]' to add a song")

        # Help menu
        menu = tk.Menu(self)
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="Instructions", command=self.show_instructions)
        help_menu.add_command(label="Troubleshooting", command=self.show_troubleshooting)
        menu.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu)

    def start_voice_control(self):
        self.update_status("Listening for voice commands...")
        self.disable_buttons(True)
        threading.Thread(target=self.run_voice_control, daemon=True).start()

    def run_voice_control(self):
        try:
            self.update_status("Processing voice command...")
            self.log_message("Voice control activated.")
            self.play_feedback_sound(success=True)
            self.speak("Processing voice command.")
            voice_control()  # Logs internally
            self.update_status("Voice command processed.")
            self.log_message("Voice command processed successfully.")
            self.speak("Voice command processed successfully.")
        except Exception as e:
            logging.error(f"Error in voice control: {e}")
            self.update_status("Error processing command. Please try again.")
            self.log_message(f"Error: {e}")
            self.play_feedback_sound(success=False)
            self.speak("Error processing command. Please try again.")
        finally:
            self.disable_buttons(False)

    def submit_command(self):
        command = self.command_entry.get().strip()
        if command:
            self.update_status(f"Processing command: {command}")
            self.disable_buttons(True)
            threading.Thread(target=self.execute_text_command, args=(command,), daemon=True).start()

    def execute_text_command(self, command):
        try:
            self.log_message(f"Executing text command: {command}")
            search_and_play(command)  # Assumes handling search/play logic
            self.update_status(f"Now playing: {command}")
            self.log_message(f"Now playing: {command}")
            self.play_feedback_sound(success=True)
            self.speak(f"Now playing: {command}")
        except Exception as e:
            logging.error(f"Error processing text command: {e}")
            self.update_status("Failed to process command.")
            self.log_message(f"Error: {e}")
            self.play_feedback_sound(success=False)
            self.speak("Failed to process command.")
        finally:
            self.disable_buttons(False)

    def update_status(self, message):
        self.status_label.config(text=message)

    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def play_feedback_sound(self, success=True):
        if success:
            winsound.Beep(1000, 200)  # Short high-pitch beep
        else:
            winsound.Beep(500, 400)  # Longer low-pitch beep

    def speak(self, message):
        self.engine.say(message)
        self.engine.runAndWait()

    def disable_buttons(self, disable=True):
        self.voice_button.config(state="disabled" if disable else "normal")
        self.submit_button.config(state="disabled" if disable else "normal")

    def show_instructions(self):
        messagebox.showinfo("Instructions", self.instructions_text)

    def show_troubleshooting(self):
        troubleshooting_text = ("Troubleshooting Tips:\n"
                                "- Ensure your Spotify app is open and running.\n"
                                "- Check your internet connection.\n"
                                "- Ensure the bot has the correct permissions in Spotify settings.\n"
                                "- Retry the command if it fails.")
        messagebox.showinfo("Troubleshooting", troubleshooting_text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app = SpotifyBotUI()
    app.mainloop()
