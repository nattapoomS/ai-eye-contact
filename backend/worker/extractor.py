import os
import subprocess
import time
from traceback import format_exc
from core.config import settings
from core.ffmpeg import find_ffmpeg

def extract_audio(video_path: str, job_id: str) -> str:
    """Extracts audio from video to temp_audio folder using FFmpeg."""
    audio_path = os.path.join(settings.TEMP_AUDIO_DIR, f"{job_id}.aac")

    ffmpeg_path = find_ffmpeg()
    cmd = [
        ffmpeg_path, "-y", "-i", video_path,
        "-q:a", "0", "-map", "a", audio_path
    ]
    
    print(f"[{job_id}] Extracting audio...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"[{job_id}] Audio extracted to {audio_path}")
    
    return audio_path

def extract_frames(video_path: str, job_id: str) -> str:
    """Extracts all frames from video to temp_frames/job_id/ folder using FFmpeg."""
    frames_dir = os.path.join(settings.TEMP_FRAMES_DIR, job_id)
    os.makedirs(frames_dir, exist_ok=True)
    
    frames_pattern = os.path.join(frames_dir, "%05d.png")
    
    ffmpeg_path = find_ffmpeg()
    cmd = [
        ffmpeg_path, "-y", "-i", video_path,
        "-vsync", "0", frames_pattern
    ]
    
    print(f"[{job_id}] Extracting frames...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Count generated frames
    frame_count = len([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    print(f"[{job_id}] Extracted {frame_count} frames to {frames_dir}")
    
    return frames_dir

def process_video_extraction(video_path: str, job_id: str) -> bool:
    """End-to-end extraction process for a single video."""
    start_time = time.time()
    try:
        extract_audio(video_path, job_id)
        extract_frames(video_path, job_id)
        
        elapsed = time.time() - start_time
        print(f"[{job_id}] Extraction completed successfully in {elapsed:.2f}s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[{job_id}] FFmpeg Extraction failed: {e}")
        return False
    except Exception as e:
        print(f"[{job_id}] Unexpected error during extraction: {e}")
        print(format_exc())
        return False
