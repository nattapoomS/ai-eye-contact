import time
import os
from datetime import datetime
from core.database import get_supabase_client
from worker.extractor import process_video_extraction
from worker.stitcher import stitch_job
from ai.processor import GazeProcessor

# Initialize the AI model once when the poller starts
gaze_processor = GazeProcessor()

def poll_jobs():
    """Polls the video_jobs table for 'pending' jobs, processes them, and updates status."""
    print(f"[{datetime.now().isoformat()}] Polling for pending jobs...")
    
    supabase = get_supabase_client()
    if not supabase:
        print("Could not connect to database.")
        return
    
    try:
        # 1. Find a pending job
        response = supabase.table("video_jobs").select("id, video_path").eq("status", "pending").order("created_at").limit(1).execute()
        jobs = response.data
        
        if not jobs:
            return  # No pending jobs
            
        job_id = jobs[0]['id']
        video_path = jobs[0]['video_path']
        
        print(f"Found pending job: {job_id}")
        
        # 2. Update status to 'extracting'
        supabase.table("video_jobs").update({"status": "extracting"}).eq("id", job_id).execute()
        
        # 3. Check if video file exists before extracting
        if not os.path.exists(video_path):
            print(f"[{job_id}] Video file not found: {video_path}")
            supabase.table("video_jobs").update({"status": "failed"}).eq("id", job_id).execute()
            return
            
        # 4. Extract audio and frames
        success = process_video_extraction(video_path, job_id)
        
        if success:
            # 5. Run AI Processing
            supabase.table("video_jobs").update({"status": "processing"}).eq("id", job_id).execute()

            ai_success = gaze_processor.process_job(job_id)

            if ai_success:
                # 6. Stitch frames → finished video (handles its own DB update)
                supabase.table("video_jobs").update({"status": "stitching"}).eq("id", job_id).execute()
                print(f"[{job_id}] Job state updated to: stitching")

                stitch_job(job_id)
                return  # stitcher already updated DB to completed/failed
            else:
                supabase.table("video_jobs").update({"status": "failed"}).eq("id", job_id).execute()
                print(f"[{job_id}] Job state updated to: failed")
        else:
            supabase.table("video_jobs").update({"status": "failed"}).eq("id", job_id).execute()
            print(f"[{job_id}] Job state updated to: failed")
            
    except Exception as e:
        print(f"Error during polling: {e}")

if __name__ == "__main__":
    print("Starting video processing worker...")
    print("Watching `video_jobs` table for 'pending' records.")
    
    # Continuous polling loop
    try:
        while True:
            poll_jobs()
            time.sleep(5)  # Wait 5 seconds before polling again
    except KeyboardInterrupt:
        print("Worker stopped by user.")
