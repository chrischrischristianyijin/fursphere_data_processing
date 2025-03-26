import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.mbti_calculator import calculate_mbti
import requests
import json
from dotenv import load_dotenv

def print_ai_analysis(result, mbti_scores):
    print("\nMBTI Analysis Results:")
    print("-" * 50)
    
    # Round scores for display
    rounded_scores = {k: round(v) for k, v in mbti_scores.items()}
    
    print("\nOriginal MBTI Scores (0-100, 50=midpoint):")
    print(json.dumps(rounded_scores, indent=2, ensure_ascii=False))
    
    # Calculate deviation scores using rounded scores
    deviation_scores = {
        "E/I": convert_to_deviation_score(rounded_scores["E/I"], "E/I"),
        "S/N": convert_to_deviation_score(rounded_scores["S/N"], "S/N"),
        "T/F": convert_to_deviation_score(rounded_scores["T/F"], "T/F"),
        "J/P": convert_to_deviation_score(rounded_scores["J/P"], "J/P")
    }
    
    print("\nMBTI Deviation Scores (0-100, 0=balanced, 100=extreme):")
    print(json.dumps(deviation_scores, indent=2, ensure_ascii=False))
    
    # Define dimension labels
    dimensions = {
        "E/I": ("Introversion", "Extraversion"),
        "S/N": ("Sensing", "Intuition"),
        "T/F": ("Thinking", "Feeling"),
        "J/P": ("Judging", "Perceiving")
    }
    
    # Map AI result keys to dimension keys
    dimension_map = {
        'm_score': 'E/I',
        'b_score': 'S/N',
        't_score': 'T/F',
        'i_score': 'J/P'
    }
    
    # Print MBTI dimensions with correct labels
    for dim, (low, high) in dimensions.items():
        score = rounded_scores[dim]
        dev_score = deviation_scores[dim]
        label = high if score > 50 else low
        
        print(f"\n{dim} Dimension:")
        print(f"Original Score: {score} ({label})")
        print(f"Deviation Score: {dev_score}")
        
        # Map dimension to AI result key for explanation
        for ai_key, mapped_dim in dimension_map.items():
            if mapped_dim == dim:
                exp_key = ai_key.replace('score', 'explanation')
                print(f"Explanation: {result[exp_key]}")
                break
    
    print("\n" + "-" * 50)
    print("Personalized Quote:")
    print(result['personal_speech'])
    
    print("\n" + "-" * 50)
    print("Third Person Diagnosis:")
    print(result['third_person_diagnosis'])
    
    print("\n" + "-" * 50)
    print("Interaction Guidelines:")
    print("Recommended Interactions:")
    print(result['do_suggestion'])
    print("\nInteractions to Avoid:")
    print(result['do_not_suggestion'])
    print("-" * 50)
    
    # Print personality tendency analysis
    print("\nPersonality Tendency Analysis:")
    print("-" * 50)
    
    for dim, (low, high) in dimensions.items():
        score = deviation_scores[dim]
        if score < 20:
            strength = "Very Balanced"
        elif score < 40:
            strength = "Moderately Balanced"
        elif score < 60:
            strength = "Slight Tendency"
        elif score < 80:
            strength = "Strong Tendency"
        else:
            strength = "Extreme Tendency"
        
        label = high if rounded_scores[dim] > 50 else low
        print(f"{dim}: {score} - {strength} ({label})")

