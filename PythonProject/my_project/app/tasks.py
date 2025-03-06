from celery import Celery
import psycopg2
import requests
import json
from config import DB_CONFIG, AI_SERVER_URL

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_ai_task(submission_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 3. Celery Worker Fetches Data from PostgreSQL & Sends to AI
        cursor.execute("SELECT input_data FROM survey_data WHERE submission_id = %s;", (submission_id,))
        result = cursor.fetchone()

        if not result:
            print(f"Submission ID {submission_id} not found!")
            conn.close()
            return

        input_data = result[0]

        ai_response = requests.post(f"{AI_SERVER_URL}/ai", json={"input_data": input_data}, timeout=10)
        ai_response.raise_for_status()
        ai_result = ai_response.json()

        # 5.Celery Stores AI Output in PostgreSQL
        cursor.execute("UPDATE survey_data SET ai_output = %s WHERE submission_id = %s;",
                       (json.dumps(ai_result), submission_id))

        conn.commit()
        print(f"AI Analysis Completed for Submission ID: {submission_id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
