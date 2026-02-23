# src/utils/exceptions.py

"""
Custom exception classes for the Federated Learning Framework for Healthcare Data Sharing.

This module defines domain-specific exceptions to handle errors gracefully, ensuring
robust error handling, logging, and recovery mechanisms in production systems.

Features:
- Comprehensive type safety with type hints.
- Advanced logging integration for monitoring and debugging.
- Thread-safe and memory-efficient design.
- Adheres to SOLID principles for maintainability and extensibility.
"""

from typing import Optional
import logging
import traceback

# Configure a dedicated logger for exceptions
logger = logging.getLogger("federated_learning.exceptions")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class BaseFrameworkException(Exception):
    """
    Base class for all custom exceptions in the Federated Learning Framework.
    Provides advanced logging and debugging capabilities.
    """

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """
        Initialize the exception with a message and optional details.

        Args:
            message (str): A human-readable description of the error.
            details (Optional[str]): Additional context or details about the error.
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.log_exception()

    def log_exception(self) -> None:
        """
        Logs the exception details, including the stack trace, for debugging and monitoring.
        """
        error_details = f"{self.__class__.__name__}: {self.message}"
        if self.details:
            error_details += f" | Details: {self.details}"
        logger.error(error_details)
        logger.debug("Stack Trace:\n%s", traceback.format_exc())


class DataValidationException(BaseFrameworkException):
    """
    Exception raised for errors in data validation during federated learning operations.
    """

    def __init__(self, message: str, invalid_data: Optional[dict] = None) -> None:
        """
        Initialize the exception with a message and optional invalid data details.

        Args:
            message (str): A human-readable description of the validation error.
            invalid_data (Optional[dict]): The invalid data that caused the error.
        """
        self.invalid_data = invalid_data
        details = f"Invalid data: {invalid_data}" if invalid_data else None
        super().__init__(message, details)


class ModelTrainingException(BaseFrameworkException):
    """
    Exception raised for errors during model training in the federated learning process.
    """

    def __init__(self, message: str, model_id: Optional[str] = None) -> None:
        """
        Initialize the exception with a message and optional model ID.

        Args:
            message (str): A human-readable description of the training error.
            model_id (Optional[str]): The ID of the model being trained.
        """
        self.model_id = model_id
        details = f"Model ID: {model_id}" if model_id else None
        super().__init__(message, details)


class CommunicationException(BaseFrameworkException):
    """
    Exception raised for errors in communication between federated learning nodes.
    """

    def __init__(self, message: str, node_id: Optional[str] = None) -> None:
        """
        Initialize the exception with a message and optional node ID.

        Args:
            message (str): A human-readable description of the communication error.
            node_id (Optional[str]): The ID of the node involved in the communication error.
        """
        self.node_id = node_id
        details = f"Node ID: {node_id}" if node_id else None
        super().__init__(message, details)


class ConfigurationException(BaseFrameworkException):
    """
    Exception raised for errors in configuration or environment setup.
    """

    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        """
        Initialize the exception with a message and optional configuration key.

        Args:
            message (str): A human-readable description of the configuration error.
            config_key (Optional[str]): The configuration key that caused the error.
        """
        self.config_key = config_key
        details = f"Configuration Key: {config_key}" if config_key else None
        super().__init__(message, details)


class SecurityException(BaseFrameworkException):
    """
    Exception raised for security-related errors, such as authentication or data breaches.
    """

    def __init__(self, message: str, user_id: Optional[str] = None) -> None:
        """
        Initialize the exception with a message and optional user ID.

        Args:
            message (str): A human-readable description of the security error.
            user_id (Optional[str]): The ID of the user involved in the security issue.
        """
        self.user_id = user_id
        details = f"User ID: {user_id}" if user_id else None
        super().__init__(message, details)


class ResourceLimitException(BaseFrameworkException):
    """
    Exception raised when resource limits (e.g., memory, CPU, disk) are exceeded.
    """

    def __init__(self, message: str, resource_type: Optional[str] = None) -> None:
        """
        Initialize the exception with a message and optional resource type.

        Args:
            message (str): A human-readable description of the resource limit error.
            resource_type (Optional[str]): The type of resource that exceeded its limit.
        """
        self.resource_type = resource_type
        details = f"Resource Type: {resource_type}" if resource_type else None
        super().__init__(message, details)


class DependencyException(BaseFrameworkException):
    """
    Exception raised for errors related to missing or incompatible dependencies.
    """

    def __init__(self, message: str, dependency_name: Optional[str] = None) -> None:
        """
        Initialize the exception with a message and optional dependency name.

        Args:
            message (str): A human-readable description of the dependency error.
            dependency_name (Optional[str]): The name of the dependency that caused the error.
        """
        self.dependency_name = dependency_name
        details = f"Dependency Name: {dependency_name}" if dependency_name else None
        super().__init__(message, details)


# Example usage of the custom exceptions
if __name__ == "__main__":
    try:
        raise DataValidationException("Invalid patient data", {"patient_id": 123, "error": "Missing age"})
    except DataValidationException as e:
        logger.exception("Handled DataValidationException: %s", e)

    try:
        raise SecurityException("Unauthorized access attempt detected", user_id="user_456")
    except SecurityException as e:
        logger.exception("Handled SecurityException: %s", e)