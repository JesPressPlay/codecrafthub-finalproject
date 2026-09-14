"""
CodeCraftHub - a simple REST API for tracking courses you want to learn.

Everything lives in this one file to keep things easy to follow:
- Flask routes handle HTTP requests/responses
- Course data is stored as a JSON array in courses.json (no database)
"""

import json
import os
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

# The JSON "database" file. It lives next to this script.
COURSES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses.json")

# The only status values we allow a course to have.
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]


def init_courses_file():
    """Create courses.json with an empty list if it doesn't exist yet.

    Called once when the app starts, so the API works on a fresh checkout
    without any manual setup.
    """
    if not os.path.exists(COURSES_FILE):
        try:
            with open(COURSES_FILE, "w") as f:
                json.dump([], f)
        except IOError as e:
            # If we can't even create the file, the app can't function -
            # fail loudly at startup rather than hitting this on every request.
            raise RuntimeError(f"Could not create {COURSES_FILE}: {e}")


def load_courses():
    """Read all courses from courses.json and return them as a Python list.

    Raises IOError/json.JSONDecodeError so callers can turn file problems
    into a proper HTTP error response instead of crashing the process.
    """
    with open(COURSES_FILE, "r") as f:
        content = f.read().strip()
        return json.loads(content) if content else []


def save_courses(courses):
    """Write the given list of courses back to courses.json."""
    with open(COURSES_FILE, "w") as f:
        json.dump(courses, f, indent=2)


def get_next_id(courses):
    """Work out the next auto-incrementing id (starts at 1).

    Using max(existing ids) + 1 - rather than len(courses) + 1 - means ids
    stay unique even after courses in the middle have been deleted.
    """
    if not courses:
        return 1
    return max(course["id"] for course in courses) + 1


def find_course_index(courses, course_id):
    """Return the list index of the course with this id, or None if missing."""
    for index, course in enumerate(courses):
        if course["id"] == course_id:
            return index
    return None


def validate_course_payload(data, require_all_fields):
    """Check a request body for missing/invalid course fields.

    Returns an error message string if something is wrong, or None if the
    payload is valid.

    require_all_fields=True is used for creating a course (every field must
    be present). For updates we only validate the fields that were actually
    sent, so a PUT can change just one field at a time.
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    required_fields = ["name", "description", "target_date", "status"]

    if require_all_fields:
        for field in required_fields:
            if field not in data or data[field] in (None, ""):
                return f"'{field}' is required"

    # Validate whichever fields are present, regardless of require_all_fields.
    if "name" in data and (not isinstance(data["name"], str) or not data["name"].strip()):
        return "'name' must be a non-empty string"

    if "description" in data and (not isinstance(data["description"], str) or not data["description"].strip()):
        return "'description' must be a non-empty string"

    if "target_date" in data:
        try:
            datetime.strptime(data["target_date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            return "'target_date' must be a valid date in YYYY-MM-DD format"

    if "status" in data and data["status"] not in VALID_STATUSES:
        return f"'status' must be one of {VALID_STATUSES}"

    return None


@app.errorhandler(404)
def handle_404(e):
    """Catch requests to routes that don't exist at all (not just missing courses)."""
    return jsonify({"error": "Resource not found"}), 404


# ---------------------------------------------------------------------------
# POST /api/courses - Add a new course
# ---------------------------------------------------------------------------
@app.route("/api/courses", methods=["POST"])
def create_course():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    error = validate_course_payload(data, require_all_fields=True)
    if error:
        return jsonify({"error": error}), 400

    try:
        courses = load_courses()

        course = {
            "id": get_next_id(courses),
            "name": data["name"].strip(),
            "description": data["description"].strip(),
            "target_date": data["target_date"],
            "status": data["status"],
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        courses.append(course)
        save_courses(courses)
    except (IOError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Failed to save course data: {e}"}), 500

    return jsonify(course), 201


# ---------------------------------------------------------------------------
# GET /api/courses - Get all courses
# ---------------------------------------------------------------------------
@app.route("/api/courses", methods=["GET"])
def get_courses():
    try:
        courses = load_courses()
    except (IOError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Failed to read course data: {e}"}), 500

    # Optional ?status=In Progress filter, mainly useful for the UI later.
    status_filter = request.args.get("status")
    if status_filter:
        if status_filter not in VALID_STATUSES:
            return jsonify({"error": f"'status' filter must be one of {VALID_STATUSES}"}), 400
        courses = [c for c in courses if c["status"] == status_filter]

    return jsonify(courses), 200


# ---------------------------------------------------------------------------
# GET /api/courses/<course_id> - Get a specific course
# ---------------------------------------------------------------------------
@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    try:
        courses = load_courses()
    except (IOError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Failed to read course data: {e}"}), 500

    index = find_course_index(courses, course_id)
    if index is None:
        return jsonify({"error": f"Course with id {course_id} not found"}), 404

    return jsonify(courses[index]), 200


# ---------------------------------------------------------------------------
# PUT /api/courses/<course_id> - Update a course
# ---------------------------------------------------------------------------
@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # Only the fields provided need to be valid - this is a partial update.
    error = validate_course_payload(data, require_all_fields=False)
    if error:
        return jsonify({"error": error}), 400

    try:
        courses = load_courses()
        index = find_course_index(courses, course_id)
        if index is None:
            return jsonify({"error": f"Course with id {course_id} not found"}), 404

        course = courses[index]
        for field in ["name", "description", "target_date", "status"]:
            if field in data:
                value = data[field]
                course[field] = value.strip() if isinstance(value, str) else value

        save_courses(courses)
    except (IOError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Failed to save course data: {e}"}), 500

    return jsonify(course), 200


# ---------------------------------------------------------------------------
# DELETE /api/courses/<course_id> - Delete a course
# ---------------------------------------------------------------------------
@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    try:
        courses = load_courses()
        index = find_course_index(courses, course_id)
        if index is None:
            return jsonify({"error": f"Course with id {course_id} not found"}), 404

        deleted_course = courses.pop(index)
        save_courses(courses)
    except (IOError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Failed to save course data: {e}"}), 500

    return jsonify({"message": "Course deleted", "course": deleted_course}), 200


# Run this at import time (not just under `python app.py`) so courses.json
# also gets created when the app is served via `flask run` or a WSGI server.
init_courses_file()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
