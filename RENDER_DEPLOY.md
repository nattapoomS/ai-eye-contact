# คู่มือการ Deploy บน Render แบบ Full Stack (Next.js + FastAPI + MySQL)

เพื่อทำให้ระบบ AI Eye Contact ใช้งานได้อย่างสมบูรณ์บนแพลตฟอร์ม [Render](https://render.com) แนะนำให้ใช้เครื่องมือ Infrastructure as Code (Blueprint) ซึ่งทีมงานได้เตรียมไฟล์ `render.yaml` ไว้ให้เรียบร้อยแล้ว

## ขั้นตอนที่ 1: การเตรียมโค้ด
1. ตอนนี้ได้ทำการสร้างไฟล์ `render.yaml` ไว้ในโฟลเดอร์รหัสต้นฉบับแล้ว
2. คุณแค่ต้อง Commit โค้ดล่าสุดไปยัง GitHub
   ```bash
   git add .
   git commit -m "Add Render blueprint deployment settings"
   git push origin main
   ```

## ขั้นตอนที่ 2: Deploy ด้วย Blueprints (1-Click Deploy)
1. เปิดเว็บบราวเซอร์ของคุณที่ [Render Dashboard](https://dashboard.render.com/) ซึ่งคุณเปิดค้างไว้แล้ว
2. ทางเมนูด้านซ้าย เลือกคำว่า **Blueprints** พิมพ์เลือกปุ่ม **New Blueprint Instance**
3. เลือก **Connect a repository** แล้วเชื่อมต่อ GitHub `nattapoomS/ai-eye-contact` ขบวนการนี้ Render จะตรวจพบไฟล์ `render.yaml` แบบอัตโนมัติ
4. เมื่อกด **Apply** Render จะสร้างและโชว์ช่องให้คุณกรอกค่า Environment Variable บางตัว (ให้ใส่ค่าดังนี้ก่อน):
   - `NEXT_PUBLIC_BACKEND_URL`: ใส่ `https://example.com` (ใส่ดัมมี่ไว้ก่อน เพราะยังไม่ทราบ URL ของ Backend)
   - `BACKEND_URL`: ใส่ `https://example.com`
   - `BETTER_AUTH_URL`: ใส่ `https://example.com`
5. กดปุ่มสร้างระบบ รอประมาณ 1-3 นาทีจนกว่า **Database (`ai-eye-mysql`)** และ **Backend (`ai-eye-backend`)** จะ Build และ Start สำเร็จจนใช้งานได้

## ขั้นตอนที่ 3: อัปเดต URL จริงให้กับ Frontend
เนื่องจาก Frontend ของโปรเจกต์ (Next.js) และระบบ Login ต้องใช้ URL ที่ Render สุ่มให้ใหม่ เราต้องเอา URL จริงมาอัปเดต:

1. กลับไปที่หน้าหลักของ Dashboard (เมนู Dashboard หรือเลือกตามชื่อ Service)
2. ก๊อปปี้ URL จริงของ `ai-eye-backend` (เช่น `https://ai-eye-backend-xxx.onrender.com`)
3. ก๊อปปี้ URL จริงของ `ai-eye-frontend` (เช่น `https://ai-eye-frontend-xxx.onrender.com`)
4. เข้าไปแก้ไข (Edit) **Environment Variables** ของ Service `ai-eye-frontend` :
   - เปลี่ยนค่า `NEXT_PUBLIC_BACKEND_URL` เป็น URL จริงของ `ai-eye-backend`
   - เปลี่ยนค่า `BACKEND_URL` เป็น URL จริงของ `ai-eye-backend`
   - เปลี่ยนค่า `BETTER_AUTH_URL` เป็น URL จริงของ `ai-eye-frontend`
5. เมื่อ Save เสร็จแล้ว ให้ไปกดปุ่ม **Manual Deploy -> Clear Build Cache & Deploy** ในหน้า service `ai-eye-frontend` เพื่อให้ Next.js สร้างหน้าเว็บใหม่ด้วยค่า Connection URL ถาวรที่อัพเดทแล้ว

> **หมายเหตุข้อควรระวังเรื่อง Disk Persistence:**
> Backend มีการตั้งค่า Disk แบบ Persistent Mount Path ไว้ที่ `/uploads` เพื่อรองรับการอัพโหลดสคริปต์วิดีโอ ซึ่งไม่ว่าจะ Restart อีกกี่ร้อยรอบไฟล์บน Render ก็จะไม่หายไป (ฟรีแพลนใน Render อาจจะไม่มีฟีเจอร์ Disk ต้องเตรียมอัพเกรดเป็น Starter Plan สำหรับ Service Backend ซึ่งมีการกำหนดไว้ใน blueprint แล้ว!)
