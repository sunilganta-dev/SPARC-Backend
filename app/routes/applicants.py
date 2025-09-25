from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from app import db
from app.models.matchmaker import Applicant, Matchmaker

applicants_bp = Blueprint("applicants", __name__)

# Allowed picture extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------------
# 1. Public route - Apply without login (by matchmaker_id)
# -------------------------------------------------------
@applicants_bp.route("/apply/<int:matchmaker_id>", methods=["POST"])
def apply_without_login(matchmaker_id):
    data = request.form.to_dict()
    file = request.files.get("picture")

    # Ensure matchmaker exists
    matchmaker = Matchmaker.query.get(matchmaker_id)
    if not matchmaker:
        return jsonify({"error": "Matchmaker not found"}), 404

    # Save picture if provided
    picture_url = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        file.save(filepath)
        picture_url = f"/uploads/{unique_name}"

    try:
        # Create applicant
        applicant = Applicant(
            shidduch_lady_id=matchmaker_id,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            dob=data.get("dob"),
            gender=data.get("gender"),
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            religious_level=data.get("religious_level"),
            kosher_level=data.get("kosher_level"),
            shabbat_observance=data.get("shabbat_observance"),
            picture_url=picture_url,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(applicant)
        db.session.commit()

        return jsonify({
            "message": "Application submitted successfully",
            "applicant": applicant.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------
# 2. Logged-in route - Regular applicant creation
# -------------------------------------------------------
@applicants_bp.route("/", methods=["POST"])
def create_applicant():
    data = request.form.to_dict()
    file = request.files.get("picture")

    picture_url = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        file.save(filepath)
        picture_url = f"/uploads/{unique_name}"

    try:
        applicant = Applicant(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            dob=data.get("dob"),
            gender=data.get("gender"),
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            religious_level=data.get("religious_level"),
            kosher_level=data.get("kosher_level"),
            shabbat_observance=data.get("shabbat_observance"),
            picture_url=picture_url,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(applicant)
        db.session.commit()

        return jsonify({
            "message": "Applicant created successfully",
            "applicant": applicant.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
