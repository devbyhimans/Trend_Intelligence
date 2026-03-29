/**
 * StateDropdown.jsx
 *
 * Presentational dropdown that lists all Indian states and Union Territories.
 * It does NOT make any API calls — it simply lets the user pick a value and
 * reports the selection upward via the onChange prop.
 *
 * Props:
 *   value    – string  – currently selected state (controlled by parent)
 *   onChange – fn      – called when selection changes: (stateName: string) => void
 */

import React from "react";

/* ── Static data ─────────────────────────────────────────────── */
const STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
];

const UNION_TERRITORIES = [
  "Andaman and Nicobar Islands", "Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
];

const STATE_FLAGS = {
  Maharashtra: "🏙️", Delhi: "🗺️", Karnataka: "🌿", "Tamil Nadu": "🌊",
  "Uttar Pradesh": "🕌", "West Bengal": "🐯", Gujarat: "💎", Rajasthan: "🏜️",
  Kerala: "🌴", Punjab: "🌾", Bihar: "🏛️", "Andhra Pradesh": "🌋",
  Telangana: "💧", "Madhya Pradesh": "🦁", Goa: "🏖️", Assam: "🍵",
};

/** Returns an emoji for the given state, defaulting to 📍 */
export const getFlag = (s) => STATE_FLAGS[s] ?? "📍";

/* ── Component ───────────────────────────────────────────────── */
export default function StateDropdown({ value, onChange }) {
  return (
    <div className="flex-1 relative">
      <select
        id="state-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full appearance-none rounded-xl border border-slate-200 dark:border-slate-700
          bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100
          text-sm font-medium px-4 py-2.5 pr-10 outline-none
          focus:border-orange-400 dark:focus:border-orange-500
          transition-colors duration-200 cursor-pointer"
      >
        <option value="India">🇮🇳 India (All)</option>

        <optgroup label="── States ──">
          {STATES.map((s) => (
            <option key={s} value={s}>
              {getFlag(s)} {s}
            </option>
          ))}
        </optgroup>

        <optgroup label="── Union Territories ──">
          {UNION_TERRITORIES.map((ut) => (
            <option key={ut} value={ut}>
              {getFlag(ut)} {ut}
            </option>
          ))}
        </optgroup>
      </select>

      {/* Custom chevron arrow (replaces native arrow via appearance-none) */}
      <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
        <svg width="16" height="16" className="w-4 h-4" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" strokeWidth="2">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </div>
    </div>
  );
}
