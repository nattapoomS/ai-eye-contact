"use client";

import { useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Instrument_Serif } from "next/font/google";
import Image from "next/image";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import LightRays from '@/components/LightRays';
import GlassSurface from '@/components/GlassSurface'

const instrumentSerif = Instrument_Serif({
  weight: "400",
  subsets: ["latin"],
  style: "italic",
});

const FACES = [
  { src: "/faces/muman1.png", alt: "Person 1" },
  { src: "/faces/muman2.png", alt: "Person 2" },
  { src: "/faces/muman3.png", alt: "Person 3" },
  { src: "/faces/muman4.png", alt: "Person 4" },
  { src: "/faces/muman5.png", alt: "Person 5" },
];

export default function LandingPage() {
  const router = useRouter();
  const handPhoneRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (handPhoneRef.current) {
      gsap.fromTo(
        handPhoneRef.current,
        { y: 50, opacity: 0 },
        { 
          y: 0, 
          opacity: 1, 
          duration: 1, 
          ease: "power3.out",
          delay: 0.2 
        }
      );
    }
  }, []);

  return (
    
    <div className="min-h-screen bg-black text-white flex flex-col relative overflow-hidden">

        <div className="absolute inset-x-0 top-0 h-[600px] pointer-events-none z-0">
          <LightRays
              raysOrigin="top-center"
              raysColor="#743df5"
              raysSpeed={1}
              lightSpread={0.5}
              rayLength={1}
              followMouse={true}
              mouseInfluence={0.1}
              noiseAmount={0}
              distortion={0}
              className="custom-rays"
              pulsating={false}
              fadeDistance={1}
              saturation={1}
        />
        </div>

      {/* ── Navbar ── */}
      <nav className="fixed top-8 left-1/2 -translate-x-1/2 z-50">
        <div className="liquid-glass-pill flex items-center rounded-full px-8 py-0.1 gap-2.5">

          {/* Logo */}
          <button
            onClick={() => router.push("/")}
            className="px-4 py-1.5 text-sm text-white/75 hover:text-white hover:bg-white/5 transition-colors rounded-full"
          >
            Home
          </button>

          <div className="w-px h-0.5 bg-white/100 mx-1" />

          <button className="px-4 py-1.5 text-sm text-white/75 hover:text-white hover:bg-white/5 transition-colors rounded-full">
            Features
          </button>

          <button
            onClick={() => router.push("/")}
            className="flex items-center gap-2 pl-1 pr-1 py-1 rounded-full hover:bg-white/5 transition-colors"
          > 
          
          {/* Logo */}
            <Image src="/logo.png" alt="AI Eye Contact" width={40} height={40} className="rounded-full" />
          </button>

          <button className="px-4 py-1.5 text-sm text-white/75 hover:text-white hover:bg-white/5 transition-colors rounded-full">
            Beta
          </button>

          <div className="w-px h-0.5 bg-white/100 mx-1" />

          <button
            onClick={() => router.push("/auth?tab=signin")}
            className="px-4 py-1.5 text-sm text-white/75 hover:text-white hover:bg-white/5 transition-colors rounded-full mr-1"
          >
            Log in
          </button>

        </div>
      </nav>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col items-center justify-start pt-38 relative z-10">

        {/* Hero text */}
        <motion.div
          className="text-center px-4 mb-10"
          initial="hidden"
          animate="visible"
          variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.1 } } }}
        >
          <motion.h1
            variants={{
              hidden: { opacity: 0, y: 24 },
              visible: { opacity: 1, y: 0, transition: { duration: 0.2, ease: [0.22, 1, 0.36, 1] } },
            }}
            className={`text-6xl md:text-7xl text-white leading-[1.08] mb-4 ${instrumentSerif.className}`}
          >
            Generate Stunning
            <br />
            <span className="bg-linear-to-b from-blue-400 to-purple-200 bg-clip-text text-transparent">
              AI Eye Contact
            </span>
          </motion.h1>

          <motion.p
            variants={{
              hidden: { opacity: 0, y: 16 },
              visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
            }}
            className="text-white/40 text-sm md:text-base max-w-sm mx-auto mb-8 leading-relaxed"
          >
            Fix your eye contact in one click — look directly
            <br />
            at your audience, even while reading a script.[Beta Version]
          </motion.p>

          <motion.div
            variants={{
              hidden: { opacity: 0, scale: 0.92 },
              visible: { opacity: 1, scale: 1, transition: { duration: 0.4 } },
            }}
          >
<button
            onClick={() => router.push("/auth?tab=signup")}
            className=" px-8 py-2.5 text-sm"
          >
            <GlassSurface 
  width={150} 
  height={50}
  borderRadius={50}
  className="my-custom-class"
>
  <h2>Get Started</h2>
</GlassSurface>
          </button>
          </motion.div>
        </motion.div>

        {/* ── Hero Visual — infinite marquee ── */}
        {/*
          Math: card w-44 (176px) + mr-4 (16px) = 192px/unit
          10 cards × 192 = 1920px track → translateX(-50%) = -960px = 5 cards ✓
          Container w-2/3 on 1440px ≈ 960px → shows exactly 5 people
        */}
        <div className="relative w-full max-w-5xl mx-auto mt-6 group">
          
          {/* ── Marquee Layer (Bottom) ── */}
          <div className="relative overflow-hidden mask-horizontal">
            {/* Edge fades */}
            <div className="absolute inset-y-0 left-0 w-24 bg-linear-to-r from-black to-transparent pointer-events-none z-10" />
            <div className="absolute inset-y-0 right-0 w-24 bg-linear-to-l from-black to-transparent pointer-events-none z-10" />
            {/* Bottom fade */}
            <div className="absolute inset-x-0 bottom-0 h-24 bg-linear-to-t from-black to-transparent pointer-events-none z-10" />

            <div className="animate-marquee flex py-8">
              {[...FACES, ...FACES, ...FACES].map((face, i) => (
                <div
                  key={i}
                  className="relative flex-shrink-0 w-48 mr-6 h-48 rounded-2xl overflow-hidden border border-white/0 shadow-[0_8px_32px_rgba(0,0,0,0.5)]"
                >
                  <Image
                    src={face.src}
                    alt={face.alt}
                    fill
                    className="object-cover"
                    sizes="192px"
                    draggable={false}
                  />
                  <div className="absolute inset-x-0 bottom-0 h-16 bg-linear-to-t from-black/100 to-transparent" />
                </div>
              ))}
              <div className="absolute inset-x-0 bottom-0 h-16 bg-linear-to-t from-black/100 to-transparent" />
            </div>
          </div>

          {/* ── Hand Phone Layer (Top) ── */}
          <div className="absolute inset-0 mt-55 pr-30 z-20 flex items-center justify-center pointer-events-none">
            <div 
              ref={handPhoneRef}
              className="relative w-[400px] h-[780px] -translate-y-8"
            >
              <Image 
                src="/hand-phone.png" 
                alt="Hand holding phone" 
                fill 
                className="object-contain drop-shadow-[0_0_50px_rgba(0,0,0,0.8)]"
                priority
              />
            </div>
          </div>

        </div>

      </main>
    </div>
  );
}
