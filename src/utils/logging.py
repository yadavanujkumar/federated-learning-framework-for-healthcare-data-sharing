# src/utils/logging.py

"""
Structured Logging Utility for Federated Learning Framework

This module provides a production-grade, structured logging setup for the Federated Learning Framework.
It supports log levels, correlation IDs for distributed tracing, and integration with log aggregation systems.

Features:
- Structured JSON logging for compatibility with modern log aggregation systems (e.g., ELK, Datadog, Splunk).
- Correlation ID support for distributed tracing across services.
- Configurable log levels via environment variables.
- Thread-safe and multiprocessing-safe logging.
- Graceful handling of edge cases and fallback mechanisms.
- Integration-ready for containerized environments (e.g., Docker).

Author: Senior Software Engineer - Production Systems Specialist
"""

import logging
import logging.config
import os
import sys
import threading
import uuid
from typing import Any, Dict, Optional
import json

# Constants for log levels
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Default log level
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if DEFAULT_LOG_LEVEL not in LOG_LEVELS:
    DEFAULT_LOG_LEVEL = "INFO"

# Correlation ID storage (thread-local for thread safety)
_thread_local = threading.local()


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter to inject correlation IDs into log records.
    Ensures that each log message includes a unique identifier for tracing.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


def get_correlation_id() -> str:
    """
    Retrieve the current thread's correlation ID. If none exists, generate a new one.

    Returns:
        str: The correlation ID.
    """
    if not hasattr(_thread_local, "correlation_id"):
        _thread_local.correlation_id = str(uuid.uuid4())
    return _thread_local.correlation_id


def set_correlation_id(correlation_id: Optional[str] = None) -> None:
    """
    Set a correlation ID for the current thread.

    Args:
        correlation_id (Optional[str]): The correlation ID to set. If None, a new one is generated.
    """
    _thread_local.correlation_id = correlation_id or str(uuid.uuid4())


def clear_correlation_id() -> None:
    """
    Clear the correlation ID for the current thread.
    """
    if hasattr(_thread_local, "correlation_id"):
        del _thread_local.correlation_id


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Converts log records into JSON format for compatibility with log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", None),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Include exception info if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


def configure_logging(log_level: str = DEFAULT_LOG_LEVEL) -> None:
    """
    Configure the logging system with structured JSON logging and correlation ID support.

    Args:
        log_level (str): The log level to use. Defaults to the value of the LOG_LEVEL environment variable.
    """
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            }
        },
        "filters": {
            "correlation_id": {
                "()": CorrelationIdFilter,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "filters": ["correlation_id"],
                "stream": sys.stdout,
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(logging_config)


# Initialize logging on module import
configure_logging()

# Example usage
if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # Set a correlation ID for this thread
    set_correlation_id("test-correlation-id")

    logger.info("This is an info message.")
    logger.error("This is an error message with additional context.", extra={"context": "example"})

    # Clear the correlation ID
    clear_correlation_id()