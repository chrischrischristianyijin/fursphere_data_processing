from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class AIInput(BaseModel):
    input_data: dict

@app.post("/ai")
async def process_ai(input: AIInput):
    # 4. FastAPI AI Service Processes Data & Returns Resut
    ai_result = {"output": f"AI processed {input.input_data}"}  # AI Processing
    return ai_result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
