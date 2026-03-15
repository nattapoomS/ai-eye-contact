"""Standalone script to generate eye detection sample without database."""
import os
import sys
import cv2

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.processor import GazeProcessor

def generate_sample():
    """Process a single frame and save with eye detection boxes."""
    # Check for frames in temp_frames
    temp_frames_dir = "temp_frames"

    # Find the first job folder with frames
    if not os.path.exists(temp_frames_dir):
        print(f"Error: {temp_frames_dir} directory not found.")
        return False

    job_dirs = [d for d in os.listdir(temp_frames_dir) if os.path.isdir(os.path.join(temp_frames_dir, d))]
    if not job_dirs:
        print(f"Error: No job folders found in {temp_frames_dir}")
        return False

    # Use the first job folder
    job_id = job_dirs[0]
    frames_dir = os.path.join(temp_frames_dir, job_id)

    # Get first PNG frame
    frames = [f for f in os.listdir(frames_dir) if f.endswith('.png')]
    if not frames:
        print(f"Error: No PNG frames found in {frames_dir}")
        return False

    frame_path = os.path.join(frames_dir, frames[0])
    output_path = "../ai_eye_tracking_sample.png"

    print(f"Processing frame: {frame_path}")
    print(f"Initializing GazeProcessor...")

    # Initialize processor
    processor = GazeProcessor()

    if not processor.face_mesh:
        print("ERROR: Face mesh not initialized. MediaPipe may not be properly installed.")
        return False

    # Process the frame
    print(f"Detecting eyes and drawing boxes...")
    success = processor.process_frame(frame_path, output_path)

    if success:
        full_output_path = os.path.abspath(output_path)
        print(f"\n✓ Success! Sample saved to: {full_output_path}")

        # Verify the output has rectangles by checking it's different from input
        input_img = cv2.imread(frame_path)
        output_img = cv2.imread(output_path)

        if input_img is not None and output_img is not None:
            # Check if images are different
            diff = cv2.absdiff(input_img, output_img)
            diff_count = cv2.countNonZero(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY))

            if diff_count > 0:
                print(f"✓ Eye detection rectangles drawn (pixels changed: {diff_count})")
            else:
                print("⚠ Warning: Output appears identical to input (no rectangles drawn)")
                print("  This may mean no face was detected in the frame.")
    else:
        print("\n✗ Failed to process frame")

    return success

if __name__ == "__main__":
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generate_sample()
