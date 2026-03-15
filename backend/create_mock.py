import os
import subprocess
import uuid
import shutil
from core.database import get_db_connection

def create_mock_job_with_real_video():
    source_video = r"C:\Users\Admin\ai-eye-contact\ai-eye-contact\vdotest\0305 (1)(6).mp4"
    print(f"Using source video: {source_video}")
    
    os.makedirs("test", exist_ok=True)
    video_path = os.path.abspath(os.path.join("test", "real_sample.mp4"))
    
    # Copy the real file instead of generating one
    shutil.copy2(source_video, video_path)
    print(f"Copied to: {video_path}")
    
    # Insert job
    job_id = str(uuid.uuid4())
    print(f"Job ID: {job_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO video_jobs (id, user_id, original_filename, video_path) VALUES (%s, %s, %s, %s)",
        (job_id, "mock_user", "0305 (1)(6).mp4", video_path)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Real job inserted. Now running job poller...")

if __name__ == "__main__":
    create_mock_job_with_real_video()