def process_survey_data(survey_data):
    # 提取宠物信息
    pet_info = survey_data["pet_info"]
    personality_data = survey_data["personality_and_behavior"]
    
    def clean_value(value):
        if isinstance(value, str):
            # 移除所有不可见字符和括号
            value = ''.join(char for char in value if char.isprintable())
            value = value.strip(')')
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0
    
    # 处理行为数据
    personality_behavior = {
        "Energy_Socialization": {
            "seek_attention": clean_value(personality_data["Energy_Socialization"]["seek_attention"]),
            "interact_with_toys": clean_value(personality_data["Energy_Socialization"]["interact_with_toys"]),
            "stranger_enter_territory": clean_value(personality_data["Energy_Socialization"]["stranger_enter_territory"])
        },
        "Routin_Curiosity": {
            "prefer_routine": clean_value(personality_data["Routin_Curiosity"]["prefer_routine"]),
            "friend_visit_behaviors": clean_value(personality_data["Routin_Curiosity"]["friend_visit_behaviors"]),
            "fur_care_7days": clean_value(personality_data["Routin_Curiosity"]["fur_care_7days"])
        },
        "Decision_Making": {
            "react_when_sad": clean_value(personality_data["Decision_Making"]["react_when_sad"]),
            "toy_out_of_reach": "Keep trying" if clean_value(personality_data["Decision_Making"]["toy_out_of_reach"]) > 50 else "Give up",
            "react_new_friend": clean_value(personality_data["Decision_Making"]["react_new_friend"])
        },
        "Structure_Spontaneity": {
            "react_new_environment": clean_value(personality_data["Structure_Spontaneity"]["react_new_environment"]),
            "respond_to_scold": clean_value(personality_data["Structure_Spontaneity"]["respond_to_scold"]),
            "follow_commands": clean_value(personality_data["Structure_Spontaneity"]["follow_commands"])
        }
    }
    
    return {
        "personality_behavior": personality_behavior,
        "pet_type": pet_info["PetSpecies"],
        "pet_breed": pet_info["PetBreed"],
        "pet_name": pet_info["PetName"]
    }

def convert_to_deviation_score(score, label):
    """
    将0-100的分数转换为偏差值（0表示平衡，100表示极端）
    例如：
    原始分数30 (E) -> 偏差值40 (|50-30|*2)
    原始分数80 (I) -> 偏差值60 (|50-80|*2)
    """
    return abs(50 - score) * 2

def test_mbti():
    while True:
        print("\nMBTI Test Menu:")
        print("1. Start new test")
        print("2. Exit")
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "2":
            print("Exiting program. Goodbye!")
            break
        elif choice != "1":
            print("Invalid choice. Please try again.")
            continue
            
        print("\nPaste your JSON data (press Enter twice to finish):")
        json_lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            json_lines.append(line)
        
        try:
            json_str = "\n".join(json_lines)
            data = json.loads(json_str)
            
            # Process data
            test_data = process_survey_data(data["surveyData"])
            
            print("\nProcessed test data:")
            print(json.dumps(test_data, indent=2, ensure_ascii=False))
            
            print("\nCalculating MBTI scores...")
            mbti_scores = calculate_mbti(
                test_data["personality_behavior"],
                test_data["pet_type"],
                test_data["pet_breed"]
            )
            
            # 为AI服务准备整数分数
            ai_input = {
                "input_data": {
                    "pet_name": test_data["pet_name"],
                    "pet_type": test_data["pet_type"],
                    "pet_breed": test_data["pet_breed"],
                    "mbti_scores": {k: round(v) for k, v in mbti_scores.items()}  # 四舍五入为整数
                }
            }
            
            try:
                # Send to AI service
                response = requests.post("http://localhost:8001/ai", json=ai_input)
                
                if response.status_code == 200:
                    ai_result = response.json()
                    # 使用原始分数进行显示，但在显示函数内部会进行四舍五入
                    print_ai_analysis(ai_result, mbti_scores)
                else:
                    print(f"Error: AI service returned status code {response.status_code}")
                    print(response.text)
            except requests.exceptions.ConnectionError:
                print("Error: Could not connect to AI service. Please ensure the AI server is running.")
                break
        except json.JSONDecodeError:
            print("Error: Invalid JSON data format")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\nPress Enter to continue...")
        input()

if __name__ == "__main__":
    load_dotenv()
    test_mbti()