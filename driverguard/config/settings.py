"""
Application configuration classes.

Each class represents an environment (development, testing, production).
Flask loads one of these via app.config.from_object().
"""

import os


class BaseConfig:
    """Base configuration shared across all environments."""

    # SECRET_KEY is used by Flask for session signing and CSRF protection.
    # os.environ.get() reads from environment variables — never hardcode secrets.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # When True, Flask returns pretty-printed JSON (easier to read during development).
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    """Development-specific configuration."""

    DEBUG = True  # Enables auto-reload and detailed error pages


class TestingConfig(BaseConfig):
    """Testing-specific configuration."""

    TESTING = True  # Tells Flask this is a test environment


class ProductionConfig(BaseConfig):
    """Production-specific configuration."""

    DEBUG = False
    TESTING = False


# Dictionary to look up config by name string
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
