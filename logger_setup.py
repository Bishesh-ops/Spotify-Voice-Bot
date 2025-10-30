"""
Centralized logging setup for the Spotify Voice Bot.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "spotify_bot.log",
    max_bytes: int = 1024 * 1024,  # 1 MB
    backup_count: int = 5,
    ui_log_queue: Optional[logging.Queue] = None
):
    """
    Configures the root logger for the application.
    
    Args:
        log_level (str): The minimum logging level (e.g., "DEBUG", "INFO").
        log_file (str): The name of the file to log to.
        max_bytes (int): Max size of the log file before rotating.
        backup_count (int): Number of old log files to keep.
        ui_log_queue (Optional[logging.Queue]): A queue to send logs to the UI.
    """
    level = logging.getLevelName(log_level.upper())
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # --- Console Handler ---
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # --- Rotating File Handler ---
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # --- UI Queue Handler ---
    if ui_log_queue:
        queue_handler = logging.handlers.QueueHandler(ui_log_queue)
        queue_handler.setLevel(level)
        # Use a simple formatter for the UI
        ui_formatter = logging.Formatter("✓ %(message)s")
        queue_handler.setFormatter(ui_formatter)
        root_logger.addHandler(queue_handler)

    logging.info("Logging configured successfully")
    logging.info(f"Log level set to {log_level}")