import json
import asyncio
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.core.bot import ChatbotEngine, PERSONAS

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
bot_engine = ChatbotEngine()

class ChatRequest(BaseModel):
    session_id: str
    message: str
    persona: str = "assistant"

@router.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "personas": PERSONAS
    })

@router.get("/api/personas")
async def get_personas():
    return PERSONAS

@router.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    bot_engine.memory.add_message(payload.session_id, "user", payload.message)
    reply = bot_engine.generate_response(payload.message, payload.persona)
    bot_engine.memory.add_message(payload.session_id, "assistant", reply)
    return {"response": reply, "persona": payload.persona}

@router.get("/api/chat/stream")
async def chat_stream(
    session_id: str = Query(...),
    message: str = Query(...),
    persona: str = Query("assistant")
):
    async def event_generator():
        async for token in bot_engine.stream_response(session_id, message, persona):
            data = json.dumps({"token": token})
            yield f"data: {data}\n\n"
            await asyncio.sleep(0.02)
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/api/history/{session_id}")
async def get_history(session_id: str):
    history = bot_engine.memory.get_history(session_id)
    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in history]

@router.delete("/api/history/{session_id}")
async def clear_history(session_id: str):
    bot_engine.memory.clear(session_id)
    return {"status": "cleared", "session_id": session_id}
