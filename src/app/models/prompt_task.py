from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, JSON, Column
import json
from app.utils.custom_json import CustomJSONEncoder

class PromptTaskBase(SQLModel):
    """Base model for prompt tasks"""
    status: str  # "pending", "processing", "completed", "failed"
    input_text: str
    board_id: str
    user_id: Optional[str] = None  # Changed from user_name to user_id
    error: Optional[str] = None

class PromptTaskCreate(PromptTaskBase):
    """Model for creating a new prompt task"""
    pass

class PromptTask(PromptTaskBase, table=True):
    """SQLModel for prompt tasks with status information"""
    __tablename__ = "PromptTasks"
    
    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON), default=None)
    
    def to_dict(self):
        result_dict = {
            "id": self.id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "input_text": self.input_text,
            "board_id": self.board_id,
            "user_id": self.user_id,  # Changed from user_name to user_id
            "error": self.error,
        }
        
        if self.completed_at:
            result_dict["completed_at"] = self.completed_at.isoformat()
        
        if self.result:
            # Handle JSON serialization using custom encoder
            result_dict["result"] = json.loads(json.dumps(self.result, cls=CustomJSONEncoder))
        
        return result_dict