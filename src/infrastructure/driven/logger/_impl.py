import logging
from datetime import datetime
from pathlib import Path

from src.domain.logger_port import LoggerPort

class LoggerAdapter(LoggerPort):
    def __init__(self, log_dir: str = "logs"):
        """
        Initializes the logger.
        1. Creates the log directory if it doesn't exist.
        2. Sets up a unique file handler based on the current timestamp.
        3. Sets up a console handler for stdout.
        """
        # Create logs directory.
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename (e.g., run_2023-10-27_10-30-05.log).
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = self.log_dir / f"run_{current_time}.log"

        # Configure the internal logger.
        # Use a specific name to ensure isolation if needed.
        self._logger = logging.getLogger("AppLogger")
        self._logger.setLevel(logging.INFO)

        # Clear existing handlers to prevent duplication if re-instantiated.
        self._logger.handlers = []

        # Create log format.
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Create file handler.
        file_handler = logging.FileHandler(str(log_file), mode='w')
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        # Create console handler.
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        self.info(f"Logger initialized. Writing to: '{log_file}'.")

    def info(self, message: str):
        self._logger.info(message)

    def warn(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

logger = LoggerAdapter()
