from typing import Dict, List
from pydantic import BaseModel
import time

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: float = 0.0

    def __init__(self, **data):
        if "timestamp" not in data or not data["timestamp"]:
            data["timestamp"] = time.time()
        super().__init__(**data)

class ConversationMemory:
    def __init__(self, max_history: int = 15):
        self.max_history = max_history
        self.sessions: Dict[str, List[ChatMessage]] = {}

    def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        msg = ChatMessage(role=role, content=content)
        self.sessions[session_id].append(msg)
        if len(self.sessions[session_id]) > self.max_history * 2:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history * 2:]
        return msg

    def get_history(self, session_id: str) -> List[ChatMessage]:
        return self.sessions.get(session_id, [])

    def clear(self, session_id: str) -> bool:
        if session_id in self.sessions:
            self.sessions[session_id] = []
            return True
        return False
