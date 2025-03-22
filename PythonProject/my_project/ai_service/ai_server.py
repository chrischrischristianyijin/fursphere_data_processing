from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any
import openai
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class MbtiOutput(BaseModel):
    m_label: Literal["Extraversion", "Introversion"]
    m_score: int = Field(description="A percentage score between 0 and 100")
    m_explanation: str = Field(description="150-200 characters")

    b_label: Literal["Sensing", "Intuition"]
    b_score: int = Field(description="A percentage score between 0 and 100")
    b_explanation: str = Field(description="150-200 characters")

    t_label: Literal["Thinking", "Feeling"]
    t_score: int = Field(description="A percentage score between 0 and 100")
    t_explanation: str = Field(description="150-200 characters")

    i_label: Literal["Judging", "Perceiving"]
    i_score: int = Field(description="A percentage score between 0 and 100")
    i_explanation: str = Field(description="150-200 characters")

    personal_speech: str = Field(
        description="""
        Something the pet would say to its owner or other people, if it could
        speak, according to its personality. 50-75 characters
        """,
    )

    third_person_diagnosis: str = Field(
        description="""
        A diagnosis of the pet's personality from a third-person perspective. Do
        not include anything already mentioned in the MBTI breakdowns, but
        describe what it might be like to spend time with this pet. 175-216
        characters
        """,
    )

class AIInput(BaseModel):
    input_data: Dict[str, Any]

def generate_mbti_description(m_score, b_score, t_score, i_score):
    description = "MBTI Score Interpretation:\n"
    
    # E/I Dimension
    if m_score <= 30:
        description += "- Very Introverted: Quiet, Independent, Calm.\n"
    elif m_score <= 60:
        description += "- Balanced: Cautious, Slightly Reserved, Organized.\n"
    else:
        description += "- Extroverted: Playful, Energetic, Sociable.\n"
    
    # S/N Dimension
    if b_score <= 30:
        description += "- Sensing: Practical, Detail-Oriented, Reliable.\n"
    elif b_score <= 60:
        description += "- Balanced: Realistic with Some Creativity.\n"
    else:
        description += "- Intuitive: Curious, Innovative, Enjoys Exploration.\n"
    
    # T/F Dimension
    if t_score <= 30:
        description += "- Thinking: Logical, Independent, Strategic.\n"
    elif t_score <= 60:
        description += "- Balanced: Combines Logic with Empathy.\n"
    else:
        description += "- Feeling: Compassionate, Emotional, Loyal.\n"
    
    # J/P Dimension
    if i_score <= 30:
        description += "- Judging: Organized, Reliable, Rule-Oriented.\n"
    elif i_score <= 60:
        description += "- Balanced: Combines Planning and Flexibility.\n"
    else:
        description += "- Perceiving: Adaptable, Spontaneous, Curious.\n"
    
    return description

def map_score_to_label(score, dimension):
    if dimension == 'E/I':
        if score <= 30:
            return "Extraversion"
        else:
            return "Introversion"
    elif dimension == 'S/N':
        if score <= 30:
            return "Sensing"
        else:
            return "Intuition"
    elif dimension == 'T/F':
        if score <= 30:
            return "Thinking"
        else:
            return "Feeling"
    elif dimension == 'J/P':
        if score <= 30:
            return "Judging"
        else:
            return "Perceiving"

@app.post("/ai", response_model=MbtiOutput)
async def process_ai(input: AIInput):
    try:
        # Get input data
        pet_name = input.input_data["pet_name"]
        pet_type = input.input_data["pet_type"]
        pet_breed = input.input_data["pet_breed"]
        mbti_scores = input.input_data["mbti_scores"]
        
        # Generate MBTI description
        mbti_description = generate_mbti_description(
            mbti_scores['E/I'],
            mbti_scores['S/N'],
            mbti_scores['T/F'],
            mbti_scores['J/P']
        )
        
        # Build prompt for AI
        prompt = f"""
        Please analyze the personality of {pet_name} ({pet_type}, breed: {pet_breed}) based on the following MBTI characteristics:

        {mbti_description}

        Please provide your analysis in the following format, with EXACT character limits:

        [E/I Explanation]
        <150-200 characters>
        Describe the pet's energy level and social interactions in a fun, captivating way. Make it feel like the pet's personality is bursting from the description.

        [S/N Explanation]
        <150-200 characters>
        Paint a vivid picture of how this pet interacts with the world. Does it rely on sharp senses or dreamy creativity? Use playful language to highlight these traits.

        [T/F Explanation]
        <150-200 characters>
        Express the pet's emotional or logical side with personality and warmth. Whether it's a devoted protector or a tender-hearted snuggler, make it feel real.

        [J/P Explanation]
        <150-200 characters>
        Describe the pet's approach to life—whether it's a structured planner or a carefree adventurer. Use lively phrases to showcase its style.

        [Personal Speech]
        <50-75 characters>
        Write a short, catchy quote the pet might say. Keep it humorous, charming, or endearing—like something that reflects their essence.

        [Third Person Diagnosis]
        <175-216 characters>
        Provide a captivating third-person description of this pet's personality. Make it feel like the reader is getting a glimpse into a living, breathing character with quirks and charm.

        Remember: Character limits are strict requirements. Count your characters carefully for each section.
        """
        
        # Call OpenAI API
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a talented and expressive pet psychologist with a flair for storytelling. 
                    Your job is to analyze the pet's personality with creativity, humor, and warmth. 
                    Make your explanations vivid, engaging, and full of life, reflecting the pet's playful or thoughtful nature.
                    Use charming, witty, and lively language that brings the pet's personality to life.
                    
                    The description should feel universal, appealing, and fun without giving away the breed type.
                    
                    IMPORTANT: You must strictly follow the character limits for each section:
                    - Explanations: 150-200 characters
                    - Personal Speech: 50-75 characters
                    - Third Person Diagnosis: 175-216 characters
                    
                    Count your characters carefully and ensure each section meets these exact requirements.
                    """
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Get AI's response
        ai_response = completion.choices[0].message.content
        
        # Parse AI response
        def extract_section(content, section_name):
            start = content.find(f"[{section_name}]")
            if start == -1:
                return ""
            start = content.find("\n", start) + 1
            end = content.find("\n\n", start)
            if end == -1:
                end = len(content)
            return content[start:end].strip()
        
        # Create structured output for frontend
        output = {
            "m_label": map_score_to_label(mbti_scores['E/I'], 'E/I'),
            "m_score": mbti_scores['E/I'],
            "m_explanation": extract_section(ai_response, "E/I Explanation"),
            
            "b_label": map_score_to_label(mbti_scores['S/N'], 'S/N'),
            "b_score": mbti_scores['S/N'],
            "b_explanation": extract_section(ai_response, "S/N Explanation"),
            
            "t_label": map_score_to_label(mbti_scores['T/F'], 'T/F'),
            "t_score": mbti_scores['T/F'],
            "t_explanation": extract_section(ai_response, "T/F Explanation"),
            
            "i_label": map_score_to_label(mbti_scores['J/P'], 'J/P'),
            "i_score": mbti_scores['J/P'],
            "i_explanation": extract_section(ai_response, "J/P Explanation"),
            
            "personal_speech": extract_section(ai_response, "Personal Speech"),
            "third_person_diagnosis": extract_section(ai_response, "Third Person Diagnosis")
        }
        
        return MbtiOutput(**output)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
