from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Any
from fastapi import HTTPException
from src.workflows.content_workflow import run_workflow
from src.core.state_initializer import create_initial_state
from fastapi.middleware.cors import CORSMiddleware
from src.memory.memory_manager import memory_manager
from src.core.lifespan import lifespan
from fastapi import FastAPI

# =========================
# REQUEST MODEL
# =========================

class ContentRequest(BaseModel):
    query: str
    conversation_id: int

#class ConversationRequest(BaseModel):
#    user_id: str


#class ConversationResponse(BaseModel):
#    conversation_id: int

# =========================
# RESPONSE MODEL
# =========================

class ContentResponse(BaseModel):
    intent: str | None = None
    response: str | None = None
    workflow_step: str | None = None
    status: str

    active_agent: str | None = None
    confidence: float | None = None
    execution_time: float | None = None
    image_url: str | None = None

    trace: list[Any] = Field(default_factory=list)

app = FastAPI(
    title="Content Blitz AI",
    description="Multi-Agent Content Generation Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "application": "Content Blitz AI",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/conversation")
def create_conversation():

    user = memory_manager.postgres.get_or_create_user("demo_user")

    conversation = memory_manager.postgres.create_conversation(user.id,
                                                                title="New Chat")

    return {
        "conversation_id": conversation.id
    }

#@app.post(
#    "/conversation",
#    response_model=ConversationResponse
#)
#def create_conversation(request: ConversationRequest):
#
#    user = memory_manager.postgres.get_or_create_user(
#        request.user_id
#    )
#
#    conversation = memory_manager.postgres.create_conversation(
#        user.id
#    )
#
#    return {
#        "conversation_id": conversation.id
#    }
#
@app.post(
    "/generate",
    response_model=ContentResponse
)
def generate_content(request: ContentRequest):
    """
    Generate blog, LinkedIn content, research, or images
    using the Content Blitz AI workflow.
    """
   

    #result = run_workflow(state)
    try:
        state = create_initial_state(
        query=request.query,
        conversation_id=request.conversation_id
        )

        memory_manager.save_message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.query
        )

        history = memory_manager.get_short_term(
        request.conversation_id
        )

        state["conversation_history"] = history 
        result = run_workflow(state)
        memory_manager.save_message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=result["answer"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "intent": result.get("current_intent"),
        "response": result.get("answer"),
        "workflow_step": result.get("workflow_step"),
        "status": result.get("status"),
        "trace": result.get("trace", []),
        "execution_time": result.get("execution_time"),
        "image_url": result.get("image_url"),
        "confidence": result.get("confidence"),
        "active_agent": result.get("active_agent")
    }