"""
Entry point for the DriverGuard application.

Usage:
    python run.py

This script creates the Flask app using the application factory
and starts the development server on http://localhost:5000.
"""

from driverguard.app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n[*] DriverGuard API starting...")
    print("[*] Health check:  http://localhost:5000/api/v1/health")
    print("[*] Drivers API:   http://localhost:5000/api/v1/drivers\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
