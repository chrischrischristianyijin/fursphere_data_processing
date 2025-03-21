from flask import Flask, request, jsonify
import json
import psycopg2
from config import DB_CONFIG
from tasks import process_ai_task

app = Flask(__name__)

def connect_db():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()

    # 1. Flask API Stores Data in PostgreSQL
    cursor.execute("""
        INSERT INTO survey_data (
            email, ip, pet_type, pet_name, pet_breed, 
            pet_gender, pet_age, personality_behavior
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING submission_id;
    """, (
        data["user_info"]["email"], 
        data["user_info"]["ip"],
        data["pet_info"]["type"],
        data["pet_info"]["name"],
        data["pet_info"]["breed"],
        data["pet_info"]["gender"],
        data["pet_info"]["age"],
        json.dumps(data["personality_behavior"])
    ))

    submission_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    # 2. Flask Queues Task for Celery to Process AI
    process_ai_task.delay(submission_id)

    return jsonify({"status": "processing", "submission_id": submission_id}), 202

@app.route('/get_result/<int:submission_id>', methods=['GET'])
def get_result(submission_id):
    conn = connect_db()
    cursor = conn.cursor()

    # 6. Frontend Requests AI Results from Flask
    cursor.execute("""
        SELECT ai_output_image, ai_output_text, generated_at 
        FROM survey_data 
        WHERE submission_id = %s;
    """, (submission_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result or not result[0]:
        return jsonify({"status": "processing"}), 202

    return jsonify({
        "status": "completed", 
        "ai_output": {
            "image": result[0],
            "text": result[1],
            "generated_at": result[2].isoformat() if result[2] else None
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


