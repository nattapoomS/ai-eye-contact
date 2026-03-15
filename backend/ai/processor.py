import os
import cv2
import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

try:
    import mediapipe as mp
    from mediapipe.tasks.python.vision import FaceLandmarker
    import torch
except ImportError as e:
    print(f"Import error: {e}")

from core.config import settings

# ─── Module-level worker state (one MediaPipe instance per process) ───────────
_face_mesh = None

def _init_worker():
    """Called once per worker process — loads the MediaPipe model."""
    global _face_mesh
    try:
        model_path = os.path.expanduser("~/.mediapipe/face_landmarker.task")
        if not os.path.exists(model_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
        _face_mesh = FaceLandmarker.create_from_model_path(model_path)
    except Exception as e:
        print(f"[worker] MediaPipe init failed: {e} — running in copy-only mode")
        _face_mesh = None


def _process_single_frame(args: tuple) -> bool:
    """Top-level function so ProcessPoolExecutor can pickle it."""
    frame_path, output_path = args
    image = cv2.imread(frame_path)
    if image is None:
        return False

    if _face_mesh is None:
        cv2.imwrite(output_path, image)
        return True

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results = _face_mesh.detect(mp_image)

    if results and results.face_landmarks:
        landmarks = results.face_landmarks[0]
        h, w, _ = image.shape

        left_eye  = [33, 133, 159, 145]
        right_eye = [362, 263, 386, 374]

        def draw_box(indices):
            xs = [int(landmarks[i].x * w) for i in indices]
            ys = [int(landmarks[i].y * h) for i in indices]
            cv2.rectangle(image, (min(xs)-10, min(ys)-10), (max(xs)+10, max(ys)+10), (0, 255, 0), 2)

        draw_box(left_eye)
        draw_box(right_eye)

        for idx in (468, 473):
            if len(landmarks) > idx:
                cx = int(landmarks[idx].x * w)
                cy = int(landmarks[idx].y * h)
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)

    cv2.imwrite(output_path, image)
    return True


# ─── GazeProcessor ───────────────────────────────────────────────────────────

class GazeProcessor:
    def __init__(self):
        print("Initializing AI Gaze Processor...")
        # Check model availability without loading (workers load their own)
        self.model_path = os.path.expanduser("~/.mediapipe/face_landmarker.task")
        if not os.path.exists(self.model_path):
            print("Downloading face landmarker model...")
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, self.model_path)
            print("Model downloaded.")
        else:
            print("Face landmarker model found.")

        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            self.device = "cpu"
        print(f"Using device: {self.device}")

        # Number of parallel workers (leave 1 CPU for OS)
        self.num_workers = max(1, multiprocessing.cpu_count() - 1)
        print(f"Will use {self.num_workers} parallel worker(s)")

    def process_frame(self, frame_path: str, output_path: str) -> bool:
        """Process a single frame (used for single-frame calls)."""
        return _process_single_frame((frame_path, output_path))

    def process_job(self, job_id: str) -> bool:
        """Process all frames for a job using a multiprocess pool."""
        frames_dir = os.path.join(settings.TEMP_FRAMES_DIR, job_id)
        output_dir = os.path.join(settings.PROCESSED_FRAMES_DIR, job_id)

        if not os.path.exists(frames_dir):
            print(f"[{job_id}] Frames directory not found.")
            return False

        os.makedirs(output_dir, exist_ok=True)

        frames = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))
        total = len(frames)
        if total == 0:
            print(f"[{job_id}] No frames to process.")
            return False

        print(f"[{job_id}] Processing {total} frames with {self.num_workers} workers…")
        tasks = [
            (os.path.join(frames_dir, f), os.path.join(output_dir, f))
            for f in frames
        ]

        start = time.time()
        done = 0

        with ProcessPoolExecutor(
            max_workers=self.num_workers,
            initializer=_init_worker,
        ) as pool:
            futures = {pool.submit(_process_single_frame, t): t for t in tasks}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"[{job_id}] Frame error: {e}")
                done += 1
                if done % 100 == 0 or done == total:
                    elapsed = time.time() - start
                    fps = done / elapsed if elapsed > 0 else 0
                    print(f"[{job_id}] {done}/{total} frames ({fps:.1f} FPS)")

        elapsed = time.time() - start
        print(f"[{job_id}] Done in {elapsed:.1f}s ({total/elapsed:.1f} FPS avg)")
        return True
