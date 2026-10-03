"""
Health check endpoint.

Provides a simple endpoint to verify the API is running.
Used by monitoring tools, load balancers, and developers to
confirm the service is alive and responding.
"""

from datetime import datetime, timezone

from flask import Blueprint, jsonify

# Create a Blueprint named 'health'
# url_prefix means all routes in this blueprint start with /api/v1
health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /api/v1/health

    Returns a JSON response indicating the service is healthy.

    Response:
        200 OK
        {
            "status": "healthy",
            "service": "DriverGuard API",
            "version": "1.0.0",
            "timestamp": "2026-10-03T12:50:33Z"
        }
    """
    return jsonify({
        "status": "healthy",
        "service": "DriverGuard API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200
