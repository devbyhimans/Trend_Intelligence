/**
 * Graph.jsx
 *
 * Pure visualization component — receives an array of trend data and renders
 * it as an SVG horizontal bar chart. Contains NO API calls and NO state.
 * The parent page is responsible for fetching data and passing it in.
 *
 * Props:
 *   data  – Array<{ query: string, trend_score: number }>
 *   title – string  – optional chart heading (default: "Trend Chart")
 *   limit – number  – max items to show (default: 10)
 */

import React from "react";

/** Maps score → bar colour class */
function barColor(score) {
  if (score >= 70) return "#34d399"; // emerald-400
  if (score >= 40) return "#fbbf24"; // yellow-400
  return "#94a3b8";                  // slate-400
}

export default function Graph({ data = [], title = "Trend Chart", limit = 10 }) {
  if (!data || data.length === 0) return null;

  const items = data.slice(0, limit);
  const maxScore = Math.max(...items.map((d) => d.trend_score), 1);

  /* SVG layout constants */
  const ROW_H    = 40;   // height per bar row
  const LABEL_W  = 140;  // left column width for query labels
  const BAR_AREA = 220;  // width of the bar + score area
  const PAD      = 16;   // top/bottom padding
  const SVG_W    = LABEL_W + BAR_AREA + 8;
  const SVG_H    = items.length * ROW_H + PAD * 2;

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-700
      bg-white dark:bg-slate-800/60 p-5 animate-fade-up">

      {/* Title */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 rounded-lg bg-orange-500/15 border border-orange-500/30
          flex items-center justify-center text-sm">
          📊
        </div>
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">{title}</h3>
        <span className="ml-auto text-xs text-slate-400 dark:text-slate-500 font-medium">
          Top {items.length}
        </span>
      </div>

      {/* SVG Chart */}
      <svg
        width="100%"
        viewBox={`0 0 ${SVG_W} ${SVG_H}`}
        aria-label={title}
        role="img"
        className="overflow-visible"
      >
        {items.map((item, i) => {
          const y        = PAD + i * ROW_H;
          const barW     = Math.max((item.trend_score / maxScore) * (BAR_AREA - 48), 4);
          const color    = barColor(item.trend_score);
          const labelY   = y + ROW_H / 2;

          return (
            <g key={item.query} aria-label={`${item.query}: ${item.trend_score}`}>
              {/* Query label */}
              <text
                x={LABEL_W - 8}
                y={labelY + 4}
                textAnchor="end"
                fontSize="11"
                fill="currentColor"
                className="fill-slate-500 dark:fill-slate-400"
                style={{ fontFamily: "Inter, sans-serif" }}
              >
                {item.query.length > 18
                  ? item.query.slice(0, 17) + "…"
                  : item.query}
              </text>

              {/* Bar background track */}
              <rect
                x={LABEL_W}
                y={y + 12}
                width={BAR_AREA - 48}
                height={16}
                rx={8}
                className="fill-slate-100 dark:fill-slate-700"
              />

              {/* Filled bar */}
              <rect
                x={LABEL_W}
                y={y + 12}
                width={barW}
                height={16}
                rx={8}
                fill={color}
                opacity={0.85}
              />

              {/* Score number */}
              <text
                x={LABEL_W + (BAR_AREA - 44)}
                y={labelY + 4}
                textAnchor="start"
                fontSize="11"
                fontWeight="600"
                fill={color}
                style={{ fontFamily: "IBM Plex Mono, monospace" }}
              >
                {item.trend_score}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 pt-3 border-t
        border-slate-100 dark:border-slate-700">
        {[
          { color: "#34d399", label: "70–100  High" },
          { color: "#fbbf24", label: "40–69   Mid"  },
          { color: "#94a3b8", label: "0–39    Low"  },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: color }} />
            <span className="text-[11px] font-mono text-slate-400">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
