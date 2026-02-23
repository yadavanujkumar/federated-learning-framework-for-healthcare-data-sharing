"""
Production-ready configuration file for the Federated Learning Framework for Healthcare Data Sharing.

This file manages environment-specific settings, secrets, and feature flags. It is designed to be secure,
scalable, and optimized for performance. Sensitive data is sourced from environment variables, and
defaults are provided for non-sensitive configurations. Ensure all required environment variables are set
before deploying.

Environment-specific settings are loaded dynamically based on the `ENVIRONMENT` variable.
"""

import os
from pathlib import Path

# Load environment variable helper
def get_env_variable(var_name, default=None, required=False):
    """
    Helper function to fetch environment variables.
    Raises an error if a required variable is not set.
    """
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    return value


# Base Configuration
class BaseConfig:
    """
    Base configuration shared across all environments.
    """
    # Application settings
    APP_NAME = "FederatedLearningFramework"
    DEBUG = False  # Disable debug mode in production
    LOG_LEVEL = "INFO"  # Default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Database settings
    DB_HOST = get_env_variable("DB_HOST", "localhost")
    DB_PORT = int(get_env_variable("DB_PORT", 5432))
    DB_NAME = get_env_variable("DB_NAME", "federated_learning")
    DB_USER = get_env_variable("DB_USER", "admin")
    DB_PASSWORD = get_env_variable("DB_PASSWORD", required=True)  # Sensitive, must be set in env vars

    # Redis (for caching, task queues, etc.)
    REDIS_HOST = get_env_variable("REDIS_HOST", "localhost")
    REDIS_PORT = int(get_env_variable("REDIS_PORT", 6379))
    REDIS_PASSWORD = get_env_variable("REDIS_PASSWORD", None)  # Optional, depending on setup

    # Security settings
    SECRET_KEY = get_env_variable("SECRET_KEY", required=True)  # Sensitive, must be set in env vars
    ALLOWED_HOSTS = get_env_variable("ALLOWED_HOSTS", "*").split(",")  # Comma-separated list of allowed hosts
    CSRF_TRUSTED_ORIGINS = get_env_variable("CSRF_TRUSTED_ORIGINS", "").split(",")  # Trusted origins for CSRF protection

    # Performance tuning
    WORKER_CONNECTIONS = int(get_env_variable("WORKER_CONNECTIONS", 1000))  # Max connections per worker
    TIMEOUT = int(get_env_variable("TIMEOUT", 30))  # Request timeout in seconds

    # Feature flags
    ENABLE_FEATURE_X = get_env_variable("ENABLE_FEATURE_X", "false").lower() == "true"  # Example feature flag
    ENABLE_FEATURE_Y = get_env_variable("ENABLE_FEATURE_Y", "false").lower() == "true"

    # File storage
    FILE_STORAGE_PATH = get_env_variable("FILE_STORAGE_PATH", "/data/files")  # Default file storage path

    # Monitoring and observability
    ENABLE_METRICS = get_env_variable("ENABLE_METRICS", "true").lower() == "true"  # Enable Prometheus metrics
    ENABLE_TRACING = get_env_variable("ENABLE_TRACING", "false").lower() == "true"  # Enable distributed tracing

    # Default paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_FILES_DIR = BASE_DIR / "static"
    MEDIA_FILES_DIR = BASE_DIR / "media"


# Development Configuration
class DevelopmentConfig(BaseConfig):
    """
    Development-specific settings.
    """
    DEBUG = True  # Enable debug mode for development
    LOG_LEVEL = "DEBUG"  # Verbose logging for debugging
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]  # Restrict hosts in development
    ENABLE_FEATURE_X = True  # Enable experimental features in development


# Staging Configuration
class StagingConfig(BaseConfig):
    """
    Staging-specific settings.
    """
    DEBUG = False  # Disable debug mode in staging
    LOG_LEVEL = "INFO"  # Standard logging level
    ALLOWED_HOSTS = get_env_variable("STAGING_ALLOWED_HOSTS", "staging.example.com").split(",")
    ENABLE_METRICS = True  # Enable metrics for staging environment


# Production Configuration
class ProductionConfig(BaseConfig):
    """
    Production-specific settings.
    """
    DEBUG = False  # Debug mode must always be disabled in production
    LOG_LEVEL = "WARNING"  # Log only warnings and errors
    ALLOWED_HOSTS = get_env_variable("PROD_ALLOWED_HOSTS", "example.com").split(",")
    ENABLE_METRICS = True  # Enable metrics for production
    ENABLE_TRACING = True  # Enable tracing in production


# Environment Loader
def get_config():
    """
    Load the appropriate configuration class based on the `ENVIRONMENT` variable.
    """
    environment = get_env_variable("ENVIRONMENT", "development").lower()
    if environment == "development":
        return DevelopmentConfig()
    elif environment == "staging":
        return StagingConfig()
    elif environment == "production":
        return ProductionConfig()
    else:
        raise ValueError(f"Invalid ENVIRONMENT value: {environment}")


# Export the selected configuration
config = get_config()