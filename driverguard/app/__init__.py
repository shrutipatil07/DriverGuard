"""
Application Factory for DriverGuard.

This module contains the create_app() function — the single entry point
that builds, configures, and returns a Flask application instance.
"""

import os

from flask import Flask

from driverguard.config.settings import config_by_name


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name: One of 'development', 'testing', 'production'.
                     Defaults to the FLASK_ENV environment variable,
                     or 'development' if not set.

    Returns:
        A fully configured Flask application instance.
    """
    # --- Step 1: Determine which configuration to use ---
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    # --- Step 2: Create the Flask application instance ---
    # __name__ tells Flask where to find templates and static files
    app = Flask(__name__)

    # --- Step 3: Load configuration from our settings module ---
    app.config.from_object(config_by_name[config_name])

    # --- Step 4: Initialize SQLite Database ---
    from driverguard.app.database import init_app
    init_app(app)

    # --- Step 5: Register Blueprints (route groups) ---
    from driverguard.app.routes.health import health_bp
    from driverguard.app.routes.drivers import drivers_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(drivers_bp)

    # --- Step 6: Return the configured application ---
    return app
