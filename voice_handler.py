"""Voice recognition handler with improved error handling."""
import logging
import speech_recognition as sr
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class VoiceRecognitionError(Exception):
    """Base exception for voice recognition errors."""
    pass

class VoiceHandler:
    """Handles voice recognition functionality."""
    
    def __init__(self, timeout: int = 5, phrase_time_limit: int = 10):
        """Initialize voice handler."""
        self.recognizer = sr.Recognizer()
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        
        # Adjust for ambient noise on initialization
        try:
            with sr.Microphone() as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Microphone calibration complete")
        except Exception as e:
            logger.error(f"Failed to calibrate microphone: {e}")
    
    def listen(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Listen for voice command. Returns (success, command_text, error_message)"""
        try:
            with sr.Microphone() as source:
                logger.info("Listening for voice command...")
                
                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.timeout,
                        phrase_time_limit=self.phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    logger.warning("Listening timed out - no speech detected")
                    return False, None, "No speech detected. Please try again."
                
                try:
                    command = self.recognizer.recognize_google(audio).lower()
                    logger.info(f"Recognized command: {command}")
                    return True, command, None
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    return False, None, "Could not understand audio. Please speak clearly."
                except sr.RequestError as e:
                    logger.error(f"Recognition service error: {e}")
                    return False, None, "Speech recognition service unavailable."
                
        except OSError as e:
            logger.error(f"Microphone error: {e}")
            return False, None, "Microphone not found or not accessible."
        except Exception as e:
            logger.error(f"Unexpected voice recognition error: {e}")
            return False, None, f"Unexpected error: {str(e)}"
    
    def is_microphone_available(self) -> bool:
        """Check if microphone is available."""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            return len(mic_list) > 0
        except Exception as e:
            logger.error(f"Error checking microphone: {e}")
            return False