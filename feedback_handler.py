"""
Cross-platform feedback handler (audio beeps and TTS).
Supports Windows, macOS, and Linux.
"""
import logging
import platform
import subprocess
import threading
from queue import Queue
from typing import Optional
import pyttsx3 # type: ignore
from pyttsx3.engine import Engine  # type: ignore  # <-- FIX: Ignore missing stub file

try:
    import winsound
except ImportError:
    winsound = None  # Non-Windows platform

logger = logging.getLogger(__name__)

class FeedbackHandler:
    """Handles audio and voice feedback."""
    
    def __init__(self, speech_rate: int = 150, enable_audio: bool = True, enable_voice: bool = True):
        self.system = platform.system()
        self.enable_audio = enable_audio
        self.enable_voice = enable_voice
        
        self.tts_queue: Queue[Optional[str]] = Queue()
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.engine: Optional[Engine] = None
        
        if self.enable_voice:
            try:
                self.engine = pyttsx3.init()# type: ignore
                if self.engine: # type: ignore
                    self.engine.setProperty('rate', speech_rate) # type: ignore
                    self.tts_thread.start()
                else:
                    raise Exception("pyttsx3.init() returned None")
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3: {e}. Voice feedback disabled.")
                self.enable_voice = False
                self.engine = None

    def _tts_worker(self):
        """Worker thread to process TTS messages from the queue."""
        while True:
            try:
                message = self.tts_queue.get()
                
                if message is None:  # Sentinel value to stop
                    break
                
                if self.engine:
                    self.engine.say(message) # type: ignore
                    self.engine.runAndWait()
                
                self.tts_queue.task_done()
            except Exception as e:
                logger.error(f"Error in TTS worker thread: {e}")

    def speak(self, message: str):
        """Add a message to the TTS queue to be spoken."""
        if not self.enable_voice or not self.engine:
            return
        self.tts_queue.put(message)

    def play_sound(self, success: bool = True):
        """Play a success or failure beep sound."""
        if not self.enable_audio:
            return
        
        try:
            if self.system == "Windows":
                if winsound:
                    freq = 1000 if success else 500
                    duration = 200 if success else 400
                    winsound.Beep(freq, duration)
                else:
                    logger.warning("winsound module not available on non-Windows platform.")
            elif self.system == "Darwin":  # macOS
                sound = "/System/Library/Sounds/Glass.aiff" if success else "/System/Library/Sounds/Basso.aiff"
                subprocess.call(["afplay", sound])
            else:  # Linux
                command = "paplay" # Assumes PulseAudio
                sound_file = "/usr/share/sounds/freedesktop/stereo/audio-volume-change.oga"
                subprocess.Popen([command, sound_file], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.warning(f"Failed to play feedback sound: {e}")

    def shutdown(self):
        """Signal the TTS thread to shut down."""
        if self.enable_voice and self.tts_thread.is_alive():
            self.tts_queue.put(None)
            self.tts_thread.join()