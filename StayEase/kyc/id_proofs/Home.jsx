import React, { useState, useContext, useEffect, useRef } from "react";
import { AuthContext } from "./contecxt/auth_context";
import { useNavigate } from "react-router-dom";
import Login from "./pages/login";

const FRAME_COUNT = 148;

function currentFrame(index) {
  const idx = index.toString().padStart(3, "0");
  return `/videos/ezgif-frame-${idx}.png`;
}

// ─── Refined Color Palette ───
const C = {
  background:      "#F5F4EC",
  backgroundAlt:   "#EEEEE5",
  inkPrimary:      "#1C2B1A",
  inkMid:          "#3A4A38",
  inkLight:        "#9B9B8A",
  inkMuted:        "#B5B5A8",
  border:          "#C8C7B4",
  borderLight:     "#D8D7CA",
  ctaGreen:        "#1E3B1B",
  ctaGreenHover:   "#2A5226",
  ctaText:         "#F5F4EC",
  white:           "#FFFFFF",
  cream:           "#FAFAF5",
  accentGold:      "#C9A96E",
  accentGreen:     "#7DBB7A",
  error:           "#C62828",
  errorBg:         "#FFEBEE",
  success:         "#2E7D32",
  successBg:       "#E8F5E9",
};

// ─── Smooth Easing ───
const easeSmooth = "cubic-bezier(0.4, 0, 0.2, 1)";
const easeGentle = "cubic-bezier(0.25, 0.1, 0.25, 1)";

