# Koyeb Deployment Guide

## Architecture บน Koyeb

| Service | Source | Port |
|---|---|---|
| `ai-eye-backend` | `backend/` + `Dockerfile.koyeb` | 8000 |
| `ai-eye-frontend` | root + `Dockerfile` | 3000 |
| MySQL | External (PlanetScale) | — |

> **Note:** Backend + Worker รวมอยู่ใน service เดียวด้วย supervisord เพราะต้องแชร์ filesystem สำหรับ temp frames/audio

---

## Step 1: ตั้ง External MySQL (PlanetScale)

1. ไปที่ [planetscale.com](https://planetscale.com) → สร้าง account + database ชื่อ `ai_eye_contact`
2. ไปที่ **Connect** → เลือก **Connect with: General** → copy connection string
3. เก็บค่าเหล่านี้ไว้:
   - `DB_HOST` (เช่น `aws.connect.psdb.cloud`)
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME` = `ai_eye_contact`
   - `DB_PORT` = `3306`

4. รัน schema ใน PlanetScale console:
```sql
CREATE TABLE IF NOT EXISTS video_jobs (
  id VARCHAR(255) PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  original_filename VARCHAR(255),
  video_path VARCHAR(255),
  file_path VARCHAR(500),
  status ENUM('pending','extracting','processing','stitching','completed','failed') DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

> ทางเลือกอื่น: [Aiven](https://aiven.io) (free tier MySQL), [Railway](https://railway.app)

---

## Step 2: Push โค้ดขึ้น GitHub

```bash
git add .
git commit -m "Add Koyeb deployment files"
git push origin main
```

---

## Step 3: Deploy Backend Service

1. [app.koyeb.com](https://app.koyeb.com) → **Create Service**
2. **Source:** GitHub → เลือก repo → branch `main`
3. **Build settings:**
   - Root directory: `backend`
   - Dockerfile: `Dockerfile.koyeb`
4. **Port:** `8000`
5. **Environment variables:**

| Key | Value |
|---|---|
| `DB_HOST` | ค่าจาก PlanetScale |
| `DB_PORT` | `3306` |
| `DB_USER` | ค่าจาก PlanetScale |
| `DB_PASSWORD` | ค่าจาก PlanetScale |
| `DB_NAME` | `ai_eye_contact` |

6. Deploy → รอ build เสร็จ → copy URL ของ service (เช่น `https://ai-eye-backend-xxx.koyeb.app`)

---

## Step 4: Deploy Frontend Service

1. **Create Service** อีกครั้ง
2. **Source:** GitHub → repo เดิม → branch `main`
3. **Build settings:**
   - Root directory: `.` (root)
   - Dockerfile: `Dockerfile`
   - **Build argument:** `NEXT_PUBLIC_BACKEND_URL=https://ai-eye-backend-xxx.koyeb.app` ← URL จาก Step 3
4. **Port:** `3000`
5. **Environment variables:**

| Key | Value |
|---|---|
| `BACKEND_URL` | `https://ai-eye-backend-xxx.koyeb.app` (same as above) |
| `BETTER_AUTH_SECRET` | random string ยาวๆ (ใช้ `openssl rand -hex 32`) |
| `BETTER_AUTH_URL` | `https://ai-eye-frontend-xxx.koyeb.app` ← URL ของ frontend |
| `NEXT_PUBLIC_BACKEND_URL` | `https://ai-eye-backend-xxx.koyeb.app` |

6. Deploy

---

## ⚠️ Storage Limitation

Koyeb free tier ใช้ **ephemeral storage** — ไฟล์จะหายเมื่อ service restart

**ผลกระทบ:** uploaded videos + processed videos จะหายถ้า backend restart

**แก้ไข (ระยะยาว):** migrate pipeline ไปใช้ object storage (Cloudflare R2 / AWS S3)
- Upload ตรงไปยัง R2 แทน local disk
- Worker ดึงไฟล์จาก R2, process, แล้ว upload กลับ
- Download URL ชี้ไป R2

สำหรับตอนนี้: Koyeb **Persistent Volumes** (paid plan) แก้ปัญหาได้โดยไม่ต้องเปลี่ยน code

---

## Troubleshooting

**Jobs stuck ที่ pending:**
Worker อาจ start ช้ากว่า API — ดู logs ของ service แล้วรอ supervisord start ทั้งคู่

**MediaPipe ช้ากว่าปกติ:**
CPU-only processing จะช้ากว่า GPU ประมาณ 5-10x — ปกติสำหรับ Koyeb free tier

**Frontend build fail:**
ตรวจสอบว่าใส่ `NEXT_PUBLIC_BACKEND_URL` เป็น build argument (ไม่ใช่แค่ env var)
