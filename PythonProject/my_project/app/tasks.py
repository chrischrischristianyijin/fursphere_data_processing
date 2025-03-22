from celery import Celery
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import requests
from typing import Dict, Any
from config import DB_CONFIG, AI_SERVER_URL, REDIS_URL
from mbti_calculator import calculate_mbti

app = Celery('tasks', broker=REDIS_URL)

@app.task
def process_ai_task(task_id: int):
    try:
        # 1. 从数据库读取宠物信息
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 读取宠物信息
        cur.execute("""
            SELECT p.*, s.personality_behavior
            FROM pet_info p
            JOIN survey_data s ON p.id = s.pet_id
            WHERE p.id = %s
        """, (task_id,))
        
        pet_data = cur.fetchone()
        if not pet_data:
            raise Exception(f"Pet data not found for task_id: {task_id}")
            
        # 2. 计算MBTI分数
        mbti_scores = calculate_mbti(
            pet_data['personality_behavior'],
            pet_data['pet_type'],
            pet_data['pet_breed']
        )
        
        # 3. 准备发送给AI服务的数据
        ai_input = {
            "pet_name": pet_data['pet_name'],
            "pet_type": pet_data['pet_type'],
            "pet_breed": pet_data['pet_breed'],
            "mbti_scores": mbti_scores
        }
        
        # 4. 调用AI服务
        ai_response = requests.post(
            f"{AI_SERVER_URL}/ai",
            json={"input_data": ai_input},
            timeout=30  # 增加超时时间
        )
        
        if ai_response.status_code != 200:
            raise Exception(f"AI service error: {ai_response.text}")
            
        ai_result = ai_response.json()
        
        # 5. 更新数据库中的AI结果
        cur.execute("""
            UPDATE survey_data 
            SET mbti_scores = %s,
                mbti_labels = %s,
                mbti_explanations = %s,
                personal_speech = %s,
                third_person_diagnosis = %s,
                ai_processed = true,
                updated_at = NOW()
            WHERE pet_id = %s
        """, (
            json.dumps(mbti_scores),
            json.dumps({
                "E/I": ai_result["m_label"],
                "S/N": ai_result["b_label"],
                "T/F": ai_result["t_label"],
                "J/P": ai_result["i_label"]
            }),
            json.dumps({
                "E/I": ai_result["m_explanation"],
                "S/N": ai_result["b_explanation"],
                "T/F": ai_result["t_explanation"],
                "J/P": ai_result["i_explanation"]
            }),
            ai_result["personal_speech"],
            ai_result["third_person_diagnosis"],
            task_id
        ))
        
        conn.commit()
        return {"status": "success", "task_id": task_id}
        
    except Exception as e:
        print(f"Error processing task {task_id}: {str(e)}")
        return {"status": "error", "task_id": task_id, "error": str(e)}
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
