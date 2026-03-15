import os
from ai.processor import GazeProcessor
from core.database import get_db_connection

def test_ai_processor():
    print("Testing the AI Loop individually...")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Get any job that has frames
    cursor.execute("SELECT id FROM video_jobs WHERE status IN ('processing', 'extracting') LIMIT 1")
    job = cursor.fetchone()
    conn.close()
    
    if not job:
        print("No test job found in DB. Make sure to run create_mock.py first.")
        return
        
    job_id = job['id']
    print(f"Testing on Job ID: {job_id}")
    
    # Initialize processor
    processor = GazeProcessor()
    
    # Process
    success = processor.process_job(job_id)
    if success:
        print("Success! Check backend/processed_frames/ for the output.")
    else:
        print("Failed.")

if __name__ == "__main__":
    test_ai_processor()
