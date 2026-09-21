from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CanvasPosition(BaseModel):
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0
    zIndex: int = 1

class NodeContent(BaseModel):
    title: str = ""
    payload: Any = None
    sha256: str = ""

class NodeMetadata(BaseModel):
    provider: str = "freellmapi"
    tokens: int = 0
    latency_ms: float = 0.0
    timestamp: str = ""

class HBOSCanvasNode(BaseModel):
    id: str
    operation_id: int = 233
    type: str = Field(..., description="episode | prompt | voiceover | video_clip | pattern | metric | orchestrator_node")
    position: CanvasPosition = Field(default_factory=CanvasPosition)
    content: NodeContent = Field(default_factory=NodeContent)
    relations: List[str] = Field(default_factory=list)
    metadata: NodeMetadata = Field(default_factory=NodeMetadata)
