# CLAUDE.md — AI Eye Contact Project

## Project Overview
Next.js 16 (App Router) + FastAPI Python backend + MySQL.
AI eye contact correction pipeline: upload MP4 → extract frames → MediaPipe AI processing → stitch back to video.

**Stack:**
- Frontend: Next.js 16, TypeScript, Tailwind v4, Framer Motion, GSAP, SWR, better-auth
- Backend: FastAPI, Python, MySQL (mysql-connector-python), MediaPipe, OpenCV, PyTorch
- Worker: Background job poller (`worker/job_poller.py`)
- Video: FFmpeg (WinGet install path on Windows)

**Run locally:** `start-local.bat` — opens 3 windows (Frontend :3000, Backend :8000, Worker)

---

## Code Style Preferences

### General
- ไม่ใส่ comment ที่ self-evident — แค่ใส่ตรงที่ logic ไม่ชัดเจน
- ไม่เพิ่ม error handling สำหรับ case ที่เกิดไม่ได้
- ไม่สร้างไฟล์ใหม่ถ้าแก้ไฟล์เดิมได้
- ไม่ abstract จนเกินไป — 3 บรรทัดที่คล้ายกันดีกว่า abstraction ที่ไม่จำเป็น

### TypeScript / React
- ใช้ `type` ไม่ใช่ `interface` ยกเว้นมี reason
- Hoist static data ออกนอก component (Vercel skill rule 6.3)
- ใช้ SWR สำหรับ polling/data fetching — ไม่ใช้ `setInterval` manual (rule 4.3)
- ใช้ ternary ไม่ใช้ `&&` สำหรับ conditional render (rule 6.8)
- `useCallback` เฉพาะ function ที่ส่งลง child หรือ dep ของ effect จริงๆ
- Dynamic import (`next/dynamic`) สำหรับ heavy component

### Python
- Type hints ทุก function signature
- ใช้ `ProcessPoolExecutor` สำหรับ CPU-bound tasks (AI frame processing)
- FFmpeg ให้ใช้ `find_ffmpeg()` จาก `core/ffmpeg.py` ไม่ hardcode path
- Database connection ต้อง close ใน `finally` block เสมอ

### Styling
- Tailwind utility classes — ไม่สร้าง custom CSS ถ้าไม่จำเป็น
- Dark theme: bg `#03030a` / `#050510`, accent blue-500/purple-500
- Glass morphism: `backdrop-blur`, `bg-white/5`, `border-white/10`
- Rounded corners: `rounded-2xl` / `rounded-3xl` เป็นหลัก

---

## Architecture Notes

### Job Pipeline & Status Flow
```
pending → extracting → processing → stitching → completed
                                              ↘ failed
```
- `main.py` — FastAPI API (upload, status, download)
- `worker/extractor.py` — FFmpeg: extract audio (.aac) + frames (.png)
- `ai/processor.py` — MediaPipe face landmark + multiprocess frame processing
- `worker/stitcher.py` — FFmpeg: encode 30fps video + mux audio → `uploads/finished/`
- `worker/job_poller.py` — polls MySQL every 5s, runs pipeline sequentially

### Key Paths (backend-relative)
- Source videos: `../uploads/{job_id}.mp4`
- Temp frames: `temp_frames/{job_id}/`
- Temp audio: `temp_audio/{job_id}.aac`
- Processed frames: `processed_frames/{job_id}/`
- Output: `../uploads/finished/{job_id}.mp4`

### DB Table: `video_jobs`
| column | type |
|---|---|
| id | varchar(255) PK |
| user_id | varchar(255) |
| original_filename | varchar(255) |
| video_path | varchar(255) |
| file_path | varchar(500) |
| status | enum(pending,extracting,processing,stitching,completed,failed) |
| created_at | timestamp |
| updated_at | timestamp |

### Next.js API Routes (proxy layer)
- `POST /api/upload` — injects `user_id` from better-auth session → forwards to `:8000`
- `GET /api/job/[jobId]` — auth guard → forwards to `:8000`
- Download: direct link to `http://localhost:8000/api/download/{job_id}`

---

## Environment
- `.env` — local dev (DB_HOST=localhost, DB_PORT=3307)
- `.env.docker` — Docker/production (DB_HOST=mysql, DB_PORT=3306)
- `NEXT_PUBLIC_BACKEND_URL` — public URL ของ backend (browser-facing)
- `BACKEND_URL` — internal URL ของ backend (server-side Next.js routes)

## Docker
```bash
docker compose up --build -d
```
Services: `mysql`, `backend`, `worker`, `frontend`
GPU: uncomment `deploy.resources` ใน `docker-compose.yml`

---

## What NOT to Do
- อย่า mock database ใน tests — เคยทำให้ prod fail มาแล้ว
- อย่า hardcode ffmpeg path — ใช้ `find_ffmpeg()` เสมอ
- อย่า reset jobs ที่ status=completed/failed โดยไม่ตั้งใจ
- อย่ารัน AI processing บน API request thread — ต้องผ่าน worker เสมอ
- อย่าลืม start worker (`python -m worker.job_poller`) ไม่งั้น jobs จะ stuck ที่ pending
