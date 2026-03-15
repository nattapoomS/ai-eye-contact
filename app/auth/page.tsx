"use client";

import { useState, useEffect, Suspense } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { Instrument_Serif } from "next/font/google";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { authClient } from "@/lib/auth-client";

const instrumentSerif = Instrument_Serif({ weight: "400", subsets: ["latin"], style: "italic" });

const FACES = [
  { src: "/faces/muman1.png", alt: "Person 1" },
  { src: "/faces/muman2.png", alt: "Person 2" },
  { src: "/faces/muman3.png", alt: "Person 3" },
  { src: "/faces/muman4.png", alt: "Person 4" },
  { src: "/faces/muman5.png", alt: "Person 5" },
];

function AuthForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab") === "signup" ? "signup" : "signin";

  const [tab, setTab] = useState<"signin" | "signup">(initialTab);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    setError(null);
    setSuccess(null);
    setName("");
    setEmail("");
    setPassword("");
  }, [tab]);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    const { error } = await authClient.signIn.email({ email, password });
    setIsLoading(false);
    if (error) {
      setError(error.message ?? "Sign in failed. Please try again.");
    } else {
      setSuccess("Signed in! Redirecting…");
      setTimeout(() => router.push("/dashboard"), 800);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    const { error } = await authClient.signUp.email({ name, email, password });
    setIsLoading(false);
    if (error) {
      setError(error.message ?? "Sign up failed. Please try again.");
    } else {
      setSuccess("Account created! Redirecting…");
      setTimeout(() => router.push("/dashboard"), 800);
    }
  };

  const inputClass =
    "w-full bg-white/[0.04] border border-white/10 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/20 transition-all focus:outline-none focus-visible:border-white/30 focus-visible:bg-white/[0.07]";

  return (
    <div className="min-h-screen bg-black text-white flex flex-col relative overflow-hidden">

      {/* ── Background: blurred marquee ── */}
      <div aria-hidden="true" className="absolute inset-0 flex items-center opacity-20 blur-sm pointer-events-none">
        <div className="animate-marquee flex">
          {[...FACES, ...FACES].map((face, i) => (
            <div key={i} className="relative flex-shrink-0 w-44 mr-4 h-screen">
              <Image src={face.src} alt="" fill className="object-cover object-top" sizes="176px" />
            </div>
          ))}
        </div>
      </div>
      {/* Dark overlay on top of bg */}
      <div aria-hidden="true" className="absolute inset-0 bg-black/60 pointer-events-none" />

      {/* ── Navbar (same as home) ── */}
      <nav className="fixed top-8 left-1/2 -translate-x-1/2 z-50">
        <div className="liquid-glass-pill flex items-center rounded-full px-5 py-1.5 gap-2">
          <button onClick={() => router.push("/")} className="flex items-center gap-2 rounded-full hover:bg-white/5 transition-colors px-2 py-1">
            <Image src="/logo.png" alt="AI Eye Contact" width={28} height={28} className="rounded-full" />
            <span className="text-sm text-white/70 hover:text-white transition-colors">Home</span>
          </button>
        </div>
      </nav>

      {/* ── Auth card ── */}
      <main className="flex-1 flex items-center justify-center relative z-10 px-4">
        <motion.div
          initial={{ opacity: 0, y: 24, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-[380px]"
        >
          <div className="liquid-glass-pill rounded-3xl overflow-hidden" style={{ borderRadius: "1.5rem" }}>
            <div className="p-8">

              {/* Header */}
              <div className="mb-8 text-center">
                <Image src="/logo.png" alt="AI Eye Contact" width={40} height={40} className="rounded-full mx-auto mb-4" />
                <h1 className={`text-2xl text-white mb-1 ${instrumentSerif.className}`}>
                  {tab === "signin" ? "Welcome back" : "Get started"}
                </h1>
                <p className="text-white/35 text-xs">
                  {tab === "signin" ? "Sign in to your account" : "Create your free account"}
                </p>
              </div>

              {/* Tab switcher */}
              <div role="tablist" className="flex bg-white/[0.04] rounded-full p-1 mb-6 border border-white/8">
                {(["signin", "signup"] as const).map((t) => (
                  <button
                    key={t}
                    role="tab"
                    aria-selected={tab === t}
                    onClick={() => setTab(t)}
                    className={`flex-1 text-xs font-medium py-2 rounded-full transition-all focus-visible:outline-none ${
                      tab === t
                        ? "bg-white/10 text-white border border-white/10"
                        : "text-white/35 hover:text-white/60"
                    }`}
                  >
                    {t === "signin" ? "Sign In" : "Sign Up"}
                  </button>
                ))}
              </div>

              {/* Status messages */}
              <AnimatePresence mode="wait">
                {error && (
                  <motion.div
                    key="error"
                    initial={{ opacity: 0, y: -6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -6 }}
                    role="alert"
                    aria-live="polite"
                    className="flex items-center gap-2 text-red-400 text-xs mb-4 bg-red-500/10 border border-red-500/20 rounded-xl px-3 py-2.5"
                  >
                    <AlertCircle size={13} className="shrink-0" />
                    <span>{error}</span>
                  </motion.div>
                )}
                {success && (
                  <motion.div
                    key="success"
                    initial={{ opacity: 0, y: -6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -6 }}
                    role="status"
                    aria-live="polite"
                    className="flex items-center gap-2 text-emerald-400 text-xs mb-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-3 py-2.5"
                  >
                    <CheckCircle size={13} className="shrink-0" />
                    <span>{success}</span>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Forms */}
              <AnimatePresence mode="wait">
                {tab === "signin" ? (
                  <motion.form
                    key="signin"
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 12 }}
                    transition={{ duration: 0.18 }}
                    onSubmit={handleSignIn}
                    className="flex flex-col gap-3"
                  >
                    <input
                      id="signin-email" type="email" name="email" autoComplete="email"
                      required spellCheck={false} placeholder="Email"
                      value={email} onChange={(e) => setEmail(e.target.value)}
                      className={inputClass}
                    />
                    <input
                      id="signin-password" type="password" name="password" autoComplete="current-password"
                      required placeholder="Password"
                      value={password} onChange={(e) => setPassword(e.target.value)}
                      className={inputClass}
                    />
                    <button type="button" className="text-xs text-white/30 hover:text-white/60 transition-colors self-end">
                      Forgot password?
                    </button>
                    <button
                      type="submit" disabled={isLoading}
                      className="w-full bg-white/10 hover:bg-white/15 border border-white/15 text-white font-medium rounded-2xl py-3 text-sm flex justify-center items-center gap-2 transition-all mt-1 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? <Loader2 size={15} className="animate-spin" /> : <>Sign In <ArrowRight size={13} /></>}
                    </button>
                  </motion.form>
                ) : (
                  <motion.form
                    key="signup"
                    initial={{ opacity: 0, x: 12 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -12 }}
                    transition={{ duration: 0.18 }}
                    onSubmit={handleSignUp}
                    className="flex flex-col gap-3"
                  >
                    <input
                      id="signup-name" type="text" name="name" autoComplete="name"
                      required placeholder="Full Name"
                      value={name} onChange={(e) => setName(e.target.value)}
                      className={inputClass}
                    />
                    <input
                      id="signup-email" type="email" name="email" autoComplete="email"
                      required spellCheck={false} placeholder="Email"
                      value={email} onChange={(e) => setEmail(e.target.value)}
                      className={inputClass}
                    />
                    <input
                      id="signup-password" type="password" name="password" autoComplete="new-password"
                      required placeholder="Password"
                      value={password} onChange={(e) => setPassword(e.target.value)}
                      className={inputClass}
                    />
                    <button
                      type="submit" disabled={isLoading}
                      className="w-full bg-white/10 hover:bg-white/15 border border-white/15 text-white font-medium rounded-2xl py-3 text-sm flex justify-center items-center gap-2 transition-all mt-1 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? <Loader2 size={15} className="animate-spin" /> : <>Create Account <ArrowRight size={13} /></>}
                    </button>
                  </motion.form>
                )}
              </AnimatePresence>

              {/* Switch tab hint */}
              <p className="text-center text-xs text-white/25 mt-5">
                {tab === "signin" ? (
                  <>Don&apos;t have an account?{" "}
                    <button onClick={() => setTab("signup")} className="text-white/50 hover:text-white transition-colors">Sign up</button>
                  </>
                ) : (
                  <>Already have an account?{" "}
                    <button onClick={() => setTab("signin")} className="text-white/50 hover:text-white transition-colors">Sign in</button>
                  </>
                )}
              </p>

            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}

export default function AuthPage() {
  return (
    <Suspense>
      <AuthForm />
    </Suspense>
  );
}
