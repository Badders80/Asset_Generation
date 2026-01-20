import logging
import sys
import os

def setup_logging(log_file="asset_gen.log", level=logging.INFO):
    """Configures logging to both console and a file."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger()
    logger.setLevel(level)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

class ComfyUIError(Exception):
    """Base class for exceptions in this module."""
    pass

class ConnectionError(ComfyUIError):
    """Raised when there is a network-level issue."""
    pass

class APIError(ComfyUIError):
    """Raised when the ComfyUI API returns an error."""
    def __init__(self, message, code=None, details=None):
        super().__init__(message)
        self.code = code
        self.details = details

def handle_fatal_error(error, message="A fatal error occurred"):
    """Logs the error and exits the script."""
    logger = logging.getLogger(__name__)
    if isinstance(error, APIError):
        logger.error(f"❌ {message}: {error} (Code: {error.code})")
        if error.details:
            logger.error(f"📝 Details: {error.details}")
    else:
        logger.error(f"❌ {message}: {error}")

    sys.exit(1)
