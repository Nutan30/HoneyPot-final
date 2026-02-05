from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

class Metadata(BaseModel):
    channel: Optional[str]
    language: Optional[str]
    locale: Optional[str]

class MessageRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[Metadata]=None

class MessageResponse(BaseModel):
    status: str
    reply: str
