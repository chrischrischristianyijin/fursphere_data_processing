from celery import Celery
import psycopg2
import requests
import json
from config import DB_CONFIG, AI_SERVER_URL

app = Celery('tasks', broker='redis://localhost:6379/0')

def calculate_mbti(personality_behavior):
    # 初始化MBTI维度分数
    mbti_scores = {
        'E': 0, 'I': 0,  # Extraversion vs Introversion
        'S': 0, 'N': 0,  # Sensing vs Intuition
        'T': 0, 'F': 0,  # Thinking vs Feeling
        'J': 0, 'P': 0   # Judging vs Perceiving
    }
    
    # E vs I 维度计算
    ei_questions = personality_behavior["Energy & Socialization (E vs. I)"]
    mbti_scores['E'] += ei_questions["How much does he/she seek your attention? (Needy ↔ Independent)"]
    mbti_scores['E'] += ei_questions["How does he/she react to new people? (Shy ↔ Outgoing)"]
    mbti_scores['E'] += ei_questions["How does he/she behave around other animals? (Avoids them ↔ Loves making new friends)"]
    
    # S vs N 维度计算
    sn_questions = personality_behavior["Routine vs. Curiosity (S vs. N)"]
    mbti_scores['S'] += (10 - sn_questions["Does he/she prefer a strict routine? (Needs routine ↔ Easily adapts to new things)"])
    mbti_scores['N'] += sn_questions["How does he/she react to new environments? (Cautious ↔ Explores immediately)"]
    mbti_scores['N'] += sn_questions["Does he/she often seem lost in thought or 'zoned out'? (Always present ↔ Often staring off at nothing)"]
    
    # T vs F 维度计算
    tf_questions = personality_behavior["Decision-Making (T vs. F)"]
    mbti_scores['F'] += tf_questions["How does he/she react when you're sad? (Ignores it ↔ Comforts you immediately)"]
    if tf_questions["When faced with a challenge (e.g., reaching food or a toy), does he/she:"] == "Keep trying":
        mbti_scores['T'] += 5
    mbti_scores['T'] += (10 - tf_questions["Does he/she seem to hold grudges? (Forgets instantly ↔ Remembers and reacts later)"])
    
    # J vs P 维度计算
    jp_questions = personality_behavior["Structure vs. Spontaneity (J vs. P)"]
    mbti_scores['J'] += jp_questions["Does he/she prefer things a certain way?"]
    mbti_scores['P'] += (10 - jp_questions["How does he/she react to unexpected changes?"])
    mbti_scores['J'] += jp_questions["Is he/she more likely to follow commands?"]
    
    # 确定最终的MBTI类型
    mbti_type = ''
    mbti_type += 'E' if mbti_scores['E'] > mbti_scores['I'] else 'I'
    mbti_type += 'S' if mbti_scores['S'] > mbti_scores['N'] else 'N'
    mbti_type += 'T' if mbti_scores['T'] > mbti_scores['F'] else 'F'
    mbti_type += 'J' if mbti_scores['J'] > mbti_scores['P'] else 'P'
    
    return mbti_type, mbti_scores

@app.task
def process_ai_task(submission_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. 从数据库读取宠物信息和行为数据
        cursor.execute("""
            SELECT pet_type, pet_name, pet_breed, pet_gender, 
                   pet_age, personality_behavior 
            FROM survey_data 
            WHERE submission_id = %s;
        """, (submission_id,))
        result = cursor.fetchone()

        if not result:
            print(f"Submission ID {submission_id} not found!")
            conn.close()
            return

        # 2. 计算MBTI分数
        personality_behavior = result[5]  # JSONB数据
        mbti_type, mbti_scores = calculate_mbti(personality_behavior)

        # 3. 存储MBTI结果到数据库
        cursor.execute("""
            UPDATE survey_data 
            SET mbti_type = %s,
                mbti_scores = %s
            WHERE submission_id = %s;
        """, (
            mbti_type,
            json.dumps(mbti_scores),
            submission_id
        ))
        conn.commit()

        # 4. 准备发送给AI的数据
        input_data = {
            "pet_type": result[0],
            "pet_name": result[1],
            "pet_breed": result[2],
            "pet_gender": result[3],
            "pet_age": result[4],
            "personality_behavior": personality_behavior,
            "mbti_type": mbti_type,
            "mbti_scores": mbti_scores
        }

        # 5. 发送数据给AI服务
        ai_response = requests.post(f"{AI_SERVER_URL}/ai", json={"input_data": input_data}, timeout=10)
        ai_response.raise_for_status()
        ai_result = ai_response.json()

        # 6. 存储AI生成结果
        cursor.execute("""
            UPDATE survey_data 
            SET ai_output_image = %s, 
                ai_output_text = %s,
                generated_at = NOW()
            WHERE submission_id = %s;
        """, (
            ai_result.get("image_url"),
            ai_result.get("text"),
            submission_id
        ))

        conn.commit()
        print(f"AI Analysis Completed for Submission ID: {submission_id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
