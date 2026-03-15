# คู่มือการ Deploy แบบใช้งานจริง (สายฟรี 100%)

โครงสร้างใหม่ตามแผน:
1. **Frontend (Website)** ➡️ **Vercel**
2. **Database & Storage** ➡️ **Supabase (PostgreSQL)**
3. **Backend AI** ➡️ **Hugging Face Spaces** (รันโมเดลหนักๆ ฟรี)

---

## ขั้นตอนที่ 1: ตั้งค่า Supabase (Database & Storage)
1. ไปที่เว็บ [Supabase](https://supabase.com) แล้วสมัคร/ล็อกอินให้เรียบร้อย
2. กด **New Project** ตั้งชื่อว่า `ai-eye-contact`
3. พอระบบสร้างเสร็จ (รอสักพัก) ให้ไปที่เมนู **Project Settings > API** จะเจอค่า 2 ตัวที่ต้องก็อปปี้ไว้:
   - `Project URL` (เอามาเป็น `SUPABASE_URL`)
   - `Project API Keys (service_role secret)` หรือ (anon public) (เอาแบบ **service_role** มาเป็น `SUPABASE_KEY` เพื่อให้หลังบ้านเราเข้าถึงได้ทุกอย่าง)
4. ไปที่เมนู **SQL Editor** ก๊อปปี้โค้ดด้านล่างนี้ไปรันเพื่อสร้างตาราง:
   ```sql
   CREATE TABLE IF NOT EXISTS video_jobs (
     id VARCHAR(255) PRIMARY KEY,
     user_id VARCHAR(255) NOT NULL,
     original_filename VARCHAR(255),
     video_path VARCHAR(255),
     file_path VARCHAR(500),
     status VARCHAR(50) DEFAULT 'pending',
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );
   ```
5. ไปที่เมนู **Storage** สร้าง **New Bucket** ชื่อ `processed_videos`
   - **สำคัญ**: กดเลือกตัวเลือก **"Public bucket"** ด้วยเพื่อให้คนกดดาวน์โหลดวิดีโอตอนเสร็จได้เลย!

---

## ขั้นตอนที่ 2: Deploy Backend AI ขึ้น Hugging Face Spaces (ฟรีโควต้า CPU ตัวแรง)
เราได้ทำการเขียน `Dockerfile.hf` สำหรับ Hugging Face เรียบร้อยแล้ว ขั้นตอนคือ:

1. ไปที่เว็บ [Hugging Face Spaces](https://huggingface.co/spaces) แล้วล็อกอิน
2. กด **Create new Space**
   - **Space name**: `ai-eye-contact-backend` (หรืออะไรก็ได้)
   - **License**: แล้วแต่
   - **Select the Space SDK**: เลือก **Docker** -> **Blank**
   - **Space Hardware**: เลือก **Free (CPU basic)** หรือถ้ามีเครดิตกด GPU ไปเลยก็เร็วกว่า!
3. เมื่อสร้างสเปซเสร็จ ให้กดแถบ **Settings** เลื่อนลงไปหา **Variables and secrets** > **New secret**:
   - ลิงก์ตู้ใส่ 2 ค่าจาก Supabase เมื่อกี้ ให้ตรงเป๊ะๆ:
   - `SUPABASE_URL` : (ลิงก์ของคุณ)
   - `SUPABASE_KEY` : (คีย์ service_role secret ของคุณ)
4. **อัปโหลดไฟล์ Backend ขึ้นไป**:
   - คุณต้องอัปโหลด **"แค่เฉพาะภายในโฟลเดอร์ \`backend/\` ทั้งโฟลเดอร์"** ขึ้นไปบน Repository ของ Hugging Face 
   - ให้แน่ใจว่าได้แก้ชื่อไฟล์ `Dockerfile.hf` ไปเป็น `Dockerfile` เฉยๆ เพื่อให้หน้าเว็บมันหาเจอ
5. รอ Hugging Face โหลด Build (ครั้งแรกอาจใช้เวลา 10 นาที) พอเสร็จระบบจะเปลี่ยนสถานะเป็น **Running**
6. กดปุ่ม `...` ตรงขวาบน -> กด **Embed this Space** แล้วก็อปปี้ URL ตัวจริงมา (เช่น `https://ชื่อคุณ-ai-eye-contact-backend.hf.space`) เก็บไว้ใช้ในขั้นตอนที่ 3

---

## ขั้นตอนที่ 3: Deploy Frontend ขี้น Vercel
1. เปิด Command Line / Terminal ทิ้งไว้ที่โฟลเดอร์หลักของโปรเจกต์ (`ai-eye-contact`)
2. พิมพ์คำสั่ง: `npx vercel` (ถ้ายังไม่เคยลงให้พิมพ์รหัสติดตั้งก่อน)
3. ระบบจะถามหาว่าจะฝากไว้โปรเจคไหน ให้ตอบ Enter เรื่อยๆ
4. มันจะถามหาตัวแปร **Environment Variables** ระหว่าง Build ให้เตรียมไว้ 2 ตัว:
   - `NEXT_PUBLIC_BACKEND_URL`: เอาลิงก์จากข้อ 2.6 มาวาง
   - `BACKEND_URL`: เอาลิงก์จากข้อ 2.6 มาวาง
   - (ส่วน Authentication จะเพิ่มอะไรอีกค่อยว่ากัน)
5. แค่นี้ก็ Deploy เว็บ Frontend เสร็จสมบูรณ์แล้ว พร้อมลุย!
