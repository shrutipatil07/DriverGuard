"""
Driver API Controller / Routes Layer.

Responsibilities of this HTTP layer:
1. Parse HTTP requests (JSON body, route params)
2. Deserialize & validate input via Pydantic Schemas
3. Delegate business operations to the DriverService
4. Map Service layer outputs and Domain Exceptions into standard HTTP JSON responses
"""

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from driverguard.app.exceptions import DriverNotFoundError, DuplicateDriverError
from driverguard.app.schemas.driver import DriverCreateSchema, DriverUpdateSchema
from driverguard.app.services.driver_service import driver_service, DriverService

# ---------------------------------------------------------------------------
# Blueprint setup
# ---------------------------------------------------------------------------
drivers_bp = Blueprint("drivers", __name__, url_prefix="/api/v1")


# ---------------------------------------------------------------------------
# Helper: format Pydantic validation errors cleanly for API clients
# ---------------------------------------------------------------------------
def _format_pydantic_errors(error: ValidationError):
    formatted_errors = []
    for err in error.errors():
        field_name = ".".join(str(loc) for loc in err["loc"])
        formatted_errors.append({
            "field": field_name,
            "message": err["msg"],
            "type": err["type"]
        })
    return jsonify({
        "error": "Unprocessable Entity",
        "message": "Validation failed for request body.",
        "details": formatted_errors
    }), 422


# =========================================================================
# ENDPOINT 1: GET /api/v1/drivers — List all drivers
# =========================================================================
@drivers_bp.route("/drivers", methods=["GET"])
def list_drivers():
    """GET /api/v1/drivers — List all drivers."""
    drivers = driver_service.list_drivers()
    return jsonify({
        "count": len(drivers),
        "drivers": drivers,
    }), 200


# =========================================================================
# ENDPOINT 2: POST /api/v1/drivers — Create a new driver
# =========================================================================
@drivers_bp.route("/drivers", methods=["POST"])
def create_driver():
    """POST /api/v1/drivers — Create a new driver."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Request body must be valid JSON."
        }), 400

    # 1. HTTP Deserialization & Schema Validation
    try:
        schema = DriverCreateSchema.model_validate(data)
    except ValidationError as e:
        return _format_pydantic_errors(e)

    # 2. Delegate Business Operation to Service Layer
    try:
        driver = driver_service.create_driver(schema)
    except DuplicateDriverError as e:
        return jsonify({
            "error": "Conflict",
            "message": str(e)
        }), 409

    # 3. Format HTTP Success Response
    return jsonify(driver), 201


# =========================================================================
# ENDPOINT 3: GET /api/v1/drivers/<id> — Get a single driver
# =========================================================================
@drivers_bp.route("/drivers/<int:driver_id>", methods=["GET"])
def get_driver(driver_id: int):
    """GET /api/v1/drivers/<id> — Get single driver."""
    try:
        driver = driver_service.get_driver(driver_id)
        return jsonify(driver), 200
    except DriverNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404


# =========================================================================
# ENDPOINT 4: PATCH /api/v1/drivers/<id> — Partially update driver
# =========================================================================
@drivers_bp.route("/drivers/<int:driver_id>", methods=["PATCH"])
def update_driver(driver_id: int):
    """PATCH /api/v1/drivers/<id> — Partially update driver."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Request body must be valid JSON."
        }), 400

    # 1. HTTP Deserialization & Schema Validation
    try:
        schema = DriverUpdateSchema.model_validate(data)
    except ValidationError as e:
        return _format_pydantic_errors(e)

    if not schema.model_dump(exclude_unset=True):
        return jsonify({
            "error": "Bad Request",
            "message": "At least one valid field (name, email, device_id) must be provided for update."
        }), 400

    # 2. Delegate Business Operation to Service Layer
    try:
        driver = driver_service.update_driver(driver_id, schema)
        return jsonify(driver), 200
    except DriverNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
    except DuplicateDriverError as e:
        return jsonify({
            "error": "Conflict",
            "message": str(e)
        }), 409


# =========================================================================
# ENDPOINT 5: DELETE /api/v1/drivers/<id> — Delete driver
# =========================================================================
@drivers_bp.route("/drivers/<int:driver_id>", methods=["DELETE"])
def delete_driver(driver_id: int):
    """DELETE /api/v1/drivers/<id> — Delete driver."""
    try:
        driver_service.delete_driver(driver_id)
        return "", 204
    except DriverNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e)
        }), 404
