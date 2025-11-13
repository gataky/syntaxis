"""Centralized logging configuration for Syntaxis."""

import logging
import os
import sys
from functools import wraps
from time import time
from typing import Any, Callable, TypeVar, cast

# Type variable for decorator
F = TypeVar('F', bound=Callable[..., Any])


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for colored logging."""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.GRAY,
        logging.INFO: Colors.CYAN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD,
    }

    def __init__(self, fmt: str):
        super().__init__(fmt)
        self._use_colors = sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        if self._use_colors:
            # Add color to level name
            levelname = record.levelname
            color = self.LEVEL_COLORS.get(record.levelno, '')
            record.levelname = f"{color}{levelname}{Colors.RESET}"

        result = super().format(record)

        # Reset levelname for subsequent formatters
        record.levelname = record.levelname.replace(Colors.RESET, '').replace(
            Colors.GRAY, ''
        ).replace(Colors.CYAN, '').replace(Colors.YELLOW, '').replace(
            Colors.RED, ''
        ).replace(Colors.BOLD, '')

        return result


def setup_logging() -> None:
    """Configure logging for the entire application.

    Reads SYNTAXIS_LOG_LEVEL environment variable (defaults to INFO).
    Sets up colored console output with detailed format.

    Call this once at application startup.
    """
    # Get log level from environment variable
    level_name = os.environ.get('SYNTAXIS_LOG_LEVEL', 'INFO').upper()
    level = getattr(logging, level_name, logging.INFO)

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create formatter with colors
    formatter = ColoredFormatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(funcName)s:%(lineno)d] %(message)s'
    )
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()  # Remove any existing handlers
    root_logger.addHandler(handler)

    # Log the initialization
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging initialized at {level_name} level")


def _truncate(value: Any, max_length: int = 100) -> str:
    """Truncate string representation of value to max_length."""
    str_value = str(value)
    if len(str_value) > max_length:
        return str_value[:max_length] + "..."
    return str_value


def log_calls(func: F) -> F:
    """Decorator that logs function entry, exit, and exceptions.

    Logs at DEBUG level:
    - Function entry with arguments
    - Function exit with return value and execution time

    Logs at ERROR level:
    - Exceptions with type and message (then re-raises)

    Args are truncated to 100 chars to prevent log spam.

    Usage:
        @log_calls
        def my_function(arg1, arg2):
            return result
    """
    # Skip logging for common dunder methods to reduce noise
    skip_methods = {'__init__', '__str__', '__repr__', '__eq__', '__hash__'}
    if func.__name__ in skip_methods:
        return func

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(func.__module__)
        func_name = func.__qualname__

        # Log entry with arguments
        args_repr = [_truncate(a) for a in args]
        kwargs_repr = [f"{k}={_truncate(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"→ {func_name}({signature})")

        start_time = time()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time() - start_time) * 1000

            # Log exit with return value and timing
            result_repr = _truncate(result)
            logger.debug(f"← {func_name} returned {result_repr} ({elapsed_ms:.2f}ms)")

            return result
        except Exception as e:
            elapsed_ms = (time() - start_time) * 1000
            logger.error(
                f"✗ {func_name} raised {type(e).__name__}: {e} ({elapsed_ms:.2f}ms)"
            )
            raise

    return cast(F, wrapper)
