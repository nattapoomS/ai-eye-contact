"""Process all frames for a job with eye detection."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.processor import GazeProcessor

def process_all_frames():
    """Process all frames in temp_frames and save to processed_frames."""
    temp_frames_dir = "temp_frames"

    # Find job folders
    if not os.path.exists(temp_frames_dir):
        print(f"Error: {temp_frames_dir} directory not found.")
        return False

    job_dirs = [d for d in os.listdir(temp_frames_dir) if os.path.isdir(os.path.join(temp_frames_dir, d))]
    if not job_dirs:
        print(f"Error: No job folders found in {temp_frames_dir}")
        return False

    # Process each job
    for job_id in job_dirs:
        print(f"\n{'='*60}")
        print(f"Processing Job: {job_id}")
        print(f"{'='*60}")

        frames_dir = os.path.join(temp_frames_dir, job_id)
        output_dir = os.path.join("processed_frames", job_id)
        os.makedirs(output_dir, exist_ok=True)

        # Get all PNG frames
        frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
        total = len(frames)

        if total == 0:
            print(f"No frames found in {frames_dir}")
            continue

        print(f"Found {total} frames to process")

        # Initialize processor
        processor = GazeProcessor()

        if not processor.face_mesh:
            print("ERROR: Face mesh not initialized. Cannot process frames.")
            return False

        # Process each frame
        import time
        start_time = time.time()

        for i, frame_name in enumerate(frames):
            frame_path = os.path.join(frames_dir, frame_name)
            output_path = os.path.join(output_dir, frame_name)

            processor.process_frame(frame_path, output_path)

            if (i + 1) % 100 == 0 or i == total - 1:
                elapsed = time.time() - start_time
                fps = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"  Processed {i + 1}/{total} frames ({fps:.1f} FPS)")

        elapsed = time.time() - start_time
        print(f"\n✓ Job complete! {total} frames processed in {elapsed:.1f}s")
        print(f"✓ Output saved to: {output_dir}")

    return True

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    process_all_frames()
