from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any

from src.auth.dependencies import get_current_user
from src.memory.models import User
from src.workflows.content_workflow import run_workflow
from src.core.state_initializer import create_initial_state
from src.memory.memory_manager import memory_manager

router = APIRouter()


class ContentRequest(BaseModel):
    query: str
    conversation_id: int


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


@router.get("/")
def health_check():
    return {
        "application": "Content Blitz AI",
        "status": "running",
        "version": "1.0.0",
    }


@router.post("/conversation")
def create_conversation(
    current_user: User = Depends(get_current_user),
):

    conversation = memory_manager.postgres.create_conversation(
        current_user.id,
        title="New Chat",
    )

    return {
        "conversation_id": conversation.id
    }


@router.post(
    "/generate",
    response_model=ContentResponse,
)
def generate_content(
    request: ContentRequest,
    current_user: User = Depends(get_current_user),
):

    try:

        state = create_initial_state(
            query=request.query,
            conversation_id=request.conversation_id,
        )

        memory_manager.save_message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.query,
        )

        memory_manager.save_persistent_message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.query,
        )

        memory_manager.save_memory(
        user_id=current_user.id,
        conversation_id=request.conversation_id,
        content=request.query,
        memory_type="conversation",
        )

        history = memory_manager.get_short_term(
            request.conversation_id
        )

        memories = memory_manager.semantic_search(
        user_id=current_user.id,
        query=request.query,
        )

        state["retrieved_memories"] = memories

        state["conversation_history"] = history

        result = run_workflow(state)

        memory_manager.save_message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=result["answer"],
        )

        memory_manager.save_persistent_message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=result["answer"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    return {
        "intent": result.get("current_intent"),
        "response": result.get("answer"),
        "workflow_step": result.get("workflow_step"),
        "status": result.get("status"),
        "trace": result.get("trace", []),
        "execution_time": result.get("execution_time"),
        "image_url": result.get("image_url"),
        "confidence": result.get("confidence"),
        "active_agent": result.get("active_agent"),
    }