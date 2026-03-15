import time
import os
from datetime import datetime
from core.database import get_db_connection
from worker.extractor import process_video_extraction
from worker.stitcher import stitch_job
from ai.processor import GazeProcessor

# Initialize the AI model once when the poller starts
gaze_processor = GazeProcessor()

def poll_jobs():
    """Polls the video_jobs table for 'pending' jobs, processes them, and updates status."""
    print(f"[{datetime.now().isoformat()}] Polling for pending jobs...")
    
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database.")
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Find a pending job
        cursor.execute("SELECT id, video_path FROM video_jobs WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1")
        job = cursor.fetchone()
        
        if not job:
            return  # No pending jobs
            
        job_id = job['id']
        video_path = job['video_path']
        
        print(f"Found pending job: {job_id}")
        
        # 2. Update status to 'extracting'
        cursor.execute("UPDATE video_jobs SET status = 'extracting' WHERE id = %s", (job_id,))
        conn.commit()
        
        # 3. Check if video file exists before extracting
        if not os.path.exists(video_path):
            print(f"[{job_id}] Video file not found: {video_path}")
            cursor.execute("UPDATE video_jobs SET status = 'failed' WHERE id = %s", (job_id,))
            conn.commit()
            return
            
        # 4. Extract audio and frames
        success = process_video_extraction(video_path, job_id)
        
        if success:
            # 5. Run AI Processing
            cursor.execute("UPDATE video_jobs SET status = 'processing' WHERE id = %s", (job_id,))
            conn.commit()

            ai_success = gaze_processor.process_job(job_id)

            if ai_success:
                # 6. Stitch frames → finished video (handles its own DB update)
                cursor.execute("UPDATE video_jobs SET status = 'stitching' WHERE id = %s", (job_id,))
                conn.commit()
                print(f"[{job_id}] Job state updated to: stitching")

                # Close DB connection before stitcher opens its own
                cursor.close()
                conn.close()

                stitch_job(job_id)
                return  # stitcher already updated DB to completed/failed
            else:
                cursor.execute("UPDATE video_jobs SET status = 'failed' WHERE id = %s", (job_id,))
                conn.commit()
                print(f"[{job_id}] Job state updated to: failed")
        else:
            cursor.execute("UPDATE video_jobs SET status = 'failed' WHERE id = %s", (job_id,))
            conn.commit()
            print(f"[{job_id}] Job state updated to: failed")
            
    except Exception as e:
        print(f"Error during polling: {e}")
        conn.rollback()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

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
