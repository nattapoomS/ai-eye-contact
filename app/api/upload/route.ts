import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

// Allow up to 110 MB uploads through this route
export const maxDuration = 120; // seconds (Vercel/serverless timeout)
export const dynamic = "force-dynamic";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const formData = await req.formData();
  const file = formData.get("file") as File | null;
  if (!file) {
    return NextResponse.json({ error: "No file provided" }, { status: 400 });
  }

  // Forward to Python backend with the authenticated user's ID
  const backendForm = new FormData();
  backendForm.append("file", file);

  const res = await fetch(
    `${BACKEND}/api/upload?user_id=${encodeURIComponent(session.user.id)}`,
    { method: "POST", body: backendForm }
  );

  const data = await res.json();
  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }
  return NextResponse.json(data);
}
