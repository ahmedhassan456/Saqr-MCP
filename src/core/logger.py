import sys
from datetime import datetime
from loguru import logger as _logger
import threading
import time
import itertools
import sys
from contextlib import contextmanager


_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to above level"""
    global _print_level
    _print_level = print_level

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    return _logger


logger = define_log_level()


class LoadingAnimation:
    def __init__(self, description="Loading", animation_chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        self.description = description
        self.animation_chars = animation_chars
        self.running = False
        self.thread = None
        
    def _animate(self):
        for c in itertools.cycle(self.animation_chars):
            if not self.running:
                break
            sys.stdout.write(f'\r{self.description} {c} ')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(self.description) + 4) + '\r')
        sys.stdout.flush()
        
    def start(self, description=None):
        if description:
            self.description = description
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

@contextmanager
def loading_animation(description="Loading"):
    """Context manager for loading animation with success/failure feedback."""
    animation = LoadingAnimation(description)
    animation.start()
    try:
        yield
    except Exception:
        animation.stop()
        print(f"{description}: ✖ Failed")
        raise 
    else:
        animation.stop()
        print(f"{description}: ✔ Done")


if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")