from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
import os
import uuid
from pydantic import BaseModel

from core.database import get_supabase_client
from core.config import settings

app = FastAPI(title="AI Eye Contact Backend")

# Allow CORS for Next.js frontend
_ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS or ["*"],
    allow_credentials=bool(_ALLOWED_ORIGINS),
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
    """Receives a video file, saves it locally, and creates a pending job in Supabase."""
    if not file.filename or not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only .mp4 files are supported.")
        
    job_id = str(uuid.uuid4())
    
    # Save file to local uploads folder (used by worker on the same machine)
    safe_filename = f"{job_id}.mp4"
    file_path = os.path.join(UPLOADS_DIR, safe_filename)
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # Create database record
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase connection failed.")
        
    try:
        supabase.table("video_jobs").insert({
            "id": job_id,
            "user_id": user_id,
            "original_filename": file.filename,
            "video_path": file_path,
            "status": "pending"
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")
            
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Video uploaded successfully. Extraction job queued."
    )

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Retrieve current processing status for a video job."""
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        response = supabase.table("video_jobs").select("id, status, original_filename, file_path, created_at").eq("id", job_id).execute()
        jobs = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

    if not jobs:
        raise HTTPException(status_code=404, detail="Job not found.")

    return jobs[0]


@app.get("/api/download/{job_id}")
async def download_video(job_id: str):
    """Redirect to the Supabase Storage URL or stream the finished video file."""
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    try:
        response = supabase.table("video_jobs").select("status, file_path, original_filename").eq("id", job_id).execute()
        jobs = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

    if not jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    job = jobs[0]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video is not ready yet.")
        
    if not job.get("file_path"):
        raise HTTPException(status_code=404, detail="Output file not found on server.")
        
    # If file_path is a Supabase public URL, redirect the user
    if str(job["file_path"]).startswith("http"):
        return RedirectResponse(url=job["file_path"])

    # Fallback to local streaming if URL not available
    if not os.path.isfile(job["file_path"]):
        raise HTTPException(status_code=404, detail="Output file not found locally.")

    filename = f"eyecontact_{job['original_filename']}"
    return FileResponse(
        path=job["file_path"],
        media_type="video/mp4",
        filename=filename,
    )