const injectStyles = () => {
  if (document.getElementById("se-v5-styles")) return;
  const s = document.createElement("style");
  s.id = "se-v5-styles";
  s.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { 
      background: ${C.background}; 
      overflow-x: hidden; 
      font-family: 'DM Sans', sans-serif;
      color: ${C.inkPrimary};
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
    ::selection {
      background: rgba(30, 59, 27, 0.15);
      color: ${C.inkPrimary};
    }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: ${C.border}; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: ${C.inkLight}; }

    .se5-root {
      font-family: 'DM Sans', sans-serif;
      color: ${C.inkPrimary};
      background: ${C.background};
      -webkit-font-smoothing: antialiased;
    }
    .se5-max { max-width: 1280px; margin: 0 auto; width: 90%; }

    /* ── NAV ── */
    .se5-nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      height: 70px; display: flex; align-items: center;
      transition: all 0.5s ${easeGentle}; padding: 0 24px;
    }
    @media (min-width: 1024px) { .se5-nav { padding: 0 56px; height: 80px; } }
    .se5-nav.hidden { opacity: 0; transform: translateY(-100%); pointer-events: none; }
    .se5-nav.light-nav {
      background: rgba(245, 244, 236, 0.95);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-bottom: 1px solid ${C.borderLight};
      box-shadow: 0 1px 20px rgba(0,0,0,0.04);
    }
    .se5-logo {
      font-family: 'Cormorant Garamond', serif;
      font-size: 18px; font-weight: 600; letter-spacing: 0.15em;
      text-transform: uppercase; color: ${C.inkPrimary}; text-decoration: none;
      display: flex; align-items: center; gap: 8px;
      transition: opacity 0.3s;
    }
    .se5-logo:hover { opacity: 0.7; }
    .se5-navlinks { display: none; gap: 32px; }
    @media (min-width: 1024px) { .se5-navlinks { display: flex; } }
    .se5-navlinks a { position: relative; padding-bottom: 4px; }
    .se5-navlinks a::after {
      content: ''; position: absolute; bottom: 0; left: 0;
      width: 0; height: 1px; background: currentColor;
      transition: width 0.3s ${easeSmooth};
    }
    .se5-navlinks a:hover::after { width: 100%; }

    /* ── SECTIONS ── */
    .se5-section { padding: 60px 0; }
    @media (min-width: 768px) { .se5-section { padding: 100px 0; } }
    .se5-grid {
      display: grid; grid-template-columns: 1fr; gap: 32px;
    }
    @media (min-width: 640px)  { .se5-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (min-width: 1024px) { .se5-grid { grid-template-columns: repeat(3, 1fr); } }

    .se5-stats-strip {
      display: grid; grid-template-columns: 1fr;
      background: rgba(255,255,255,0.1); gap: 1px;
    }
    @media (min-width: 768px) { .se5-stats-strip { grid-template-columns: repeat(3, 1fr); } }

    .se5-btn {
      font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase;
      font-weight: 600; padding: 14px 28px; border-radius: 2px;
      cursor: pointer; transition: all 0.3s ${easeSmooth}; border: none;
      position: relative; overflow: hidden;
    }
    .se5-btn::before {
      content: ''; position: absolute; top: 0; left: -100%;
      width: 100%; height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
      transition: left 0.5s;
    }
    .se5-btn:hover::before { left: 100%; }
    .se5-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(30, 59, 27, 0.2); }
    .se5-btn:active { transform: translateY(0); }
    @media (max-width: 480px) { .se5-btn { width: 100%; } }

    /* ── FLOATING SEARCH BAR ── */
    .se5-float-search {
      display: flex; align-items: center;
      background: ${C.white}; border-radius: 999px;
      padding: 14px 14px 14px 32px; width: 100%; max-width: 720px;
      box-shadow: 0 12px 48px rgba(0,0,0,0.2), 0 2px 8px rgba(0,0,0,0.1);
      gap: 16px; position: relative;
      transition: transform 0.3s ${easeSmooth}, box-shadow 0.3s;
    }
    .se5-float-search:focus-within {
      transform: translateY(-2px);
      box-shadow: 0 16px 56px rgba(0,0,0,0.25), 0 4px 12px rgba(0,0,0,0.15);
    }
    .se5-float-search-inner { flex: 1; display: flex; flex-direction: column; min-width: 0; }
    .se5-float-label {
      font-size: 11px; font-weight: 600; letter-spacing: 0.2em;
      text-transform: uppercase; color: ${C.inkLight}; margin-bottom: 4px; line-height: 1;
    }
    .se5-float-input {
      border: none; outline: none; background: transparent;
      font-family: 'DM Sans', sans-serif; font-size: 16px; font-weight: 500;
      letter-spacing: 0.06em; text-transform: uppercase;
      color: ${C.inkPrimary}; width: 100%; padding: 0;
    }
    .se5-float-input::placeholder { color: ${C.inkLight}; font-weight: 500; }
    .se5-float-input:disabled { opacity: 0.6; }
    .se5-float-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .se5-near-btn {
      background: transparent; border: 1.5px solid ${C.border}; border-radius: 999px;
      height: 52px; padding: 0 18px; display: flex; align-items: center; gap: 8px;
      cursor: pointer; font-family: 'DM Sans', sans-serif; font-size: 11px;
      font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
      color: ${C.inkMid}; transition: all 0.3s ${easeSmooth}; white-space: nowrap;
    }
    .se5-near-btn:hover { border-color: ${C.ctaGreen}; color: ${C.ctaGreen}; background: rgba(30,59,27,0.04); }
    .se5-near-btn:disabled { opacity: 0.45; cursor: not-allowed; }
    .se5-near-btn.locating { border-color: ${C.ctaGreen}; color: ${C.ctaGreen}; }

    .se5-round-search-btn {
      width: 52px; height: 52px; border-radius: 50%; background: ${C.ctaGreen};
      border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; transition: all 0.3s ${easeSmooth}; position: relative; overflow: hidden;
    }
    .se5-round-search-btn::after {
      content: ''; position: absolute; inset: 0;
      background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
      opacity: 0; transition: opacity 0.3s;
    }
    .se5-round-search-btn:hover::after { opacity: 1; }
    .se5-round-search-btn:hover { background: ${C.ctaGreenHover}; transform: scale(1.08); box-shadow: 0 4px 16px rgba(30, 59, 27, 0.3); }
    .se5-round-search-btn:active { transform: scale(0.95); }
    .se5-round-search-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

    .se5-float-status {
      margin-top: 16px; font-size: 13px; color: rgba(255,255,255,0.8);
      font-family: 'DM Sans', sans-serif; text-align: center; min-height: 20px;
      display: flex; align-items: center; justify-content: center; gap: 6px;
      letter-spacing: 0.02em; transition: all 0.3s;
    }
    .se5-float-status.on-light { color: ${C.inkLight}; }
    .se5-float-status.error { color: ${C.error}; }
    .se5-float-status.success { color: ${C.success}; }

    @keyframes locPulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.3; transform: scale(1.5); }
    }
    .loc-pulse { animation: locPulse 1s ease-in-out infinite; }

    /* ── HOSTEL CARDS ── */
    .hostel-card {
      border: 1px solid ${C.borderLight}; background: ${C.white};
      transition: all 0.4s ${easeSmooth}; cursor: pointer;
      border-radius: 12px; overflow: hidden; position: relative;
    }
    .hostel-card::before {
      content: ''; position: absolute; inset: 0;
      background: linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.02) 100%);
      opacity: 0; transition: opacity 0.4s; pointer-events: none; z-index: 1;
    }
    .hostel-card:hover::before { opacity: 1; }
    .hostel-card:hover {
      transform: translateY(-8px);
      box-shadow: 0 20px 40px rgba(0,0,0,0.1);
      border-color: ${C.border};
    }
    .hostel-image-wrapper { height: 240px; position: relative; overflow: hidden; }
    .hostel-image-wrapper img {
      width: 100%; height: 100%; object-fit: cover;
      transition: transform 0.6s ${easeSmooth};
    }
    .hostel-card:hover .hostel-image-wrapper img { transform: scale(1.08); }
    .hostel-image-placeholder {
      height: 240px;
      background: linear-gradient(135deg, ${C.backgroundAlt} 0%, ${C.background} 100%);
      display: flex; align-items: center; justify-content: center;
      color: ${C.inkLight}; font-size: 14px; position: relative; overflow: hidden;
    }
    .hostel-image-placeholder::after {
      content: ''; position: absolute; inset: 0;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239B9B8A' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
      opacity: 0.5;
    }
    .hostel-badge {
      position: absolute; top: 16px; left: 16px;
      padding: 6px 12px; border-radius: 20px;
      font-size: 11px; font-weight: 600;
      letter-spacing: 0.05em; text-transform: uppercase;
      z-index: 2; backdrop-filter: blur(8px);
    }
    .hostel-badge.available { background: rgba(46, 125, 50, 0.9); color: white; }
    .hostel-badge.unavailable { background: rgba(198, 40, 40, 0.9); color: white; }
    .hostel-badge.featured { background: rgba(201, 169, 110, 0.9); color: ${C.inkPrimary}; }

    .availability-badge {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 12px; font-size: 11px; font-weight: 600;
      border-radius: 20px; margin-top: 12px; letter-spacing: 0.02em;
    }
    .availability-badge.available { background: ${C.successBg}; color: ${C.success}; border: 1px solid #a5d6a7; }
    .availability-badge.unavailable { background: ${C.errorBg}; color: ${C.error}; border: 1px solid #ef9a9a; }

    .clear-search-btn {
      background: transparent; border: 1.5px solid ${C.border};
      padding: 10px 20px; border-radius: 6px; font-size: 12px;
      font-weight: 600; letter-spacing: 0.05em; cursor: pointer;
      transition: all 0.3s ${easeSmooth}; color: ${C.inkMid};
      display: inline-flex; align-items: center; gap: 8px;
    }
    .clear-search-btn:hover {
      border-color: ${C.ctaGreen}; color: ${C.ctaGreen};
      background: rgba(30, 59, 27, 0.04); transform: translateY(-1px);
    }
    .section-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 48px; flex-wrap: wrap; gap: 16px;
    }

    /* ── ANIMATIONS ── */
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes slideIn {
      from { opacity: 0; transform: translateX(-20px); }
      to { opacity: 1; transform: translateX(0); }
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .animate-fade-in-up { animation: fadeInUp 0.6s ${easeSmooth} forwards; }
    .animate-fade-in { animation: fadeIn 0.4s ${easeSmooth} forwards; }
    .animate-slide-in { animation: slideIn 0.5s ${easeSmooth} forwards; }
    .stagger-1 { animation-delay: 0.1s; }
    .stagger-2 { animation-delay: 0.2s; }
    .stagger-3 { animation-delay: 0.3s; }
    .stagger-4 { animation-delay: 0.4s; }
    .stagger-5 { animation-delay: 0.5s; }
    .stagger-6 { animation-delay: 0.6s; }

    /* ── LOADING STATES ── */
    .skeleton {
      background: linear-gradient(90deg, ${C.backgroundAlt} 25%, ${C.background} 50%, ${C.backgroundAlt} 75%);
      background-size: 200% 100%;
      animation: skeleton 1.5s infinite;
      border-radius: 4px;
    }
    @keyframes skeleton {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* ── SCROLL REVEAL ── */
    .reveal {
      opacity: 0; transform: translateY(24px);
      transition: all 0.6s ${easeSmooth};
    }
    .reveal.visible { opacity: 1; transform: translateY(0); }
  `;
  document.head.appendChild(s);
};

// ─── Icon Components ───
const SearchSVG = ({ color = "#fff", size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 18 18" fill="none">
    <circle cx="7.5" cy="7.5" r="5.5" stroke={color} strokeWidth="1.8" />
    <path d="M12 12L16 16" stroke={color} strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

const LocSVG = ({ pulsing = false, color = C.inkMid }) => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none"
    className={pulsing ? "loc-pulse" : ""} style={{ flexShrink: 0 }}>
    <circle cx="8" cy="8" r="3" fill={color} />
    <circle cx="8" cy="8" r="5.5" stroke={color} strokeWidth="1.5" />
    <line x1="8" y1="1" x2="8" y2="2.5" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    <line x1="8" y1="13.5" x2="8" y2="15" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    <line x1="1" y1="8" x2="2.5" y2="8" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    <line x1="13.5" y1="8" x2="15" y2="8" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

const ArrowRightSVG = ({ size = 16, color = C.inkPrimary }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);

const StarSVG = ({ size = 14, filled = true }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={filled ? "#FFB800" : "none"} stroke="#FFB800" strokeWidth="1.5">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
);

// ─── Scroll Reveal Hook ───
function useScrollReveal() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );
    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);
}

// ─── Canvas Hero ───
function CanvasHero({ onScrollProgress, onSearchResults }) {
  const canvasRef  = useRef(null);
  const wrapperRef = useRef(null);
  const imagesRef  = useRef([]);
  const scrollRef  = useRef(0);
  const rafRef     = useRef();
  const [progress, setProgress] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    let loadedCount = 0;
    for (let i = 1; i <= FRAME_COUNT; i++) {
      const img = new Image();
      img.onload = () => {
        loadedCount++;
        if (loadedCount === FRAME_COUNT) setIsLoaded(true);
      };
      img.src = currentFrame(i);
      imagesRef.current[i - 1] = img;
    }

    const onScroll = () => {
      if (!wrapperRef.current) return;
      const { top, height } = wrapperRef.current.getBoundingClientRect();
      let f = -top / (height - window.innerHeight);
      f = Math.max(0, Math.min(1, f));
      scrollRef.current = f;
      setProgress(f);
      onScrollProgress(f);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [onScrollProgress]);

  useEffect(() => {
    const draw = () => {
      const canvas = canvasRef.current;
      if (canvas && imagesRef.current.length > 0) {
        const idx = Math.min(FRAME_COUNT - 1, Math.floor(scrollRef.current * (FRAME_COUNT - 1)));
        const img = imagesRef.current[idx];
        if (img && img.complete) {
          const ctx = canvas.getContext("2d", { alpha: false });
          const cw = canvas.width, ch = canvas.height;
          const iw = img.naturalWidth, ih = img.naturalHeight;
          const ratio = Math.max(cw / iw, ch / ih);
          const nw = iw * ratio, nh = ih * ratio;
          ctx.clearRect(0, 0, cw, ch);
          ctx.drawImage(img, (cw - nw) / 2, (ch - nh) / 2, nw, nh);
        }
      }
      rafRef.current = requestAnimationFrame(draw);
    };
    rafRef.current = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  useEffect(() => {
    const onResize = () => {
      if (canvasRef.current) {
        canvasRef.current.width  = window.innerWidth;
        canvasRef.current.height = window.innerHeight;
      }
    };
    onResize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const textOpacity = progress <= 0.05
    ? 1
    : Math.max(0, 1 - (progress - 0.05) / 0.15);

  const handleSearchResults = (results, location) => {
    if (onSearchResults) {
      onSearchResults(results, location);
    }
  };

  return (
    <div ref={wrapperRef} style={{ height: "400vh", position: "relative" }}>
      <div style={{
        position: "sticky", top: 0, height: "100vh",
        width: "100vw", overflow: "hidden", background: "#000",
      }}>
        <canvas ref={canvasRef} style={{ display: "block", width: "100%", height: "100%" }} />

        {/* Loading indicator */}
        {!isLoaded && (
          <div style={{
            position: "absolute", inset: 0,
            display: "flex", alignItems: "center", justifyContent: "center",
            background: "rgba(0,0,0,0.8)",
          }}>
            <div style={{
              width: "40px", height: "40px",
              border: `3px solid rgba(255,255,255,0.2)`,
              borderTopColor: C.white,
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }} />
          </div>
        )}

        {/* Hero Text */}
        <div style={{
          position: "absolute", inset: 0, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center", textAlign: "center",
          opacity: textOpacity, padding: "0 24px",
          pointerEvents: progress > 0.2 ? "none" : "auto",
          transition: "opacity 0.1s linear",
        }}>
          <p style={{
            color: C.white, fontSize: "10px",
            letterSpacing: "0.4em", textTransform: "uppercase", marginBottom: "20px",
            opacity: 0.8,
          }}>
            Find your perfect stay
          </p>

          <h1 style={{
            fontFamily: "'Cormorant Garamond', serif",
            fontSize: "clamp(2.5rem, 8vw, 6rem)",
            color: C.white, lineHeight: 1.05, textTransform: "uppercase",
            fontWeight: 300,
            letterSpacing: "0.02em",
          }}>
            Home Away<br />From Home
          </h1>

          <div style={{
            display: "flex", gap: "16px", marginTop: "40px",
            flexWrap: "wrap", justifyContent: "center", width: "100%",
          }}>
            <button className="se5-btn" style={{ background: C.ctaGreen, color: C.ctaText }}>
              Start exploring
            </button>
            <button className="se5-btn" style={{
              background: "transparent", color: C.white,
              border: "1px solid rgba(255,255,255,0.4)",
            }}>
              Watch demo
            </button>
          </div>
        </div>

        {/* Search Section */}
        {(() => {
          const searchOpacity = progress < 0.85
            ? 0
            : Math.min(1, (progress - 0.85) / 0.15);

          return (
            <div style={{
              position: "absolute", inset: 0,
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              opacity: searchOpacity,
              pointerEvents: progress >= 0.85 ? "auto" : "none",
              padding: "0 24px",
              transition: "opacity 0.3s linear",
            }}>
              <h2 style={{
                fontFamily: "'Cormorant Garamond', serif",
                fontSize: "clamp(2rem, 6vw, 4.5rem)",
                color: C.white, lineHeight: 1.1,
                marginBottom: "48px", textAlign: "center",
                fontWeight: 300,
              }}>
                Your{" "}
                <em style={{ color: C.accentGreen, fontStyle: "italic", fontWeight: 400 }}>home away</em>
                {" "}from home
              </h2>

              <FloatingSearchBar 
                onLight={false} 
                onSearchResults={handleSearchResults}
              />
            </div>
          );
        })()}
      </div>
    </div>
  );
}

// ─── Floating Search Bar ───
function FloatingSearchBar({ onLight = false, onSearchResults }) {
  const [query,      setQuery]      = useState("");
  const [status,     setStatus]     = useState({ msg: "", error: false });
  const [loading,    setLoading]    = useState(false);
  const [locLoading, setLocLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const [showRecent, setShowRecent] = useState(false);
  const busy = loading || locLoading;
  const inputRef = useRef(null);

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved).slice(0, 5));
      } catch (e) { /* ignore */ }
    }
  }, []);

  const saveRecentSearch = (location) => {
    const updated = [location, ...recentSearches.filter(s => s !== location)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));
  };

  const performSearch = async (lat, lon, displayName) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/client/search/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude: lat, longitude: lon }),
      });
      if (!res.ok) throw new Error("backend");
      const data = await res.json();
      saveRecentSearch(displayName);
      if (onSearchResults) {
        onSearchResults(data, displayName);
      }
      setStatus({ msg: `Found ${data.length} hostels near ${displayName}`, error: false });
    } catch {
      setStatus({ msg: "Server error. Please try again.", error: true });
    }
    setLoading(false);
    setLocLoading(false);
  };

  const handleSearch = async () => {
    const place = query.trim();
    if (!place) { 
      setStatus({ msg: "Enter a city or area to search.", error: false }); 
      return; 
    }

    setLoading(true);
    setStatus({ msg: "Looking up location…", error: false });

    try {
      const geoRes  = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(place)}`,
        { headers: { "Accept-Language": "en" } }
      );
      const geoData = await geoRes.json();

      if (!geoData?.length) {
        setStatus({ msg: "Location not found. Try a different name.", error: true });
        setLoading(false);
        return;
      }

      const lat         = parseFloat(geoData[0].lat);
      const lon         = parseFloat(geoData[0].lon);
      const displayName = geoData[0].display_name.split(",").slice(0, 2).join(", ");

      setStatus({ msg: `Searching near ${displayName}…`, error: false });
      await performSearch(lat, lon, displayName);
    } catch {
      setStatus({ msg: "Something went wrong. Try again.", error: true });
      setLoading(false);
    }
  };

  const handleCurrentLocation = () => {
    if (!navigator.geolocation) {
      setStatus({ msg: "Geolocation not supported by your browser.", error: true });
      return;
    }
    setLocLoading(true);
    setStatus({ msg: "Detecting your location…", error: false });

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        let displayName = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
        try {
          const rev  = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`,
            { headers: { "Accept-Language": "en" } }
          );
          const revD = await rev.json();
          if (revD?.address) {
            const a = revD.address;
            displayName = [a.city || a.town || a.village || a.county, a.state]
              .filter(Boolean).slice(0, 2).join(", ");
          }
        } catch { /* use fallback */ }

        setQuery(displayName);
        setStatus({ msg: `Found: ${displayName}. Searching…`, error: false });
        await performSearch(lat, lon, displayName);
      },
      (err) => {
        setLocLoading(false);
        const msgs = {
          1: "Location permission denied. Allow it in browser settings.",
          2: "Could not detect location. Search manually.",
          3: "Location request timed out. Try again.",
        };
        setStatus({ msg: msgs[err.code] || "Could not get location.", error: true });
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const statusClass = [
    "se5-float-status",
    onLight ? "on-light" : "",
    status.error ? "error" : "",
    !status.error && status.msg.includes("Found") ? "success" : "",
  ].join(" ").trim();

  return (
    <div style={{ 
      display: "flex", 
      flexDirection: "column", 
      alignItems: "center", 
      width: "100%", 
      maxWidth: "720px",
      position: "relative",
    }}>
      <div className="se5-float-search">
        <div className="se5-float-search-inner">
          <span className="se5-float-label">Location</span>
          <input
            ref={inputRef}
            className="se5-float-input"
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onFocus={() => setShowRecent(true)}
            onBlur={() => setTimeout(() => setShowRecent(false), 200)}
            onKeyDown={e => e.key === "Enter" && !busy && handleSearch()}
            placeholder="Search and find"
            disabled={busy}
          />
        </div>

        <div className="se5-float-actions">
          <button
            className={`se5-near-btn${locLoading ? " locating" : ""}`}
            onClick={handleCurrentLocation}
            disabled={busy}
            title="Use my current location"
          >
            <LocSVG pulsing={locLoading} color={locLoading ? C.ctaGreen : C.inkMid} />
            {locLoading ? "Locating…" : "Near me"}
          </button>

          <button
            className="se5-round-search-btn"
            onClick={handleSearch}
            disabled={busy}
            title="Search"
          >
            {loading
              ? <svg width="20" height="20" viewBox="0 0 18 18" fill="none">
                  <circle cx="9" cy="9" r="7" stroke="rgba(245,244,236,0.4)" strokeWidth="2" />
                  <path d="M9 2a7 7 0 0 1 7 7" stroke={C.ctaText} strokeWidth="2" strokeLinecap="round">
                    <animateTransform attributeName="transform" type="rotate" from="0 9 9" to="360 9 9" dur="0.8s" repeatCount="indefinite" />
                  </path>
                </svg>
              : <SearchSVG color={C.ctaText} />
            }
          </button>
        </div>
      </div>

      {/* Recent searches dropdown */}
      {showRecent && recentSearches.length > 0 && !query && (
        <div style={{
          position: "absolute",
          top: "100%",
          left: 0,
          right: 0,
          marginTop: "8px",
          background: C.white,
          borderRadius: "16px",
          boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
          padding: "8px",
          zIndex: 50,
        }}>
          <p style={{
            fontSize: "10px",
            textTransform: "uppercase",
            letterSpacing: "0.15em",
            color: C.inkLight,
            padding: "8px 12px",
            fontWeight: 600,
          }}>
            Recent
          </p>
          {recentSearches.map((search, i) => (
            <button
              key={i}
              onClick={() => {
                setQuery(search);
                inputRef.current?.focus();
              }}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                width: "100%",
                padding: "10px 12px",
                border: "none",
                background: "transparent",
                cursor: "pointer",
                borderRadius: "8px",
                fontSize: "14px",
                color: C.inkPrimary,
                transition: "background 0.2s",
                textAlign: "left",
              }}
              onMouseEnter={e => e.currentTarget.style.background = C.background}
              onMouseLeave={e => e.currentTarget.style.background = "transparent"}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={C.inkLight} strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              {search}
            </button>
          ))}
        </div>
      )}

      {status.msg && <p className={statusClass}>{status.msg}</p>}
    </div>
  );
}

// ─── Skeleton Card ───
function SkeletonCard() {
  return (
    <div style={{
      border: `1px solid ${C.borderLight}`,
      background: C.white,
      borderRadius: "12px",
      overflow: "hidden",
    }}>
      <div className="skeleton" style={{ height: "240px" }} />
      <div style={{ padding: "24px" }}>
        <div className="skeleton" style={{ height: "24px", width: "70%", marginBottom: "12px" }} />
        <div className="skeleton" style={{ height: "14px", width: "50%", marginBottom: "8px" }} />
        <div className="skeleton" style={{ height: "14px", width: "90%" }} />
      </div>
    </div>
  );
}

// ─── Hostel Card Component ───
function HostelCard({ hostel, index, onClick }) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  return (
    <div 
      className="hostel-card reveal"
      style={{ animationDelay: `${index * 0.1}s` }}
      onClick={onClick}
    >
      <div className="hostel-image-wrapper">
        {hostel.image_url && !imageError ? (
          <>
            {!imageLoaded && (
              <div style={{
                position: "absolute", inset: 0,
                background: C.backgroundAlt,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <div className="skeleton" style={{ width: "60%", height: "20px" }} />
              </div>
            )}
            <img
              src={hostel.image_url}
              alt={hostel.name}
              onLoad={() => setImageLoaded(true)}
              onError={() => setImageError(true)}
              style={{ opacity: imageLoaded ? 1 : 0, transition: "opacity 0.4s" }}
            />
          </>
        ) : (
          <div className="hostel-image-placeholder">
            <div style={{ textAlign: "center" }}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke={C.inkLight} strokeWidth="1" style={{ marginBottom: "8px", opacity: 0.5 }}>
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9 22 9 12 15 12 15 22" />
              </svg>
              <p style={{ fontSize: "13px", color: C.inkLight }}>
                {hostel.city}, {hostel.state}
              </p>
            </div>
          </div>
        )}

        {/* Badges */}
        {hostel.rooms_available > 0 ? (
          <span className="hostel-badge available">
            {hostel.rooms_available} {hostel.rooms_available === 1 ? 'room' : 'rooms'}
          </span>
        ) : (
          <span className="hostel-badge unavailable">Full</span>
        )}
        {hostel.featured && (
          <span className="hostel-badge featured" style={{ left: "auto", right: "16px" }}>
            Featured
          </span>
        )}
      </div>

      <div style={{ padding: "24px" }}>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "8px",
        }}>
          <h3 style={{ 
            fontFamily: "'Cormorant Garamond', serif", 
            fontSize: "22px",
            fontWeight: 600,
            color: C.inkPrimary,
            lineHeight: 1.2,
          }}>
            {hostel.name}
          </h3>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "4px",
            background: "rgba(255, 184, 0, 0.1)",
            padding: "4px 8px",
            borderRadius: "6px",
          }}>
            <StarSVG size={12} />
            <span style={{
              fontSize: "12px",
              fontWeight: 600,
              color: "#FFB800",
            }}>
              {hostel.rating || "4.5"}
            </span>
          </div>
        </div>

        <p style={{ 
          color: C.inkLight, 
          fontSize: "13px", 
          margin: "0 0 12px",
          display: "flex",
          alignItems: "center",
          gap: "6px",
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={C.inkLight} strokeWidth="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
            <circle cx="12" cy="10" r="3" />
          </svg>
          {hostel.city}, {hostel.state}
        </p>

        {hostel.description && (
          <p style={{ 
            fontSize: "13px", 
            color: C.inkMid,
            lineHeight: 1.5,
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}>
            {hostel.description}
          </p>
        )}

        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "16px",
          paddingTop: "16px",
          borderTop: `1px solid ${C.borderLight}`,
        }}>
          <div>
            <span style={{
              fontFamily: "'Cormorant Garamond', serif",
              fontSize: "24px",
              fontWeight: 700,
              color: C.inkPrimary,
            }}>
              ₹{hostel.price_per_night || "N/A"}
            </span>
            <span style={{
              fontSize: "12px",
              color: C.inkLight,
              marginLeft: "4px",
            }}>
              / night
            </span>
          </div>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "4px",
            color: C.ctaGreen,
            fontSize: "12px",
            fontWeight: 600,
          }}>
            View details
            <ArrowRightSVG size={14} color={C.ctaGreen} />
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Home Component ───
function Home() {
  const [showLogin, setShowLogin]       = useState(false);
  const [heroProgress, setHeroProgress] = useState(0);
  const [displayedHostels, setDisplayedHostels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchActive, setSearchActive] = useState(false);
  const [currentLocation, setCurrentLocation] = useState("");
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => { injectStyles(); }, []);
  useScrollReveal();

  // Fetch initial featured hostels
  useEffect(() => {
    const fetchInitialHostels = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/hostels/");
        if (response.ok) {
          const data = await response.json();
          setDisplayedHostels(data.slice(0, 6));
        }
      } catch (error) {
        console.error("Error fetching hostels:", error);
        setDisplayedHostels([]);
      } finally {
        setLoading(false);
      }
    };
    fetchInitialHostels();
  }, []);

  const heroFinished = heroProgress >= 0.98;
  const navHidden    = heroProgress > 0.02 && !heroFinished;

  const handleLogout = () => { 
    logout(); 
    navigate("/"); 
  };

  useEffect(() => {
    if (user && showLogin) setShowLogin(false);
  }, [user]);

  const handleHostelClick = (hostel) => {
    navigate(`/hostel/${hostel.id}`, { state: { hostel } });
  };

  const handleSearchResults = (results, location) => {
    setDisplayedHostels(results);
    setSearchActive(true);
    setCurrentLocation(location);
  };

  const clearSearch = async () => {
    setSearchActive(false);
    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/hostels/");
      if (response.ok) {
        const data = await response.json();
        setDisplayedHostels(data.slice(0, 6));
      }
    } catch (error) {
      console.error("Error fetching hostels:", error);
      setDisplayedHostels([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="se5-root">
      {/* Navigation */}
      <header className={`se5-nav ${navHidden ? "hidden" : ""} ${heroFinished ? "light-nav" : ""}`}>
        <div className="se5-nav-inner se5-max" style={{ 
          display: "flex", 
          justifyContent: "space-between", 
          width: "100%",
          alignItems: "center",
        }}>
          <a href="#" className="se5-logo" style={{ color: heroFinished ? C.inkPrimary : C.white }}>
            <div style={{ 
              width: 8, 
              height: 8, 
              borderRadius: "50%", 
              background: C.ctaGreen,
              boxShadow: `0 0 0 3px ${heroFinished ? C.background : 'rgba(255,255,255,0.2)}`,
            }} />
            StayEasy
          </a>

          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            <nav className="se5-navlinks">
              {["Explore", "Hostels", "Support"].map(l => (
                <a key={l} href="#" style={{
                  color: heroFinished ? C.inkPrimary : C.white,
                  textDecoration: "none", fontSize: "11px",
                  letterSpacing: "0.12em", textTransform: "uppercase",
                  fontWeight: 500,
                  transition: "opacity 0.3s",
                }}>{l}</a>
              ))}
            </nav>

            <button
              onClick={() => navigate("/dashboard")}
              style={{
                padding: "10px 20px", 
                background: "transparent",
                color: heroFinished ? C.inkPrimary : C.white,
                border: `1px solid ${heroFinished ? C.border : "rgba(255,255,255,0.4)"}`,
                borderRadius: "4px", 
                fontSize: "10px", 
                fontWeight: 600, 
                cursor: "pointer",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                transition: "all 0.3s",
              }}
              onMouseEnter={e => {
                e.target.style.background = heroFinished ? C.ctaGreen : "rgba(255,255,255,0.1)";
                e.target.style.color = C.ctaText;
                e.target.style.borderColor = C.ctaGreen;
              }}
              onMouseLeave={e => {
                e.target.style.background = "transparent";
                e.target.style.color = heroFinished ? C.inkPrimary : C.white;
                e.target.style.borderColor = heroFinished ? C.border : "rgba(255,255,255,0.4)";
              }}
            >
              ADD HOSTEL
            </button>

            {user ? (
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <span style={{
                  fontSize: "12px",
                  color: heroFinished ? C.inkMid : "rgba(255,255,255,0.7)",
                  fontWeight: 500,
                }}>
                  {user.username}
                </span>
                <button 
                  onClick={handleLogout} 
                  style={{
                    padding: "10px 20px", 
                    background: "transparent",
                    color: heroFinished ? C.error : "rgba(255,255,255,0.8)",
                    border: `1px solid ${heroFinished ? C.error : "rgba(255,255,255,0.3)"}`,
                    borderRadius: "4px",
                    fontSize: "10px", 
                    fontWeight: 600, 
                    cursor: "pointer",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    transition: "all 0.3s",
                  }}
                  onMouseEnter={e => {
                    e.target.style.background = C.error;
                    e.target.style.color = C.white;
                  }}
                  onMouseLeave={e => {
                    e.target.style.background = "transparent";
                    e.target.style.color = heroFinished ? C.error : "rgba(255,255,255,0.8)";
                  }}
                >
                  LOGOUT
                </button>
              </div>
            ) : (
              <button 
                onClick={() => setShowLogin(true)} 
                style={{
                  padding: "10px 24px", 
                  background: C.ctaGreen, 
                  color: C.ctaText,
                  border: "none", 
                  borderRadius: "4px",
                  fontSize: "10px", 
                  fontWeight: 600, 
                  cursor: "pointer",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  transition: "all 0.3s",
                  boxShadow: "0 4px 12px rgba(30, 59, 27, 0.3)",
                }}
                onMouseEnter={e => {
                  e.target.style.background = C.ctaGreenHover;
                  e.target.style.transform = "translateY(-2px)";
                  e.target.style.boxShadow = "0 6px 20px rgba(30, 59, 27, 0.4)";
                }}
                onMouseLeave={e => {
                  e.target.style.background = C.ctaGreen;
                  e.target.style.transform = "translateY(0)";
                  e.target.style.boxShadow = "0 4px 12px rgba(30, 59, 27, 0.3)";
                }}
              >
                LOGIN
              </button>
            )}
          </div>
        </div>
      </header>

      <main>
        <CanvasHero 
          onScrollProgress={setHeroProgress}
          onSearchResults={handleSearchResults}
        />

        {/* Featured Hostels Section */}
        <div style={{ background: C.background, paddingTop: "80px" }}>
          <div className="se5-max">
            <section className="se5-section" style={{ paddingTop: 0 }}>
              <div className="section-header reveal">
                <div>
                  <h2 style={{
                    fontFamily: "'Cormorant Garamond', serif",
                    fontSize: "clamp(2rem, 4vw, 3rem)",
                    margin: 0,
                    fontWeight: 600,
                    lineHeight: 1.2,
                  }}>
                    {searchActive ? `Hostels near ${currentLocation}` : "Featured Hostels"}
                  </h2>
                  <p style={{
                    color: C.inkLight,
                    fontSize: "14px",
                    marginTop: "8px",
                  }}>
                    {searchActive 
                      ? `${displayedHostels.length} results found` 
                      : "Handpicked stays for your next adventure"
                    }
                  </p>
                </div>
                {searchActive && (
                  <button onClick={clearSearch} className="clear-search-btn">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="19" y1="12" x2="5" y2="12" />
                      <polyline points="12 19 5 12 12 5" />
                    </svg>
                    Show Featured
                  </button>
                )}
              </div>

              {loading ? (
                <div className="se5-grid">
                  {[1, 2, 3, 4, 5, 6].map(i => <SkeletonCard key={i} />)}
                </div>
              ) : displayedHostels.length === 0 ? (
                <div style={{ 
                  textAlign: "center", 
                  padding: "80px 0",
                  background: C.white,
                  borderRadius: "16px",
                  border: `1px solid ${C.borderLight}`,
                }}>
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke={C.inkLight} strokeWidth="1" style={{ marginBottom: "16px", opacity: 0.5 }}>
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                  <p style={{ 
                    color: C.inkLight, 
                    fontSize: "16px",
                    marginBottom: "8px",
                  }}>
                    No hostels found
                  </p>
                  <p style={{ 
                    color: C.inkMuted, 
                    fontSize: "14px",
                  }}>
                    Try searching for another location or browse our featured stays
                  </p>
                </div>
              ) : (
                <div className="se5-grid">
                  {displayedHostels.map((hostel, index) => (
                    <HostelCard
                      key={hostel.id}
                      hostel={hostel}
                      index={index}
                      onClick={() => handleHostelClick(hostel)}
                    />
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>

        {/* Stats Section */}
        <section style={{ 
          background: C.inkPrimary, 
          color: C.white, 
          padding: "80px 0",
          position: "relative",
          overflow: "hidden",
        }}>
          {/* Decorative background pattern */}
          <div style={{
            position: "absolute",
            inset: 0,
            opacity: 0.03,
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />

          <div className="se5-max se5-stats-strip" style={{ position: "relative", zIndex: 1 }}>
            {[
              { n: "12K+", l: "Hostels", d: "Across 50+ countries" },
              { n: "4.8★", l: "Rating", d: "From 50K+ reviews" },
              { n: "99.9%", l: "Uptime", d: "Reliable booking" },
            ].map((s, i) => (
              <div key={s.n} style={{ padding: "40px", textAlign: "center" }}>
                <div style={{ 
                  fontFamily: "'Cormorant Garamond', serif", 
                  fontSize: "3.5rem",
                  fontWeight: 300,
                  lineHeight: 1,
                  marginBottom: "8px",
                }}>
                  {s.n}
                </div>
                <div style={{ 
                  fontSize: "12px", 
                  opacity: 0.9, 
                  textTransform: "uppercase", 
                  letterSpacing: "0.15em",
                  fontWeight: 600,
                  marginBottom: "4px",
                }}>
                  {s.l}
                </div>
                <div style={{
                  fontSize: "13px",
                  opacity: 0.5,
                }}>
                  {s.d}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer style={{
          background: C.inkPrimary,
          borderTop: `1px solid rgba(255,255,255,0.1)`,
          padding: "40px 0",
        }}>
          <div className="se5-max" style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "24px",
          }}>
            <div style={{
              fontFamily: "'Cormorant Garamond', serif",
              fontSize: "18px",
              color: C.white,
              letterSpacing: "0.15em",
              textTransform: "uppercase",
            }}>
              StayEasy
            </div>
            <div style={{
              display: "flex",
              gap: "32px",
            }}>
              {["Privacy", "Terms", "Contact"].map(item => (
                <a key={item} href="#" style={{
                  color: "rgba(255,255,255,0.5)",
                  textDecoration: "none",
                  fontSize: "12px",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  transition: "color 0.3s",
                }}
                onMouseEnter={e => e.target.style.color = C.white}
                onMouseLeave={e => e.target.style.color = "rgba(255,255,255,0.5)"}
                >
                  {item}
                </a>
              ))}
            </div>
            <div style={{
              fontSize: "12px",
              color: "rgba(255,255,255,0.3)",
            }}>
              © 2024 StayEasy. All rights reserved.
            </div>
          </div>
        </footer>
      </main>

      {showLogin && <Login onClose={() => setShowLogin(false)} />}
    </div>
  );
}

export default Home;
