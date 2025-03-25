# app/routers/logo_router.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from typing import List, Optional
import os
import uuid
from datetime import datetime
from fastapi.responses import FileResponse
import aiofiles
import shutil
from app.authentication import verify_token  # Import authentication dependency

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "logos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# In-memory storage for logos (replace with database in production)
logos_db = {}
logo_id_counter = 1

def validate_file_extension(filename: str):
    """Validate if the file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File extension {ext} not allowed. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return ext

@router.post("/logo", response_model=dict)
async def upload_logo(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    token: str = Depends(verify_token)  # Require authentication
):
    """
    Upload a new logo file (.png, .jpg, .jpeg).
    """
    global logo_id_counter
    
    # Validate file extension
    ext = validate_file_extension(file.filename)
    
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save the file
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Create logo record
    logo_id = logo_id_counter
    logo_id_counter += 1
    
    logo_info = {
        "id": logo_id,
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_size": os.path.getsize(file_path),
        "file_type": file.content_type,
        "description": description,
        "upload_date": datetime.now().isoformat(),
        "last_modified": datetime.now().isoformat()
    }
    
    logos_db[logo_id] = logo_info
    
    return logo_info

@router.get("/logo", response_model=List[dict])
def get_logos(
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(verify_token)  # Require authentication
):
    """
    Get a list of all logo files.
    """
    logos = list(logos_db.values())
    start = min(skip, len(logos))
    end = min(skip + limit, len(logos))
    
    return logos[start:end]

@router.get("/logo/{logo_id}", response_model=dict)
def get_logo_by_id(
    logo_id: int,
    token: str = Depends(verify_token)  # Require authentication
):
    """
    Get logo information by ID.
    """
    if logo_id not in logos_db:
        raise HTTPException(status_code=404, detail="Logo not found")
    
    return logos_db[logo_id]

@router.put("/logo/{logo_id}", response_model=dict)
async def update_logo(
    logo_id: int,
    file: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None),
    token: str = Depends(verify_token)  # Require authentication
):
    """
    Update a logo file. Can update the file itself or description.
    """
    if logo_id not in logos_db:
        raise HTTPException(status_code=404, detail="Logo not found")
    
    logo = logos_db[logo_id]
    
    # Update file if provided
    if file:
        # Validate file extension
        ext = validate_file_extension(file.filename)
        
        # Delete old file
        if os.path.exists(logo["file_path"]):
            os.remove(logo["file_path"])
        
        # Generate a new unique filename
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the new file
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
                
            # Update file-related fields
            logo["filename"] = unique_filename
            logo["original_filename"] = file.filename
            logo["file_path"] = file_path
            logo["file_size"] = os.path.getsize(file_path)
            logo["file_type"] = file.content_type
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Update description if provided
    if description is not None:
        logo["description"] = description
    
    logo["last_modified"] = datetime.now().isoformat()
    
    return logo

@router.delete("/logo/{logo_id}", response_model=dict)
def delete_logo(
    logo_id: int,
    token: str = Depends(verify_token)  # Require authentication
):
    """
    Delete a logo file and its record.
    """
    if logo_id not in logos_db:
        raise HTTPException(status_code=404, detail="Logo not found")
    
    logo = logos_db[logo_id]
    
    # Delete the file from storage
    if os.path.exists(logo["file_path"]):
        os.remove(logo["file_path"])
    
    # Delete the record
    del logos_db[logo_id]
    
    return {"message": "Logo deleted successfully"}
