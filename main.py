from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.graph import app_graph
import app.config as config

app = FastAPI(
    title="Shadow Shield",
    description="An agentic gateway that locally anonymizes PII in user prompts before forwarding them to cloud LLMs",
    version="0.0.1"
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {
        "status": "running",
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        initial_state = {
            "original_text": request.message,
            "anonymized_text": "",
            "mapping": {},
            "llm_response": "",
            "deanonymized_response": ""
        }
        
        result = await app_graph.ainvoke(initial_state)
        
        return ChatResponse(response=result["deanonymized_response"])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error during graph execution: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
