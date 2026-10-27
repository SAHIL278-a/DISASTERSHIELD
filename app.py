import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, render_template

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Add project root to Python import path
sys.path.insert(0, str(PROJECT_ROOT))

# Import risk engine and database
from backend.risk_engine import assess_disaster_risk
from backend.ai_engine import (
    analyze_disaster_alert,
    ask_emergency_assistant,
    model_status
)
from database.db import get_connection, initialize_database
import requests
import feedparser



# Flask application
app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path="/static"
)

# Initialize database
initialize_database()


# -----------------------------------------
# HOME PAGE - FRONTEND WEBSITE
# -----------------------------------------
@app.route("/")
def home():
    return send_from_directory(str(FRONTEND_DIR), "index.html")


# -----------------------------------------
# BACKEND HEALTH CHECK
# -----------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "project": "DisasterShield AI",
        "status": "Online",
        "message": "Backend is working correctly"
    })


# -----------------------------------------
# CREATE DISASTER REPORT
# -----------------------------------------
@app.route("/api/reports", methods=["POST"])
def create_report():
    data = request.get_json(silent=True) or {}

    incident_type = str(
        data.get("incident_type", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()

    location = str(
        data.get("location", "")
    ).strip()

    if not incident_type or not description:
        return jsonify({
            "error": "Incident type and description are required"
        }), 400

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO disaster_reports
                (incident_type, description, location)
                VALUES (?, ?, ?)
                """,
                (incident_type, description, location)
            )

            report_id = cursor.lastrowid

        return jsonify({
            "message": "Disaster report saved successfully",
            "report_id": report_id,
            "incident_type": incident_type,
            "description": description,
            "location": location,
            "status": "Pending"
        }), 201

    except Exception:
        app.logger.exception("Failed to save disaster report")

        return jsonify({
            "error": "Unable to save report. Check the database."
        }), 500


# -----------------------------------------
# GET ALL DISASTER REPORTS
# -----------------------------------------
@app.route("/api/reports", methods=["GET"])
def get_reports():
    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM disaster_reports
                ORDER BY id DESC
                """
            ).fetchall()

        reports = [dict(row) for row in rows]

        return jsonify({
            "total": len(reports),
            "reports": reports
        })

    except Exception:
        app.logger.exception("Failed to retrieve disaster reports")

        return jsonify({
            "error": "Unable to retrieve reports"
        }), 500

@app.route("/api/risk-assessment", methods=["POST"])
def risk_assessment():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please send valid JSON data."
        }), 400

    incident_type = str(data.get("incident_type", "")).strip()

    if not incident_type:
        return jsonify({
            "error": "Disaster type is required."
        }), 400

    try:
        rainfall_mm = float(data.get("rainfall_mm", 0))
        wind_speed_kmh = float(data.get("wind_speed_kmh", 0))
        people_at_risk = int(data.get("people_at_risk", 0))

        if not all(map(
            lambda value: value >= 0,
            [rainfall_mm, wind_speed_kmh, people_at_risk]
        )):
            raise ValueError("Values cannot be negative.")

        if people_at_risk != float(data.get("people_at_risk", 0)):
            raise ValueError("People at risk must be a whole number.")

        if not all(map(
            lambda value: value < float("inf"),
            [rainfall_mm, wind_speed_kmh, people_at_risk]
        )):
            raise ValueError("Values must be finite numbers.")

    except (ValueError, TypeError, OverflowError):
        return jsonify({
            "error": "Enter valid, non-negative numbers."
        }), 400

    water_level_rising = data.get("water_level_rising", False)

    if not isinstance(water_level_rising, bool):
        return jsonify({
            "error": "water_level_rising must be true or false."
        }), 400

    result = assess_disaster_risk(
        incident_type=incident_type,
        rainfall_mm=rainfall_mm,
        wind_speed_kmh=wind_speed_kmh,
        water_level_rising=water_level_rising,
        people_at_risk=people_at_risk
    )

    return jsonify({
        "project": "DisasterShield AI",
        "assessment_type": "Prototype rule-based assessment",
        "risk_level": result.level,
        "risk_score": result.score,
        "message": result.message,
        "recommendations": result.recommendations
    }), 200

