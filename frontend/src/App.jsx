import React, { useState, useEffect } from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";

import Search from "./pages/Search";
import GlobalTrends from "./pages/GlobalTrends";
import IndiaTrends from "./pages/IndiaTrends";
import "./index.css";

/* ── Inline SVG Icons ──────────────────────────────────────────── */
const IconSearch = () => (
 <svg width="16" height="16" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
 </svg>
);
const IconGlobe = () => (
 <svg width="16" height="16" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="12" cy="12" r="10" />
  <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
 </svg>
);
const IconMap = () => (
 <svg width="16" height="16" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
  <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
  <line x1="9" y1="3" x2="9" y2="18" /><line x1="15" y1="6" x2="15" y2="21" />
 </svg>
);
const IconSun = () => (
 <svg width="16" height="16" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
  <circle cx="12" cy="12" r="5" />
  <line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" />
  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
  <line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" />
  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
 </svg>
);
const IconMoon = () => (
 <svg width="16" height="16" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
 </svg>
);

/* ── Navbar ─────────────────────────────────────────────────────── */
function Navbar({ isDark, toggleTheme }) {
 const location = useLocation();
 const isActive = (path) =>
  path === "/" ? location.pathname === "/" : location.pathname === path;

 const linkBase =
  "flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-medium transition-all duration-200 border border-transparent";
 const linkIdle =
  "text-slate-400 hover:text-slate-100 hover:bg-slate-800 dark:hover:bg-slate-800 hover:border-slate-700";
 const linkActiveDark =
  "text-orange-400 bg-orange-500/10 border-orange-500/30";
 const linkActiveLight =
  "text-orange-600 bg-orange-50 border-orange-200";

 const getLink = (path) =>
  `${linkBase} ${isActive(path)
   ? isDark ? linkActiveDark : linkActiveLight
   : linkIdle + (isDark ? "" : " dark:hover:bg-transparent hover:bg-slate-100 hover:text-slate-800 hover:border-slate-200")}`;

 return (
  <header className="sticky top-0 z-50 border-b backdrop-blur-xl bg-white/80 dark:bg-slate-950/85 border-slate-200 dark:border-slate-800 transition-colors duration-300">
   <div className="max-w-6xl mx-auto px-5 h-14 flex items-center gap-3">
    {/* Brand */}
    <Link to="/" className="flex items-center gap-2.5 mr-5 flex-shrink-0 group no-underline">
     <div className="w-8 h-8 rounded-lg flex items-center justify-center text-base shadow-glow-sm animate-float"
      style={{ background: "linear-gradient(135deg, #ff4500, #ff6b35)" }}>
      📡
     </div>
     <span className="text-[17px] font-bold tracking-tight text-slate-900 dark:text-slate-100">
      Trend<span className="text-orange-500">Intel</span>
     </span>
    </Link>

    {/* Navigation links */}
    <nav className="flex items-center gap-1 flex-1">
     <Link to="/" id="nav-search" className={getLink("/")}>
      <IconSearch /><span className="hidden sm:inline">Search</span>
     </Link>
     <Link to="/trends" id="nav-global" className={getLink("/trends")}>
      <IconGlobe /><span className="hidden sm:inline">Global</span>
     </Link>
     <Link to="/region" id="nav-india" className={getLink("/region")}>
      <IconMap /><span className="hidden sm:inline">India</span>
     </Link>
    </nav>

    {/* Right side */}
    <div className="flex items-center gap-2 ml-auto">
     {/* Live badge */}
     <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium
            bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700
            text-slate-500 dark:text-slate-400">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-dot" />
      Live
     </div>

     {/* Theme toggle */}
     <button
      id="theme-toggle"
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className="w-9 h-9 flex items-center justify-center rounded-xl border transition-all duration-200
              bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700
              text-slate-500 dark:text-slate-400 hover:text-orange-500 hover:border-orange-300
              dark:hover:text-orange-400 dark:hover:border-orange-500/40"
     >
      {isDark ? <IconSun /> : <IconMoon />}
     </button>
    </div>
   </div>
  </header>
 );
}

/* ── App Shell ──────────────────────────────────────────────────── */
function App() {
 const [isDark, setIsDark] = useState(() => {
  const stored = localStorage.getItem("theme");
  if (stored) return stored === "dark";
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
 });

 useEffect(() => {
  const root = document.documentElement;
  if (isDark) {
   root.classList.add("dark");
   localStorage.setItem("theme", "dark");
  } else {
   root.classList.remove("dark");
   localStorage.setItem("theme", "light");
  }
 }, [isDark]);

 const toggleTheme = () => setIsDark((prev) => !prev);

 return (
  <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-[#0d1117] transition-colors duration-300">
   <Navbar isDark={isDark} toggleTheme={toggleTheme} />
   <main className="flex-1 max-w-6xl w-full mx-auto px-5 py-8 pb-16">
    <Routes>
     <Route path="/" element={<Search />} />
     <Route path="/trends" element={<GlobalTrends />} />
     <Route path="/region" element={<IndiaTrends />} />
    </Routes>
   </main>
   <footer className="border-t border-slate-200 dark:border-slate-800 py-5 text-center text-sm text-slate-400 dark:text-slate-500 transition-colors duration-300">
    TrendIntel © 2026 — Powered by{" "}
    <span className="text-orange-500 font-medium">Reddit Trends</span>{" "}
    · Built by Team Tripod
   </footer>
  </div>
 );
}

export default App;