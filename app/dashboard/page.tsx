"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import Image from "next/image";
import { motion } from "framer-motion";
import { Instrument_Serif } from "next/font/google";
import {
  UploadCloud, FileVideo, Eye, Sparkles, FileWarning,
  LogOut, Download, CheckCircle, XCircle, RefreshCw,
} from "lucide-react";
import gsap from "gsap";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import useSWR from "swr";

const instrumentSerif = Instrument_Serif({ weight: "400", subsets: ["latin"], style: "italic" });

// ─── Types ───────────────────────────────────────────────────────────────────
type JobStatus = "pending" | "extracting" | "processing" | "stitching" | "completed" | "failed";

interface Job {
  id: string;
  status: JobStatus;
  original_filename: string;
}

// ─── Status step config ───────────────────────────────────────────────────────
const STEPS: { key: JobStatus; label: string }[] = [
  { key: "extracting", label: "Extracting frames" },
  { key: "processing", label: "AI eye correction" },
  { key: "stitching",  label: "Assembling video"  },
  { key: "completed",  label: "Ready!"            },
];

const STEP_ORDER: JobStatus[] = ["pending", "extracting", "processing", "stitching", "completed"];

function stepIndex(status: JobStatus) {
  return STEP_ORDER.indexOf(status);
}

const STATUS_LABEL: Record<JobStatus, string> = {
  pending:    "Queued — waiting to start…",
  extracting: "Extracting audio & frames…",
  processing: "AI correcting eye contact…",
  stitching:  "Assembling final video…",
  completed:  "Done! Your video is ready.",
  failed:     "Processing failed.",
};