@app.route("/api/live-alerts", methods=["GET"])
def live_alerts():
    feed_url = (
        "https://sachet.ndma.gov.in/"
        "cap_public_website/rss/rss_india.xml"
    )

    try:
        response = requests.get(
    feed_url,
    timeout=(5, 30),
    headers={"User-Agent": "Mozilla/5.0 DisasterShieldAI/1.0"}
)
        
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        alerts = []

        for entry in feed.entries[:30]:
            alerts.append({
                "title": entry.get("title", "Disaster Alert"),
                "description": entry.get("summary", ""),
                "published": entry.get("published", ""),
                "link": entry.get("link", ""),
                "source": "NDMA SACHET"
            })

        return jsonify({
            "source": "NDMA SACHET",
            "live_data": True,
            "total": len(alerts),
            "alerts": alerts
        })

    except requests.RequestException as e:
        print("NDMA CONNECTION ERROR:", repr(e))

        return jsonify({
            "source": "NDMA SACHET",
            "live_data": False,
            "error": str(e),
            "alerts": []
        }), 502


# -----------------------------------------
# AI MODEL CONFIGURATION / STATUS
# -----------------------------------------
@app.route("/api/ai/status", methods=["GET"])
def ai_status():
    return jsonify({"project": "DisasterShield AI", **model_status()})

# -----------------------------------------
# GEMMA 4 - DISASTER ALERT EXPLANATION
# -----------------------------------------
@app.route("/api/ai/analyze-alert", methods=["POST"])
def analyze_alert():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please send valid JSON data."
        }), 400

    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    location = str(data.get("location", "")).strip()

    if not title and not description:
        return jsonify({
            "error": "Alert title or description is required."
        }), 400

    try:
        analysis = analyze_disaster_alert(
            title=title,
            description=description,
            location=location
        )

        return jsonify({
            "project": "DisasterShield AI",
            "model": model_status().get("last_successful_model") or model_status().get("primary_model"),
            "success": True,
            "analysis": analysis,
            "official_source": "NDMA SACHET",
            "notice": (
                "AI-generated explanation. "
                "Follow the original official alert."
            )
        }), 200

    except Exception:
        app.logger.exception("Gemma 4 alert analysis failed")

        return jsonify({
            "success": False,
            "error": (
                "Gemma 4 analysis is temporarily unavailable. "
                "Please refer to the original official alert."
            )
        }), 502

# -----------------------------------------
# GEMMA 4 - EMERGENCY ASSISTANT
# -----------------------------------------
@app.route("/api/ai/emergency-assistant", methods=["POST"])
def emergency_assistant():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Please send valid JSON data."
        }), 400

    question = str(data.get("question", "")).strip()
    location = str(data.get("location", "")).strip()

    if not question:
        return jsonify({
            "success": False,
            "error": "Please enter your emergency-related question."
        }), 400

    if len(question) > 3000:
        return jsonify({
            "success": False,
            "error": "Question must be 3000 characters or fewer."
        }), 400

    try:
        answer = ask_emergency_assistant(
            question=question,
            location=location
        )

        return jsonify({
            "project": "DisasterShield AI",
            "model": model_status().get("last_successful_model") or model_status().get("primary_model"),
            "success": True,
            "question": question,
            "answer": answer,
            "notice": (
                "AI-generated safety guidance. "
                "Follow official emergency instructions."
            )
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

    except Exception as error:
        app.logger.exception("Gemma 4 Emergency Assistant failed")

        return jsonify({
            "success": False,
            "error": "Emergency Assistant failed. Check server logs and /api/ai/status."
        }), 502

@app.route("/risk-map")
def risk_map():
    return send_from_directory(str(FRONTEND_DIR),"map.html")       

# -----------------------------------------
# RUN SERVER
# -----------------------------------------
if __name__ == "__main__":
    print("=" * 45)
    print("       DISASTERSHIELD AI")
    print("       Backend Starting...")
    print("=" * 45)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )