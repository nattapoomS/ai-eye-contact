# Hugging Face Spaces — Docker SDK
# Runs FastAPI + background worker via supervisord on port 7860
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# HF Spaces requires uid 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user:user requirements.koyeb.txt .
RUN pip install --no-cache-dir -r requirements.koyeb.txt

COPY --chown=user:user . .

# Directories used by the processing pipeline
RUN mkdir -p temp_audio temp_frames processed_frames $HOME/uploads/finished
ENV FINISHED_DIR=$HOME/uploads/finished

EXPOSE 7860

COPY --chown=user:user supervisord.hf.conf /tmp/supervisord.conf
CMD ["supervisord", "-n", "-c", "/tmp/supervisord.conf"]
