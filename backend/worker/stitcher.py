"""Phase 4 — Stitch processed frames back into a finished video file."""
import os
import shutil
import subprocess
from traceback import format_exc

from core.config import settings
from core.database import get_supabase_client
from core.ffmpeg import find_ffmpeg


def _encode_video(frames_dir: str, temp_video: str, fps: int, ffmpeg: str) -> None:
    """Encode PNG frames → silent MP4 at the given fps."""
    frames = [f for f in os.listdir(frames_dir) if f.endswith(".png")]
    if not frames:
        raise FileNotFoundError(f"No PNG frames found in {frames_dir}")

    sample = sorted(frames)[0]
    pattern = "frame_%05d.png" if sample.startswith("frame_") else "%05d.png"
    input_pattern = os.path.join(frames_dir, pattern)

    cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-i", input_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-r", str(fps),
        "-an",
        temp_video,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed:\n{result.stderr}")


def _mux_audio(temp_video: str, audio_path: str, output_path: str, ffmpeg: str) -> None:
    """Mux silent video with audio; sync audio to video timeline."""
    cmd = [
        ffmpeg, "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-af", "aresample=async=1:first_pts=0",
        "-shortest",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg mux failed:\n{result.stderr}")


def _cleanup(job_id: str) -> None:
    """Remove temp_frames and processed_frames for this job."""
    for base_dir in (settings.TEMP_FRAMES_DIR, settings.PROCESSED_FRAMES_DIR):
        job_dir = os.path.join(base_dir, job_id)
        if os.path.isdir(job_dir):
            shutil.rmtree(job_dir)
            print(f"[{job_id}] Deleted {job_dir}")

    # Remove temp audio
    audio_path = os.path.join(settings.TEMP_AUDIO_DIR, f"{job_id}.aac")
    if os.path.isfile(audio_path):
        os.remove(audio_path)
        print(f"[{job_id}] Deleted {audio_path}")


def _update_db(job_id: str, status: str, file_path: str | None = None) -> None:
    """Update job status (and optionally file_path) in Supabase."""
    supabase = get_supabase_client()
    if not supabase:
        raise ConnectionError("Could not connect to database for status update.")
    
    data = {"status": status}
    if file_path:
        data["file_path"] = file_path
        
    try:
        supabase.table("video_jobs").update(data).eq("id", job_id).execute()
    except Exception as e:
        print(f"[{job_id}] DB Update Error: {e}")


def stitch_job(job_id: str) -> bool:
    """
    Full Phase 4 pipeline for a single job:
      1. Encode processed frames → silent MP4 at OUTPUT_FPS
      2. Mux with extracted audio
      3. Save finished file to uploads/finished/
      4. Cleanup temp dirs
      5. Update DB → completed
    Returns True on success, False on failure.
    """
    fps = settings.OUTPUT_FPS  # 30 fps
    frames_dir = os.path.join(settings.PROCESSED_FRAMES_DIR, job_id)
    audio_path = os.path.join(settings.TEMP_AUDIO_DIR, f"{job_id}.aac")
    finished_dir = settings.FINISHED_DIR
    os.makedirs(finished_dir, exist_ok=True)

    output_path = os.path.join(finished_dir, f"{job_id}.mp4")
    temp_video = os.path.join(finished_dir, f"{job_id}_tmp.mp4")

    try:
        ffmpeg = find_ffmpeg()
        print(f"[{job_id}] Using ffmpeg: {ffmpeg}")

        # Step 1 — Encode frames
        print(f"[{job_id}] Encoding {fps}fps video from processed frames...")
        _encode_video(frames_dir, temp_video, fps, ffmpeg)
        print(f"[{job_id}] Silent video encoded.")

        # Step 2 — Mux audio
        if os.path.isfile(audio_path):
            print(f"[{job_id}] Muxing audio...")
            _mux_audio(temp_video, audio_path, output_path, ffmpeg)
            os.remove(temp_video)
            print(f"[{job_id}] Audio muxed.")
        else:
            # No audio track — just rename temp as final output
            print(f"[{job_id}] No audio file found, saving video-only output.")
            os.rename(temp_video, output_path)

        # Step 3 — Cleanup
        print(f"[{job_id}] Cleaning up temp files...")
        _cleanup(job_id)

        # Step 3.5 - Upload to Supabase Storage
        print(f"[{job_id}] Uploading to Supabase Storage...")
        supabase = get_supabase_client()
        if supabase:
            try:
                with open(output_path, "rb") as f:
                    supabase.storage.from_("processed_videos").upload(
                        file=f,
                        path=f"{job_id}.mp4",
                        file_options={"content-type": "video/mp4"}
                    )
                public_url = supabase.storage.from_("processed_videos").get_public_url(f"{job_id}.mp4")
                
                # Step 4 — Update DB with Public URL, remove local file
                _update_db(job_id, "completed", public_url)
                if os.path.isfile(output_path):
                    os.remove(output_path)
                print(f"[{job_id}] Done. Output uploaded to Supabase: {public_url}")
                
            except Exception as e:
                print(f"[{job_id}] Supabase upload failed: {e}")
                # Fallback to local path if upload fails
                _update_db(job_id, "completed", output_path)
                print(f"[{job_id}] Done. Output saved locally (fallback).")
        else:
            # Step 4 — Update DB
            _update_db(job_id, "completed", output_path)
            print(f"[{job_id}] Done. Output saved locally: {output_path}")

        return True

    except Exception as e:
        print(f"[{job_id}] Stitching failed: {e}")
        print(format_exc())
        # Clean up any partial temp video
        if os.path.isfile(temp_video):
            os.remove(temp_video)
        try:
            _update_db(job_id, "failed")
        except Exception:
            pass
        return False
