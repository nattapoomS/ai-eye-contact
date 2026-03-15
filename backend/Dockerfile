# ── Stage: runtime ──────────────────────────────────────────────────────────
# Use CUDA base for GPU support. Swap to python:3.11-slim for CPU-only deploys.
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# System deps for OpenCV + ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python deps — install torch first (already in base image), skip re-download
COPY requirements.txt .
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    mysql-connector-python \
    ffmpeg-python \
    python-dotenv \
    pydantic \
    opencv-python-headless \
    mediapipe

# Copy source
COPY . .

# Ensure output directories exist
RUN mkdir -p temp_audio temp_frames processed_frames

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
