import csv
import os
import signal
from datetime import datetime

LOG_FILE = 'shutdown_log.csv'

def log_shutdown(reason="shutdown"):
    """Logs a shutdown event to the CSV file."""
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['timestamp', 'reason'])
        writer.writerow([datetime.now().isoformat(), reason])

def signal_handler(signum, frame):
    """Handles signals and logs the shutdown."""
    log_shutdown(f'signal_{signum}')
    # Exit the program after logging
    exit(1)

def setup_signal_handlers():
    """Sets up the logging for unexpected shutdowns."""
    # Register signal handlers for unexpected shutdowns
    signal.signal(signal.SIGTERM, signal_handler)
    # Add other signals if needed, e.g., signal.SIGINT for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)