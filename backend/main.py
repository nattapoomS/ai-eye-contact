from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime
from pydantic import BaseModel

from core.database import get_db_connection
from core.config import settings

app = FastAPI(title="AI Eye Contact Backend")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads dir if it doesn't exist
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

@app.post("/api/upload", response_model=JobResponse)
async def upload_video(user_id: str, file: UploadFile = File(...)):
    """Receives a video file, saves it, and creates a pending job in MySQL."""
    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only .mp4 files are supported.")
        
    job_id = str(uuid.uuid4())
    
    # Save file to uploads folder
    safe_filename = f"{job_id}.mp4"
    file_path = os.path.join(UPLOADS_DIR, safe_filename)
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # Create database record
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed.")
        
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO video_jobs (id, user_id, original_filename, video_path, status)
        VALUES (%s, %s, %s, %s, 'pending')
        """
        cursor.execute(query, (job_id, user_id, file.filename, file_path))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Video uploaded successfully. Extraction job queued."
    )

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Retrieve current processing status for a video job."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, status, original_filename, file_path, created_at FROM video_jobs WHERE id = %s",
            (job_id,)
        )
        job = cursor.fetchone()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        return job
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.get("/api/download/{job_id}")
async def download_video(job_id: str):
    """Stream the finished video file to the client."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT status, file_path, original_filename FROM video_jobs WHERE id = %s",
            (job_id,)
        )
        job = cursor.fetchone()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video is not ready yet.")
    if not job["file_path"] or not os.path.isfile(job["file_path"]):
        raise HTTPException(status_code=404, detail="Output file not found on server.")

    filename = f"eyecontact_{job['original_filename']}"
    return FileResponse(
        path=job["file_path"],
        media_type="video/mp4",
        filename=filename,
    )
