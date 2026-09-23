from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import json

from security.encryption import encrypt_text, decrypt_text
from nlp_model import analyze_text
from risk_engine import determine_risk

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "sprout.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# STUDENT HOME
# =========================================================

@app.route("/")
def student_home():
    return render_template("index.html")


# =========================================================
# COUNSELOR DASHBOARD
# =========================================================

@app.route("/counselor")
def counselor_dashboard():
    return render_template("counselor.html")


# =========================================================
# SAVE JOURNAL
# =========================================================

@app.route("/api/journal", methods=["POST"])
def save_journal():

    data = request.get_json() or {}

    student_id = data.get("student_id", "MB-1024")
    content = data.get("content", "").strip()
    mood = data.get("mood", "").strip()

    # New chip data
    day_factors = data.get("day_factors", [])
    helpful_needs = data.get("helpful_needs", [])

    # Make sure they are lists
    if not isinstance(day_factors, list):
        day_factors = []

    if not isinstance(helpful_needs, list):
        helpful_needs = []

    if not content:
        return jsonify({
            "error": "Journal content cannot be empty."
        }), 400

    # -----------------------------------------------------
    # ENCRYPT JOURNAL CONTENT
    # -----------------------------------------------------

    encrypted_content = encrypt_text(content)

    # Store chip selections as JSON
    day_factors_json = json.dumps(
        day_factors,
        ensure_ascii=False
    )

    helpful_needs_json = json.dumps(
        helpful_needs,
        ensure_ascii=False
    )

    conn = get_db_connection()

    # -----------------------------------------------------
    # SAVE JOURNAL + MOOD + CHIP DATA
    # -----------------------------------------------------

    conn.execute(
        """
        INSERT INTO journal_entries
        (
            student_id,
            encrypted_content,
            mood,
            day_factors,
            helpful_needs
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            student_id,
            encrypted_content,
            mood,
            day_factors_json,
            helpful_needs_json
        )
    )

    # -----------------------------------------------------
    # LOCAL NLP ANALYSIS
    # -----------------------------------------------------

    analysis = analyze_text(content)

    prediction = analysis["prediction"]
    confidence = analysis["confidence"]

    # -----------------------------------------------------
    # RISK / WELLBEING SIGNAL ENGINE
    # -----------------------------------------------------

    risk = determine_risk(
        prediction,
        confidence
    )

    risk_level = risk["risk_level"]
    signal_summary = risk["signal_summary"]

    # -----------------------------------------------------
    # COUNSELOR ESCALATION
    # IMPORTANT:
    # NO RAW JOURNAL CONTENT IS STORED HERE
    # -----------------------------------------------------

    if risk_level in ["ELEVATED", "HIGH"]:

        conn.execute(
            """
            INSERT INTO escalation_alerts
            (
                student_id,
                risk_level,
                signal_summary
            )
            VALUES (?, ?, ?)
            """,
            (
                student_id,
                risk_level,
                signal_summary
            )
        )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Journal securely saved.",
        "prediction": prediction,
        "confidence": confidence,
        "risk_level": risk_level
    })


# =========================================================
# STUDENT JOURNAL HISTORY
# =========================================================

@app.route("/api/student/history", methods=["GET"])
def get_student_history():

    student_id = request.args.get(
        "student_id",
        "MB-1024"
    )

    conn = get_db_connection()

    entries = conn.execute(
        """
        SELECT
            entry_id,
            student_id,
            encrypted_content,
            mood,
            day_factors,
            helpful_needs,
            created_at
        FROM journal_entries
        WHERE student_id = ?
        ORDER BY created_at DESC
        """,
        (student_id,)
    ).fetchall()

    conn.close()

    history = []

    for entry in entries:

        # Decrypt only when retrieving
        # the student's own private history
        decrypted_content = decrypt_text(
            entry["encrypted_content"]
        )

        # Safely decode chip data
        try:
            day_factors = json.loads(
                entry["day_factors"]
            ) if entry["day_factors"] else []
        except (json.JSONDecodeError, TypeError):
            day_factors = []

        try:
            helpful_needs = json.loads(
                entry["helpful_needs"]
            ) if entry["helpful_needs"] else []
        except (json.JSONDecodeError, TypeError):
            helpful_needs = []

        history.append({

            "entry_id":
                entry["entry_id"],

            "student_id":
                entry["student_id"],

            "content":
                decrypted_content,

            "mood":
                entry["mood"],

            "day_factors":
                day_factors,

            "helpful_needs":
                helpful_needs,

            "created_at":
                entry["created_at"]
        })

    return jsonify(history)


# =========================================================
# COUNSELOR ALERTS
# =========================================================

@app.route("/api/counselor/alerts", methods=["GET"])
def get_counselor_alerts():

    conn = get_db_connection()

    alerts = conn.execute(
        """
        SELECT
            alert_id,
            student_id,
            risk_level,
            signal_summary,
            status,
            created_at
        FROM escalation_alerts
        ORDER BY created_at DESC
        """
    ).fetchall()

    conn.close()

    return jsonify([
        dict(alert)
        for alert in alerts
    ])


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )