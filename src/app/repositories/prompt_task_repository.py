from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from app.database import engine
from app.models.prompt_task import PromptTask, PromptTaskCreate

class PromptTaskRepository:
    def __init__(self):
        # Create tables if they don't exist
        PromptTask.metadata.create_all(engine)
    
    def create_task(self, task_id: str, task_data: PromptTaskCreate) -> PromptTask:
        """Create a new prompt task"""
        db_task = PromptTask(
            id=task_id,
            status=task_data.status,
            input_text=task_data.input_text,
            board_id=task_data.board_id,
            user_id=task_data.user_id,
            error=task_data.error,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with Session(engine) as session:
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task
    
    def get_task(self, task_id: str) -> Optional[PromptTask]:
        """Get a task by ID"""
        with Session(engine) as session:
            return session.get(PromptTask, task_id)
    
    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[PromptTask]:
        """Update a task with new data"""
        with Session(engine) as session:
            db_task = session.get(PromptTask, task_id)
            if not db_task:
                return None
            
            for key, value in update_data.items():
                if hasattr(db_task, key):
                    setattr(db_task, key, value)
            
            db_task.updated_at = datetime.utcnow()
            
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task
    
    def update_task_status(self, task_id: str, status: str, 
                          result: Optional[Dict[str, Any]] = None,
                          error: Optional[str] = None) -> Optional[PromptTask]:
        """Update a task's status, result, and error"""
        update_data = {"status": status}
        
        if status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.utcnow()
        
        if result is not None:
            update_data["result"] = result
            
        if error is not None:
            update_data["error"] = error
            
        return self.update_task(task_id, update_data)
    
    def get_tasks_by_user_id(self, user_id: str, limit: int = 10) -> List[PromptTask]:
        """Get tasks for a specific user by user ID"""
        with Session(engine) as session:
            statement = select(PromptTask).where(PromptTask.user_id == user_id).order_by(PromptTask.created_at.desc()).limit(limit)
            return list(session.exec(statement))
    
    def get_pending_tasks(self) -> List[PromptTask]:
        """Get all pending or processing tasks"""
        with Session(engine) as session:
            statement = select(PromptTask).where(
                (PromptTask.status == "pending") | (PromptTask.status == "processing")
            )
            return list(session.exec(statement))