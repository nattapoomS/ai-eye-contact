"""Combine processed frames into video with audio."""
import os
import subprocess
import sys

# Find ffmpeg executable (handles cases where PATH is not yet updated)
def find_ffmpeg():
    import shutil
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    # WinGet install path fallback
    winget_base = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    if os.path.isdir(winget_base):
        for pkg in os.listdir(winget_base):
            if "Gyan.FFmpeg" in pkg or "ffmpeg" in pkg.lower():
                candidate = os.path.join(winget_base, pkg)
                for root, dirs, files in os.walk(candidate):
                    if "ffmpeg.exe" in files:
                        return os.path.join(root, "ffmpeg.exe")
    raise FileNotFoundError("ffmpeg not found. Please ensure FFmpeg is installed.")

def create_video_with_audio():
    """Combine frames into video and add audio track."""
    ffmpeg = find_ffmpeg()
    print(f"Using ffmpeg: {ffmpeg}")

    job_id = "706d32ef-5c59-4786-95b0-2f7fcd5befd6"
    fps = 24  # Target FPS

    frames_dir = f"processed_frames/{job_id}"
    audio_path = f"temp_audio/{job_id}.aac"
    output_video = f"../output_video_{job_id}.mp4"

    # Check if frames exist
    if not os.path.exists(frames_dir):
        print(f"Error: Frames directory not found: {frames_dir}")
        return False

    frames = [f for f in os.listdir(frames_dir) if f.endswith('.png')]
    total_frames = len(frames)

    if total_frames == 0:
        print(f"Error: No frames found in {frames_dir}")
        return False

    print(f"Found {total_frames} frames")
    print(f"Target FPS: {fps}")
    print(f"Audio file: {audio_path}")

    # Create video from frames using ffmpeg
    # Use libx264 for video codec, yuv420p for compatibility
    temp_video = f"temp_video_{job_id}.mp4"

    print("\nStep 1: Creating video from frames...")

    # ffmpeg command to create video from frames
    # -framerate: input frame rate
    # -i: input file pattern (frame_00001.png, etc.)
    # -c:v libx264: video codec
    # -pix_fmt yuv420p: pixel format for compatibility
    # -r: output frame rate

    # Get the frame naming pattern
    sample_frame = sorted(frames)[0]
    if sample_frame.startswith("frame_"):
        pattern = "frame_%05d.png"
    else:
        pattern = "%05d.png"

    ffmpeg_cmd = [
        ffmpeg,
        "-y",  # Overwrite output files
        "-framerate", str(fps),
        "-i", f"{frames_dir}/{pattern}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",  # Quality (lower is better, 18 is visually lossless)
        "-r", str(fps),
        "-an",  # No audio yet
        temp_video
    ]

    print(f"Running: {' '.join(ffmpeg_cmd)}")
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error creating video: {result.stderr}")
        return False

    print(f"✓ Video created: {temp_video}")

    # Step 2: Add audio
    print("\nStep 2: Adding audio track...")

    if not os.path.exists(audio_path):
        print(f"Warning: Audio file not found: {audio_path}")
        print("Creating video without audio...")

        # Just rename temp video to output
        os.rename(temp_video, output_video)
        print(f"✓ Output video saved: {output_video}")
        return True

    # Combine video and audio — resample audio to match 24fps video duration exactly
    ffmpeg_cmd = [
        ffmpeg,
        "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",       # Copy video stream as-is
        "-c:a", "aac",        # AAC audio codec
        "-b:a", "192k",       # Audio bitrate
        "-af", f"aresample=async=1:first_pts=0",  # Sync audio to video timeline
        "-shortest",          # Match duration to shortest input
        output_video
    ]

    print(f"Running: {' '.join(ffmpeg_cmd)}")
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error adding audio: {result.stderr}")
        print("Keeping video without audio...")
        os.rename(temp_video, output_video)
    else:
        print(f"✓ Audio added successfully")

    # Cleanup temp video
    if os.path.exists(temp_video):
        os.remove(temp_video)
        print(f"✓ Cleaned up temp file")

    # Get output file info
    if os.path.exists(output_video):
        size_mb = os.path.getsize(output_video) / (1024 * 1024)
        print(f"\n{'='*60}")
        print(f"✓ Success! Output video created:")
        print(f"  File: {os.path.abspath(output_video)}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Frames: {total_frames}")
        print(f"  FPS: {fps}")
        print(f"  Duration: {total_frames/fps:.2f} seconds")
        print(f"{'='*60}")
        return True

    return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = create_video_with_audio()
    sys.exit(0 if success else 1)
