/**
 * TrendCard.jsx
 *
 * Shared, purely presentational card component used by both GlobalTrends and
 * IndiaTrends pages. It receives one trend item and its rank index as props
 * and renders a styled card with a score bar. Contains NO API logic.
 *
 * Props:
 *   trend  – { query: string, trend_score: number }
 *   index  – 0-based position in the list (for rank badge + animation delay)
 */

import React from "react";

/**
 * scoreConfig – maps a numeric trend score to Tailwind colour classes.
 * @param {number} s  Trend score 0-100
 * @returns {{ text: string, bg: string }}
 */
function scoreConfig(s) {
  if (s >= 70) return { text: "text-emerald-400", bg: "bg-emerald-400/10 border-emerald-400/30" };
  if (s >= 40) return { text: "text-yellow-400",  bg: "bg-yellow-400/10  border-yellow-400/30"  };
  return             { text: "text-slate-400",   bg: "bg-slate-500/10   border-slate-500/20"   };
}

export default function TrendCard({ trend, index }) {
  const pct = Math.min(trend.trend_score, 100);
  const sc  = scoreConfig(trend.trend_score);

  return (
    <div
      className="group relative rounded-2xl border border-slate-200 dark:border-slate-700/80
        bg-white dark:bg-slate-800/60 p-5 flex flex-col gap-3
        transition-all duration-200 cursor-default overflow-hidden
        hover:-translate-y-1 hover:border-orange-400/40 hover:shadow-glow-sm
        animate-fade-up"
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      {/* Orange accent line revealed on hover */}
      <div className="absolute top-0 left-0 right-0 h-0.5 btn-accent
        opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

      {/* Header row: rank | query | score badge */}
      <div className="flex items-start justify-between gap-3">
        <span className="text-[11px] font-mono font-semibold text-slate-400 dark:text-slate-500
          bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600
          px-2 py-0.5 rounded-md flex-shrink-0">
          #{index + 1}
        </span>

        <p className="flex-1 text-sm font-semibold text-slate-800 dark:text-slate-100 leading-snug">
          {trend.query}
        </p>

        <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border
          flex-shrink-0 ${sc.bg} ${sc.text}`}>
          {trend.trend_score}
        </span>
      </div>

      {/* Progress bar */}
      <div className="flex items-center gap-2.5">
        <div className="flex-1 h-1.5 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
          <div
            className="h-full rounded-full btn-accent transition-all duration-700"
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="text-[11px] font-mono font-semibold text-slate-400
          dark:text-slate-500 min-w-[28px] text-right">
          {pct}
        </span>
      </div>
    </div>
  );
}