// ─── Component ────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();

  useEffect(() => {
    if (!isPending && !session) router.push("/auth");
  }, [isPending, session, router]);

  const handleSignOut = async () => {
    await authClient.signOut();
    router.push("/");
  };

  // ── File state ──
  const [file, setFile]           = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // ── Job state ──
  const [jobId, setJobId] = useState<string | null>(null);

  // ── SWR polling (rule 4.3 — use SWR for automatic deduplication) ──
  const { data: job } = useSWR<Job>(
    jobId ? `/api/job/${jobId}` : null,
    (url: string) => fetch(url).then((r) => r.json()),
    {
      refreshInterval: (data) =>
        data?.status === "completed" || data?.status === "failed" ? 0 : 3000,
      revalidateOnFocus: false,
    }
  );

  // ── Refs for animation ──
  const containerRef   = useRef<HTMLDivElement>(null);
  const progressLineRef = useRef<HTMLDivElement>(null);
  const eyeIconRef     = useRef<SVGSVGElement>(null);

  // ── Dropzone ──
  const onDrop = useCallback((accepted: File[], rejected: any[]) => {
    setUploadError(null);
    if (rejected.length > 0) {
      setUploadError("Please upload a valid MP4 file (max 100 MB).");
      return;
    }
    if (accepted.length > 0) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "video/mp4": [".mp4"] },
    maxSize: 104_857_600,
    multiple: false,
  });

  // ── Entry animation ──
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from(".animate-in", {
        y: 30, opacity: 0, duration: 1.2, stagger: 0.15, ease: "power3.out",
      });
    }, containerRef);
    return () => ctx.revert();
  }, []);

  // ── Processing bar animation ──
  const isActive = job && job.status !== "completed" && job.status !== "failed";
  useEffect(() => {
    if (isActive && progressLineRef.current && eyeIconRef.current) {
      const tl = gsap.timeline({ repeat: -1 });
      tl.to(progressLineRef.current, { x: "100%", duration: 2, ease: "sine.inOut" })
        .to(progressLineRef.current, { x: "-100%", duration: 0 });
      gsap.to(eyeIconRef.current, {
        scale: 1.1, opacity: 0.8, duration: 1.5, repeat: -1, yoyo: true, ease: "sine.inOut",
      });
      return () => { tl.kill(); gsap.killTweensOf(eyeIconRef.current); };
    }
  }, [isActive]);


  // ── Upload handler ──
  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setUploadError(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch("/api/upload", { method: "POST", body: form });
      const data = await res.json();

      if (!res.ok) {
        setUploadError(data.error ?? data.detail ?? "Upload failed.");
        setIsUploading(false);
        return;
      }

      // SWR will start polling automatically once jobId is set
      setJobId(data.job_id);
    } catch {
      setUploadError("Network error — could not reach the server.");
    } finally {
      setIsUploading(false);
    }
  };

  // ── Reset ──
  const handleReset = () => {
    setFile(null);
    setJobId(null);
    setUploadError(null);
  };

  // ── Session guard ──
  if (isPending) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-7 h-7 rounded-full border-2 border-white/10 border-t-white/50 animate-spin" />
      </div>
    );
  }
  if (!session) return null;

  // ─── Derived ─────────────────────────────────────────────────────────────
  const jobStatus   = job?.status ?? (jobId ? "pending" : undefined);
  const isBusy      = isUploading || (!!jobId && jobStatus !== "completed" && jobStatus !== "failed");
  const isDone      = jobStatus === "completed";
  const isFailed    = jobStatus === "failed";
  const currentStep = jobStatus ? stepIndex(jobStatus) : -1;

  return (
    <div ref={containerRef} className="min-h-screen bg-black text-white flex flex-col relative overflow-hidden">

      {/* ── Background orbs ── */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
        <div style={{ animation: "orb-1 20s ease-in-out infinite" }}
          className="absolute top-[-15%] left-[20%] w-[500px] h-[500px] rounded-full bg-blue-600/15 blur-[100px]" />
        <div style={{ animation: "orb-2 25s ease-in-out infinite" }}
          className="absolute bottom-[-10%] right-[15%] w-[420px] h-[420px] rounded-full bg-purple-600/12 blur-[90px]" />
        <div style={{ animation: "orb-3 18s ease-in-out infinite" }}
          className="absolute top-[40%] left-[-10%] w-[350px] h-[350px] rounded-full bg-indigo-500/10 blur-[80px]" />
      </div>

      {/* ── Navbar ── */}
      <nav aria-label="Dashboard navigation" className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[calc(100%-3rem)] max-w-4xl">
        <div className="liquid-glass-pill rounded-full px-5 py-2 flex justify-between items-center">
          <div className="flex items-center gap-2.5 animate-in">
            <Image src="/logo.png" alt="AI Eye Contact" width={28} height={28} className="rounded-full" />
            <span className="font-medium text-sm text-white/80">
              Polaris<span className="text-white font-semibold">AI</span> Gaze
            </span>
          </div>
          <div className="flex items-center gap-3 animate-in">
            <span className="text-xs text-white/30 hidden sm:block truncate max-w-[160px]">{session.user.email}</span>
            <div className="w-px h-3.5 bg-white/10" />
            <button
              onClick={handleSignOut}
              aria-label="Sign out"
              className="flex items-center gap-1.5 text-xs text-white/35 hover:text-red-400 transition-colors rounded-full px-3 py-1.5 hover:bg-red-500/10"
            >
              <LogOut size={13} />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </nav>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 relative z-10">

        {/* Heading */}
        <motion.div
          className="text-center mb-10 animate-in"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <h1 className={`text-4xl md:text-5xl text-white mb-3 leading-tight ${instrumentSerif.className}`}>
            Fix your Eye Contact
          </h1>
          <p className="text-white/30 text-sm max-w-sm mx-auto">
            Drop an MP4 — AI corrects your gaze in minutes.
          </p>
        </motion.div>

        {/* Panel */}
        <motion.div
          className="w-full max-w-lg animate-in"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="liquid-glass-pill rounded-3xl p-8" style={{ borderRadius: "1.5rem" }}>

            {/* ── State: no file & no job ── */}
            {!file && !job && (
              <div
                {...getRootProps()}
                className={`border border-dashed rounded-2xl p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300
                  ${isDragActive ? "border-white/40 bg-white/5" : "border-white/10 hover:border-white/20 hover:bg-white/[0.03]"}`}
              >
                <input {...getInputProps()} />
                <div className="w-14 h-14 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-5">
                  <UploadCloud size={26} className="text-white/50" />
                </div>
                <p className="text-base font-medium text-white/80 mb-1">Drop your video here</p>
                <p className="text-xs text-white/25 mb-6">MP4 · up to 100 MB</p>
                <button className="bg-white/8 hover:bg-white/12 border border-white/10 px-5 py-2.5 rounded-full text-xs font-medium text-white/70 flex items-center gap-2 transition-all">
                  <FileVideo size={14} /> Browse Files
                </button>
              </div>
            )}

            {/* ── State: file selected ── */}
            {file && !job && !isUploading && (
              <div className="flex flex-col items-center">
                <div className="w-14 h-14 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-5">
                  <FileVideo size={26} className="text-white/60" />
                </div>
                <p className="text-sm font-medium mb-1 truncate max-w-xs text-white/80">{file.name}</p>
                <p className="text-xs text-white/25 mb-8">{(file.size / 1_048_576).toFixed(2)} MB</p>
                <div className="flex gap-3">
                  <button onClick={handleReset}
                    className="px-5 py-2.5 rounded-full text-xs text-white/40 hover:text-white/70 border border-white/10 hover:bg-white/5 transition-all">
                    Cancel
                  </button>
                  <button onClick={handleUpload}
                    className="bg-white/10 hover:bg-white/15 border border-white/15 px-6 py-2.5 rounded-full text-xs font-medium text-white flex items-center gap-2 transition-all">
                    <Sparkles size={13} className="text-white/60" /> Start Processing
                  </button>
                </div>
              </div>
            )}

            {/* ── State: uploading ── */}
            {isUploading && (
              <div className="flex flex-col items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                  <UploadCloud size={26} className="text-white/60 animate-bounce" />
                </div>
                <p className="text-sm font-medium text-white/70">Uploading…</p>
                <p className="text-xs text-white/25">Sending file to server</p>
              </div>
            )}

            {/* ── State: job running / done / failed ── */}
            {jobId && !isUploading && (
              <div className="flex flex-col items-center w-full gap-5">

                <div className="w-14 h-14 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                  {isDone    ? <CheckCircle size={26} className="text-emerald-400" />
                  : isFailed ? <XCircle    size={26} className="text-red-400" />
                  : <Eye ref={eyeIconRef} size={26} className="text-white/50" />}
                </div>

                <div className="text-center">
                  <p className="text-sm font-medium truncate max-w-xs text-white/80">
                    {job?.original_filename ?? file?.name ?? "Processing…"}
                  </p>
                  <p className={`text-xs mt-1 ${isDone ? "text-emerald-400" : isFailed ? "text-red-400" : "text-white/30"}`}>
                    {jobStatus ? STATUS_LABEL[jobStatus] : "Queued…"}
                  </p>
                </div>

                {/* Step pills */}
                {!isFailed && (
                  <div className="flex items-center gap-2 flex-wrap justify-center">
                    {STEPS.map((step, i) => {
                      const done    = currentStep > i + 1;
                      const active  = STEP_ORDER[currentStep] === step.key;
                      const reached = stepIndex(step.key) <= currentStep;
                      return (
                        <span key={step.key} className={`text-xs px-3 py-1 rounded-full border transition-all ${
                          done || (isDone && reached)
                            ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
                            : active
                            ? "border-white/20 bg-white/8 text-white/70 animate-pulse"
                            : "border-white/8 bg-white/[0.03] text-white/20"
                        }`}>
                          {step.label}
                        </span>
                      );
                    })}
                  </div>
                )}

                {/* Progress bar */}
                {isBusy && (
                  <div className="w-full">
                    <div className="h-px w-full bg-white/8 rounded-full overflow-hidden relative">
                      <div ref={progressLineRef}
                        className="absolute top-0 bottom-0 -left-full w-full bg-linear-to-r from-transparent via-white/40 to-transparent" />
                    </div>
                  </div>
                )}

                {isDone && (
                  <a href={`${process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000"}/api/download/${jobId}`}
                    download
                    className="bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 px-7 py-2.5 rounded-full text-xs font-medium text-emerald-300 flex items-center gap-2 transition-all">
                    <Download size={14} /> Download Video
                  </a>
                )}

                {(isDone || isFailed) && (
                  <button onClick={handleReset}
                    className="text-xs text-white/25 hover:text-white/50 flex items-center gap-1.5 transition-colors">
                    <RefreshCw size={12} /> Process another video
                  </button>
                )}
              </div>
            )}

            {/* Error */}
            {uploadError && (
              <div className="mt-5 flex items-center gap-2 text-red-400 text-xs p-3 rounded-xl bg-red-500/8 border border-red-500/15">
                <FileWarning size={14} />
                <span>{uploadError}</span>
              </div>
            )}

          </div>
        </motion.div>
      </main>
    </div>
  );
}
