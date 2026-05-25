from fastapi import FastAPI
from src.workflows.content_workflow import run_workflow

app = FastAPI()

@app.get("/")
def health_check():
     return {
        "status": "running"
    }

@app.post("/generate")
def generate_content(query: str):

    state = {
        "user_id": "demo_user",
        "session_id": "session_001",
        "user_query": query,
        "conversation_history": [],
        "memory": [],
        "errors": [],
        "trace": []
    }

    result = run_workflow(state)

    return {
        "intent": result.get("current_intent"),
        "response": result.get("answer"),
        "workflow_step": result.get("workflow_step"),
        "status": result.get("status")
    }