import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { jobId } = await params;
  const res = await fetch(`${BACKEND}/api/job/${encodeURIComponent(jobId)}`);
  const data = await res.json();
  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }
  return NextResponse.json(data);
}
