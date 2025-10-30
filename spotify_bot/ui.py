"""
Main UI for the Spotify Voice Control Bot (v2.0).
Integrates all refactored services and handlers.
"""
import logging
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --- FIX: Add dots for all relative imports ---
from .logger_setup import setup_logging
from .config import AppConfig
from .spotify_service import SpotifyService, AuthenticationError
from .command_handler import CommandHandler
from .voice_handler import VoiceHandler
from .feedback_handler import FeedbackHandler
# --- Custom UI Log Handler ---
class QueueLogHandler(logging.Handler):
    """Sends log records to a queue for the UI."""
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))


class SpotifyBotUI(tk.Tk):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.ui_config = config.ui
        
        # --- Setup Logging ---
        self.log_queue = queue.Queue()
        setup_logging(
            log_level=config.log_level,
            log_file=config.log_file,
            ui_log_queue=self.log_queue
        )
        self.logger = logging.getLogger(__name__)

        # --- Initialize Services ---
        try:
            self.spotify_service = SpotifyService(config.spotify)
            auth_success, username = self.spotify_service.check_auth()
            if not auth_success:
                raise AuthenticationError(username)
        except Exception as e:
            self.logger.critical(f"Fatal Error: {e}")
            messagebox.showerror("Fatal Error", f"Failed to authenticate with Spotify: {e}\nSee log for details. Exiting.")
            sys.exit(1)

        self.command_handler = CommandHandler(self.spotify_service)
        self.voice_handler = VoiceHandler()
        self.feedback_handler = FeedbackHandler(
            speech_rate=self.ui_config.speech_rate,
            enable_audio=True, # You can tie this to config
            enable_voice=True  # You can tie this to config
        )
        
        # --- Build UI ---
        self.title("Spotify Voice Control Bot v2.0")
        self.geometry(f"{self.ui_config.window_width}x{self.ui_config.window_height}")
        self.configure(bg=self.ui_config.background_color)
        
        self.build_widgets()
        
        # Start queue poller
        self.after(100, self.poll_log_queue)
        
        # Set protocol for closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.logger.info(f"Welcome, {username}! UI Initialized.")

    def build_widgets(self):
        """Create and place all UI widgets."""
        
        # --- Status Label ---
        self.status_label = tk.Label(
            self, text="Welcome! Waiting for command...", font=("Helvetica", 14),
            anchor="w", bg=self.ui_config.primary_color, 
            fg=self.ui_config.text_color, relief="flat", padx=10
        )
        self.status_label.pack(fill="x", pady=5)

        # --- Command Frame ---
        command_frame = tk.Frame(self, bg=self.ui_config.background_color)
        command_frame.pack(fill="x", padx=10, pady=5)
        
        # Voice Button
        self.voice_button = tk.Button(
            command_frame, text="🎤 Voice Command", command=self.start_voice_command,
            font=("Helvetica", 12, "bold"), bg=self.ui_config.primary_color,
            fg=self.ui_config.text_color, relief="raised", borderwidth=3
        )
        self.voice_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        if not self.voice_handler.is_microphone_available():
            self.voice_button.config(text="🎤 No Microphone", state="disabled")

        # --- Text Input Frame ---
        text_frame = tk.Frame(self, bg=self.ui_config.background_color)
        text_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.command_entry = tk.Entry(
            text_frame, font=("Helvetica", 12), width=40,
            bg=self.ui_config.secondary_color, fg=self.ui_config.text_color,
            insertbackground=self.ui_config.text_color
        )
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.command_entry.bind("<Return>", self.start_text_command_event)

        self.submit_button = tk.Button(
            text_frame, text="Submit", command=self.start_text_command,
            font=("Helvetica", 10, "bold"), bg=self.ui_config.primary_color,
            fg=self.ui_config.text_color
        )
        self.submit_button.pack(side="left")

        # --- Log Frame ---
        log_frame = tk.Frame(self, bg=self.ui_config.secondary_color)
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, font=("Consolas", 10), bg="#0d0d0d", 
            fg=self.ui_config.text_color, wrap="word", state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure tags for log colors
        self.log_text.tag_configure("INFO", foreground=self.ui_config.text_color)
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("WARN", foreground="orange")
        self.log_text.tag_configure("SUCCESS", foreground=self.ui_config.primary_color)
        
    def start_voice_command(self):
        """Handle voice command button click."""
        self.update_status("Listening...")
        self.set_ui_state("disabled")
        # Run in a thread to not block UI
        threading.Thread(target=self.run_voice_command, daemon=True).start()

    def run_voice_command(self):
        """Worker thread for voice commands."""
        success, command, error_msg = self.voice_handler.listen()
        
        if not success:
            self.handle_command_result(False, error_msg, is_voice=True)
            return

        if command:
            self.logger.info(f"Voice recognized: '{command}'")
            self.update_status(f"Processing: {command}")
            cmd_success, cmd_msg = self.command_handler.execute(command)
            self.handle_command_result(cmd_success, cmd_msg, is_voice=True)
        else:
            self.handle_command_result(False, "No command recognized.", is_voice=True)

    def start_text_command_event(self, event=None):
        self.start_text_command()

    def start_text_command(self):
        """Handle text command submit button click."""
        command = self.command_entry.get().strip()
        if not command:
            return
            
        self.update_status(f"Processing: {command}")
        self.set_ui_state("disabled")
        self.command_entry.delete(0, 'end')
        
        # Run in a thread to not block UI
        threading.Thread(target=self.run_text_command, args=(command,), daemon=True).start()

    def run_text_command(self, command: str):
        """Worker thread for text commands."""
        try:
            cmd_success, cmd_msg = self.command_handler.execute(command)
            self.handle_command_result(cmd_success, cmd_msg)
        except Exception as e:
            self.logger.error(f"Unhandled error executing command: {e}")
            self.handle_command_result(False, f"An unexpected error occurred: {e}")

    def handle_command_result(self, success: bool, message: str, is_voice: bool = False):
        """Update UI and provide feedback based on command outcome."""
        if success:
            self.logger.info(message)
            self.update_status(f"Success: {message}", "SUCCESS")
            self.feedback_handler.play_sound(success=True)
            if is_voice: self.feedback_handler.speak(message)
        else:
            self.logger.error(message)
            self.update_status(f"Error: {message}", "ERROR")
            self.feedback_handler.play_sound(success=False)
            if is_voice: self.feedback_handler.speak(message)
            
        self.set_ui_state("normal")

    def set_ui_state(self, state: str):
        """Disable or enable UI elements."""
        self.voice_button.config(state=state)
        self.submit_button.config(state=state)
        self.command_entry.config(state=state)

    def update_status(self, message: str, tag: str = "INFO"):
        """Update the top status label."""
        self.status_label.config(text=message)
        # Change color based on tag
        if tag == "SUCCESS":
            self.status_label.config(bg=self.ui_config.primary_color)
        elif tag == "ERROR":
            self.status_label.config(bg="red")
        else:
            self.status_label.config(bg=self.ui_config.primary_color)

    def log_to_ui(self, message_record: logging.LogRecord): # <-- FIX 1
        """Append a message to the text log area."""
        self.log_text.config(state="normal")
        
        # --- FIX 2: Check the attributes of the LogRecord object ---
        log_level = message_record.levelname
        log_message = message_record.getMessage()

        # Determine tag
        if log_level == "ERROR":
            tag = "ERROR"
        elif log_level == "WARNING":
            tag = "WARN"
        elif "✓" in log_message: # You can still check the message string
            tag = "SUCCESS"
        else:
            tag = "INFO"
            
        # Format message
        formatted_message = log_message.replace("✓ ", "") + "\n"
        
        self.log_text.insert(tk.END, formatted_message, tag)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def poll_log_queue(self):
        """Check the log queue for new messages and display them."""
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.log_to_ui(record) # 'record' is a LogRecord object
        self.after(100, self.poll_log_queue)

    def on_closing(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.logger.info("Shutting down application...")
            self.feedback_handler.shutdown()
            self.destroy()

# --- Main execution ---
if __name__ == "__main__":
    try:
        app_config = AppConfig.from_env()
        app = SpotifyBotUI(app_config)
        app.mainloop()
    except ValueError as e:
        logging.critical(f"Configuration Error: {e}")
        messagebox.showerror("Configuration Error", f"Fatal error on startup: {e}\nPlease check your .env file.")
    except Exception as e:
        logging.critical(f"Unhandled exception on startup: {e}")
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}")