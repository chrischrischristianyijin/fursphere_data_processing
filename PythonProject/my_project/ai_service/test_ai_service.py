import requests
import json
from pprint import pprint
import os
from dotenv import load_dotenv

def check_openai_api_key():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nError: OPENAI_API_KEY not found in environment variables!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your-api-key-here")
        return False
    return True

def test_ai_service():
    # 首先检查OpenAI API密钥
    if not check_openai_api_key():
        return

    # AI服务URL
    url = "http://localhost:8001/ai"
    
    # 测试数据
    test_data = {
        "input_data": {
            "pet_name": "Kimi",
            "pet_type": "Dog",
            "pet_breed": "Border Collie",
            "mbti_scores": {
                "E/I": 27,  # Extraversion
                "S/N": 72,  # Intuition
                "T/F": 32,  # Feeling
                "J/P": 25   # Judging
            }
        }
    }
    
    try:
        # 测试健康检查端点
        print("\n1. Testing health check endpoint...")
        health_response = requests.get("http://localhost:8001/health")
        print("Health Check Response:")
        pprint(health_response.json())
        
        # 测试AI分析端点
        print("\n2. Testing AI analysis endpoint...")
        print("Sending request with test data:")
        pprint(test_data)
        
        response = requests.post(url, json=test_data)
        
        # 检查响应状态
        if response.status_code == 200:
            print("\nAI Service Response:")
            result = response.json()
            print("\nMBTI Analysis Results:")
            print("-" * 50)
            print(f"E/I Dimension:")
            print(f"  Label: {result['m_label']}")
            print(f"  Score: {result['m_score']}")
            print(f"  Explanation: {result['m_explanation']}")
            print("-" * 50)
            print(f"S/N Dimension:")
            print(f"  Label: {result['b_label']}")
            print(f"  Score: {result['b_score']}")
            print(f"  Explanation: {result['b_explanation']}")
            print("-" * 50)
            print(f"T/F Dimension:")
            print(f"  Label: {result['t_label']}")
            print(f"  Score: {result['t_score']}")
            print(f"  Explanation: {result['t_explanation']}")
            print("-" * 50)
            print(f"J/P Dimension:")
            print(f"  Label: {result['i_label']}")
            print(f"  Score: {result['i_score']}")
            print(f"  Explanation: {result['i_explanation']}")
            print("-" * 50)
            print("\nPersonal Speech:")
            print(result['personal_speech'])
            print("-" * 50)
            print("\nThird Person Diagnosis:")
            print(result['third_person_diagnosis'])
            print("-" * 50)
            
        else:
            print(f"\nError: Received status code {response.status_code}")
            print("Response:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the AI service. Make sure it's running on localhost:8001")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_ai_service() 