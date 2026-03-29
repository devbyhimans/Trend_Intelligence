# 📘 TrendIntel Frontend — Complete Technical Documentation

> **Project:** Trend Intelligence System  
> **Frontend Path:** `trend-intelligence-system/frontend/`  
> **Framework:** React 18 + Vite 5  
> **Styling:** Tailwind CSS v3 (dark/light mode)  
> **Routing:** React Router DOM v7  
> **Last Updated:** March 2026

---

## 🏗️ Architecture Overview

The frontend follows a clear three-layer separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│  PAGES  — own state, call services, compose components      │
│  Search.jsx  │  GlobalTrends.jsx  │  IndiaTrends.jsx        │
├─────────────────────────────────────────────────────────────┤
│  COMPONENTS  — purely presentational, zero API calls        │
│  TrendCard  │  SearchBar  │  StateDropdown  │  Graph        │
├─────────────────────────────────────────────────────────────┤
│  SERVICES  — all backend HTTP communication                 │
│  services/api.js                                            │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Responsibility |
|---|---|
| **Pages** | Manage state, orchestrate API calls, compose components into screens |
| **Components** | Render UI only — receive props, emit callbacks, make zero API calls |
| **Services** | Central bridge between frontend and FastAPI backend — all `fetch()` calls live here |

---

## 📁 Project Directory Structure

```
frontend/
├── public/
│   └── hero_banner.png              # Hero section background image
├── src/
│   ├── main.jsx                     # App entry point — mounts React tree
│   ├── index.css                    # Tailwind directives + custom utilities
│   ├── App.jsx                      # Root: Navbar + routing + theme toggle
│   ├── pages/
│   │   ├── Search.jsx               # "/" — search a trend by keyword
│   │   ├── GlobalTrends.jsx         # "/trends" — all global trends
│   │   └── IndiaTrends.jsx          # "/region" — state/UT-wise trends
│   ├── components/
│   │   ├── TrendCard.jsx            # Shared trend result card (stateless)
│   │   ├── SearchBar.jsx            # Input + button UI (fully controlled)
│   │   ├── StateDropdown.jsx        # India state/UT picker (stateless)
│   │   └── Graph.jsx                # SVG bar chart visualization (stateless)
│   ├── services/
│   │   └── api.js                   # All HTTP calls to the FastAPI backend
│   └── utils/                       # (reserved for future helpers)
├── index.html                       # HTML shell, loads /src/main.jsx
├── vite.config.js                   # Vite build config with React plugin
├── tailwind.config.js               # Tailwind v3 design system config
├── postcss.config.js                # PostCSS pipeline (Tailwind + Autoprefixer)
└── package.json                     # Dependencies and npm scripts
```

---

## 🚀 Entry Point — `main.jsx`

**Purpose:** Bootstraps the React application into the DOM.

```jsx
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
```

| Part | Role |
|---|---|
| `ReactDOM.createRoot` | Mounts the React app into `<div id="root">` in `index.html` |
| `React.StrictMode` | Enables extra dev-time warnings and double-invocation checks |
| `BrowserRouter` | Provides HTML5 history-based routing context to the whole app |
| `import "./index.css"` | Loads Tailwind CSS directives so all utility classes work |

**Data Flow:** `main.jsx` → wraps `<App>` → routing context available everywhere

---

## 🏠 Root Component — `App.jsx`

**Purpose:** Owns the global `isDark` theme state, renders the sticky `<Navbar>`, the page `<Routes>`, and the footer.

### Inline SVG Icon Components

All icons are stateless functional components returning inline SVG. They carry **both** HTML `width`/`height` attributes and Tailwind `w-N h-N` classes to prevent oversized rendering before Tailwind CSS compiles.

| Component | Icon | Used In |
|---|---|---|
| `IconSearch` | 🔍 Magnifying glass | Navbar "Search" link |
| `IconGlobe` | 🌐 Globe | Navbar "Global" link |
| `IconMap` | 🗺 Map | Navbar "India" link |
| `IconSun` | ☀️ Sun | Theme toggle when dark mode is ON |
| `IconMoon` | 🌙 Moon | Theme toggle when dark mode is OFF |

---

### `Navbar` Component

**Props:**
| Prop | Type | Description |
|---|---|---|
| `isDark` | `boolean` | Current theme — used to style active nav links correctly per theme |
| `toggleTheme` | `function` | Flips `isDark` in the parent `App` component |

**Key Logic:**
```js
const isActive = (path) =>
  path === "/" ? location.pathname === "/" : location.pathname === path;
```
- Uses `useLocation()` from React Router to detect the current URL
- Active link gets an orange highlight; idle links get hover effects via `getLink(path)`

**Renders:**
- **Brand logo** (`📡 TrendIntel`) — always links back to `/`
- **Nav links** — Search (`/`), Global (`/trends`), India (`/region`)
- **Live badge** — green pulsing dot + "Live" text
- **Theme toggle button** — `<IconSun>` in dark mode, `<IconMoon>` in light mode

---

### `App` Component (default export)

**State:**

| Variable | Type | Initial Value | Description |
|---|---|---|---|
| `isDark` | `boolean` | Lazy: `localStorage` → `prefers-color-scheme` | Drives the entire dark/light theme |

**Lazy Initializer:**
```js
const [isDark, setIsDark] = useState(() => {
  const stored = localStorage.getItem("theme");
  if (stored) return stored === "dark";
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
});
```
- Reads `localStorage` first (persisted preference)
- Falls back to the OS/browser media query

**Side Effect — `useEffect`:**
```js
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
```
- Adds/removes `"dark"` class on `<html>` — activates/deactivates all `dark:` Tailwind variants
- Saves the choice to `localStorage` for persistence across sessions

**`toggleTheme`:** `() => setIsDark(prev => !prev)` — passed as prop down to `<Navbar>`

**Routes:**
| Path | Component | Description |
|---|---|---|
| `/` | `<Search>` | Keyword search page |
| `/trends` | `<GlobalTrends>` | All global trends list |
| `/region` | `<IndiaTrends>` | State-wise India trends |

---

## 🧩 Components — `src/components/`

> All components in this folder are **purely presentational**. They contain no `fetch()` calls, no `useEffect` for data loading, and no direct API imports. They receive data via props and communicate upward via callback props.

---

### `TrendCard.jsx`

**Shared by:** `Search.jsx`, `GlobalTrends.jsx`, `IndiaTrends.jsx`

**Purpose:** Renders a single trend item as a styled card with a rank badge, query text, score badge, and an animated progress bar. Previously duplicated inside each page — now a single shared source of truth.

**Props:**
| Prop | Type | Description |
|---|---|---|
| `trend` | `object` | `{ query: string, trend_score: number }` — one item from the API |
| `index` | `number` | 0-based position — drives the `#N` rank badge and staggered animation delay |

**Internal helper: `scoreConfig(s)`**
| Score | Tailwind `text` class | Tailwind `bg`/`border` class |
|---|---|---|
| `>= 70` | `text-emerald-400` | `bg-emerald-400/10 border-emerald-400/30` |
| `>= 40` | `text-yellow-400` | `bg-yellow-400/10 border-yellow-400/30` |
| `< 40` | `text-slate-400` | `bg-slate-500/10 border-slate-500/20` |

**What it renders:**
- Monospace rank badge: `#1`, `#2`, etc.
- Query text (middle, flexible width)
- Score badge (right, coloured by `scoreConfig`)
- Progress bar filled to `trend_score%` with orange gradient
- Orange top-border line that reveals on hover (`group-hover:opacity-100`)
- `animationDelay: index * 0.05s` → cards stagger in one after another

---

### `SearchBar.jsx`

**Used by:** `Search.jsx`

**Purpose:** Renders the search input UI — the text field, search icon, and "Search →" button. It is a **fully controlled component**: it owns no state of its own. The parent `Search.jsx` controls everything via props.

**Props:**
| Prop | Type | Description |
|---|---|---|
| `value` | `string` | The current text in the input (passed from parent's `query` state) |
| `onChange` | `function` | `(newValue: string) => void` — called on every keystroke |
| `onSearch` | `function` | `() => void` — called when user clicks Search or presses Enter |
| `loading` | `boolean` | Disables button and shows "Searching…" text |
| `placeholder` | `string` | Optional placeholder text (defaults to an example prompt) |

**Internal handler: `handleKey(e)`**
```js
const handleKey = (e) => {
  if (e.key === "Enter") onSearch();
};
```
Intercepts Enter key in the input and delegates to the parent's `onSearch`.

> **Design principle:** `SearchBar` never knows what `query` means or what `onSearch` does. It just renders the UI and fires callbacks. This makes it reusable for any search context.

---

### `StateDropdown.jsx`

**Used by:** `IndiaTrends.jsx`

**Purpose:** Renders the styled `<select>` dropdown listing all 28 Indian states and 8 Union Territories. Makes **zero API calls** — selecting a value only triggers the `onChange` callback so the parent page can decide what to do next.

**Props:**
| Prop | Type | Description |
|---|---|---|
| `value` | `string` | Currently selected state (controlled by parent's `state` state) |
| `onChange` | `function` | `(stateName: string) => void` — called when user picks a new option |

**Module-level constants (owned by this component):**

| Constant | Type | Description |
|---|---|---|
| `STATES` | `string[28]` | All 28 Indian states in alphabetical order |
| `UNION_TERRITORIES` | `string[8]` | All 8 Union Territories |
| `STATE_FLAGS` | `object` | Maps state names to decorative emoji (`"Goa" → "🏖️"`, etc.) |

**Exported utility: `getFlag(s)`**
```js
export const getFlag = (s) => STATE_FLAGS[s] ?? "📍";
```
- Also exported as a named export so `IndiaTrends.jsx` can use the same emoji map for the state preview pill, quick-pick chips, and spotlight card without duplicating the data.

**Renders:**
- A custom-styled `<select>` with `appearance-none` (removes native arrow)
- `<optgroup>` sections separating States from Union Territories
- Each `<option>` includes the emoji from `getFlag()`
- A custom SVG chevron arrow positioned absolutely over the right edge

---

### `Graph.jsx`

**Used by:** `GlobalTrends.jsx`, `IndiaTrends.jsx`

**Purpose:** Pure data visualization component — renders an SVG horizontal bar chart from a trends array. Contains **zero API calls and zero state**. The parent page fetches the data and passes it in.

**Props:**
| Prop | Type | Default | Description |
|---|---|---|---|
| `data` | `array` | `[]` | `Array<{ query: string, trend_score: number }>` |
| `title` | `string` | `"Trend Chart"` | Heading shown above the chart |
| `limit` | `number` | `10` | Max items to display (slices the array) |

**SVG layout constants (internal):**
| Constant | Value | Purpose |
|---|---|---|
| `ROW_H` | `40` | Pixel height per bar row |
| `LABEL_W` | `140` | Width of the left label column |
| `BAR_AREA` | `220` | Width of the bar + score number area |
| `PAD` | `16` | Top/bottom padding |

**Bar colour logic: `barColor(score)`**
| Score | Hex | Tailwind equivalent |
|---|---|---|
| `>= 70` | `#34d399` | emerald-400 |
| `>= 40` | `#fbbf24` | yellow-400 |
| `< 40` | `#94a3b8` | slate-400 |

**Renders:**
- Query labels (truncated at 18 chars with `…`)
- Background track bars (grey)
- Filled bars proportional to `trend_score / maxScore`
- Score numbers in monospace next to each bar
- A colour legend at the bottom (High / Mid / Low)
- Returns `null` if `data` is empty (renders nothing, no blank space)

> **Used via toggle:** Both `GlobalTrends` and `IndiaTrends` have a "📊 Chart / 📋 Cards" button that shows either `<Graph data={...} />` or the `<TrendCard>` grid — not both at once.

---

## 📄 Pages — `src/pages/`

> Pages own state and API orchestration. They import from `services/api.js` and compose components from `components/`.

---

### `Search.jsx` — Route `/`

**Purpose:** Lets users type a keyword or click a hot-topic chip to fetch and display a trend score.

**Imports:**
- `searchQuery` from `../services/api`
- `SearchBar` from `../components/SearchBar`
- `TrendCard` from `../components/TrendCard`

**Constants:**
| Name | Type | Description |
|---|---|---|
| `HOT_TOPICS` | `string[8]` | Pre-defined quick-search labels shown as orange pill chips |

**Helper: `scoreLabel(s)`**
Returns a plain-English description of the score level:
- `>= 70` → `"Trending massively right now"`
- `>= 40` → `"Moderate search interest"`
- `< 40` → `"Low search volume currently"`

**State:**
| Variable | Type | Initial | Description |
|---|---|---|---|
| `query` | `string` | `""` | Current text value — lifted up from `SearchBar` |
| `result` | `object \| null` | `null` | API response `{ query, trend_score }` |
| `loading` | `boolean` | `false` | `true` while API call is in-flight |
| `error` | `string \| null` | `null` | Error message shown in the error banner |

**Function: `doSearch(term?)`**
```js
const doSearch = async (term) => {
  const keyword = term ?? query;
  if (!keyword?.trim()) return;        // guard: skip blank searches
  setLoading(true); setError(null); setResult(null);
  try {
    const data = await searchQuery(keyword);
    setResult(data);
    setQuery(keyword);                 // sync input if called from a chip
  } catch {
    setError("Could not reach the API...");
  } finally {
    setLoading(false);
  }
};
```
- `term` optional param lets hot-topic chips bypass the `query` state (chips call `doSearch("IPL 2025")` directly)
- Clears previous result/error before each new request

**How SearchBar connects:**
```jsx
<SearchBar
  value={query}          // SearchBar displays this
  onChange={setQuery}    // every keystroke updates query state here
  onSearch={() => doSearch()}  // Search button / Enter → doSearch()
  loading={loading}      // button disables + shows "Searching…"
/>
```

**Rendered Sections:**
1. **Hero Banner** — background image, gradient overlay, headline, 3 stat counters
2. **Search Section** — heading, subtitle, `<SearchBar>` component
3. **Hot Topic Chips** — 8 orange pill buttons; click calls `doSearch(topic)`
4. **Skeleton Loader** — 3 shimmer bars while `loading === true`
5. **Error Banner** — orange-bordered card with ⚠️ message
6. **Result** — `scoreLabel()` text above + `<TrendCard trend={result} index={0} />`

**Data Flow:**
```
User types or clicks chip → doSearch(term)
        ↓
api.searchQuery(term)  →  GET /search?q=<term>
        ↓
{ query, trend_score }
        ↓
setResult(data)  →  <TrendCard> renders
```

---

### `GlobalTrends.jsx` — Route `/trends`

**Purpose:** Auto-fetches all global trends on mount and displays them. Supports manual refresh, a category filter UI, and toggle between card grid and bar chart.

**Imports:**
- `getTrends` from `../services/api`
- `TrendCard` from `../components/TrendCard`
- `Graph` from `../components/Graph`

**Constants:**
| Name | Value | Purpose |
|---|---|---|
| `CATEGORIES` | `["All","Technology",...]` | Filter chip labels (UI-only; backend filter not yet implemented) |

**State:**
| Variable | Type | Initial | Description |
|---|---|---|---|
| `trends` | `array` | `[]` | All trend objects from `getTrends()` |
| `loading` | `boolean` | `true` | `true` on mount and during refresh |
| `error` | `string \| null` | `null` | Error message |
| `spinning` | `boolean` | `false` | Controls the refresh icon rotation animation |
| `active` | `string` | `"All"` | Active category chip (UI only) |
| `showGraph` | `boolean` | `false` | Toggles between `<Graph>` and `<TrendCard>` grid |

**Function: `fetchData()`**
```js
const fetchData = async () => {
  setLoading(true); setError(null);
  try {
    const data = await getTrends();
    setTrends(Array.isArray(data) ? data : []); // safe array guard
  } catch {
    setError("Could not load trends...");
  } finally { setLoading(false); }
};
```
- Auto-called via `useEffect(() => { fetchData(); }, [])` on mount
- `Array.isArray` guard prevents crashes on unexpected API shapes

**Function: `handleRefresh()`**
```js
const handleRefresh = async () => {
  setSpinning(true);
  await fetchData();
  setTimeout(() => setSpinning(false), 650); // min spin duration
};
```
- Minimum 650ms spinner ensures visual feedback even for instant responses

**View Toggle:**
```jsx
{showGraph
  ? <Graph data={trends} title="All Trends Overview" limit={12} />
  : <div className="grid ...">
      {trends.map((t, i) => <TrendCard key={i} trend={t} index={i} />)}
    </div>
}
```
- "📊 Chart" button toggles `showGraph` — switches between `Graph` and `TrendCard` grid

**Rendered Sections:**
1. **Page Header** — title, topic count badge, "📊 Chart/📋 Cards" toggle, Refresh button
2. **Category Chips** — 6 filter pills, active one highlighted in orange
3. **Skeleton Grid** — 6 shimmer cards while loading
4. **Error / Empty states**
5. **Spotlight Card** — `trends[0]` in large type with full-width progress bar
6. **View** — either `<Graph>` or `<TrendCard>` grid (3-column responsive)

**Data Flow:**
```
Component mounts → useEffect → fetchData()
        ↓
api.getTrends()  →  GET /trends
        ↓
[{ query, trend_score }, ...]
        ↓
setTrends(data)
        ↓
Spotlight + TrendCard grid (or Graph)
```

---

### `IndiaTrends.jsx` — Route `/region`

**Purpose:** Manages state selection, calls the region API on demand, and displays filtered results. Composes `StateDropdown`, `TrendCard`, and `Graph`.

**Imports:**
- `getRegionTrends` from `../services/api`
- `StateDropdown`, `getFlag` from `../components/StateDropdown`
- `TrendCard` from `../components/TrendCard`
- `Graph` from `../components/Graph`

**Constants:**
| Name | Value | Description |
|---|---|---|
| `QUICK` | 6 popular states | Quick-pick chip buttons for fast access |

**State:**
| Variable | Type | Initial | Description |
|---|---|---|---|
| `state` | `string` | `"India"` | Selected state/UT — drives the API call |
| `data` | `array` | `[]` | Region trend results |
| `loading` | `boolean` | `false` | `true` while API call is in-flight |
| `error` | `string \| null` | `null` | Error message |
| `fetched` | `boolean` | `false` | `true` after first API call — gates empty-state display |
| `showGraph` | `boolean` | `false` | Toggles between `<Graph>` and `<TrendCard>` grid |

> **Why `fetched`?** Without it, the "No data" empty state would appear immediately on page load before the user has clicked anything. `fetched` ensures that message only appears after a real API call returns nothing.

**Function: `handleFetch(overrideState?)`**
```js
const handleFetch = async (overrideState) => {
  const target = overrideState ?? state;
  setLoading(true); setError(null); setData([]);
  try {
    const res = await getRegionTrends(target);
    setData(Array.isArray(res) ? res : []);
  } catch {
    setError("Could not load region trends...");
  } finally {
    setLoading(false);
    setFetched(true);
  }
};
```

> **Why `overrideState`?** React `setState` is asynchronous. Quick-pick chips call `setState(s)` and `handleFetch(s)` back-to-back. Without the override, `handleFetch()` would still read the *old* `state` value because the component hasn't re-rendered yet. Passing the state name directly bypasses this timing issue.

**How StateDropdown connects:**
```jsx
<StateDropdown
  value={state}           // controlled value — shows current selection
  onChange={setState}     // only updates the dropdown display, no API call
/>
```
The API call only fires when the user clicks the "Get Trends" button or a quick-pick chip.

**Quick-pick chip pattern:**
```jsx
onClick={() => {
  setState(s);        // update dropdown to reflect new selection
  handleFetch(s);     // fetch immediately using override (bypasses async setState)
}}
```

**Rendered Sections:**
1. **Page Header** — title, results count badge (after fetch), "📊/📋" toggle
2. **Subtitle**
3. **Controls Row** — state preview pill + `<StateDropdown>` + "Get Trends" button
4. **Quick-pick Chips** — 6 shortcut buttons with emoji flags from `getFlag()`
5. **Skeleton Grid** — 6 shimmer placeholders during loading
6. **Error State**
7. **Initial Prompt** — shown when `!fetched && !loading`
8. **Empty After Fetch** — shown when `fetched && data.length === 0`
9. **Spotlight Card** — region flag + "Top Trend ·" label + `data[0]`
10. **View** — `<Graph>` or `<TrendCard>` grid based on `showGraph`

**Data Flow:**
```
User clicks quick-chip / selects dropdown + "Get Trends"
              ↓
handleFetch("Delhi")  or  handleFetch()
              ↓
api.getRegionTrends("Delhi")  →  GET /region?state=Delhi
              ↓
[{ query, trend_score }, ...]
              ↓
setData(res) + setFetched(true)
              ↓
Spotlight + TrendCard grid (or Graph)
```

---

## 🔗 API Service — `services/api.js`

**Purpose:** Centralises all HTTP communication with the FastAPI backend. No page or component ever calls `fetch()` directly — everything goes through this module.

### Base URL
```js
const BASE_URL = "http://127.0.0.1:8000";
```
> ⚠️ Hardcoded to localhost. For production use `import.meta.env.VITE_API_URL`.

### Exported Functions

#### `searchQuery(q)` → used by `Search.jsx`
```js
export const searchQuery = async (q) => {
  const res = await fetch(`${BASE_URL}/search?q=${q}`);
  return res.json();
};
```
| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/search?q=<keyword>` |
| **Returns** | `{ query: string, trend_score: number }` |

#### `getTrends()` → used by `GlobalTrends.jsx`
```js
export const getTrends = async () => {
  const res = await fetch("http://127.0.0.1:8000/trends");
  return res.json();
};
```
| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/trends` |
| **Returns** | `Array<{ query: string, trend_score: number }>` |

#### `getRegionTrends(state)` → used by `IndiaTrends.jsx`
```js
export const getRegionTrends = async (state) => {
  const res = await fetch(`http://127.0.0.1:8000/region?state=${state}`);
  return res.json();
};
```
| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/region?state=<stateName>` |
| **Returns** | `Array<{ query: string, trend_score: number }>` |

> **Error handling pattern:** All three functions throw on network failure. Each calling page wraps them in `try/catch` and sets its own `error` state — keeping the service layer clean and generic.

---

## 🎨 Styling System — `index.css` + `tailwind.config.js`

### Tailwind Dark Mode
Strategy: `"class"` — Tailwind activates `dark:` variants when `<html>` has the `"dark"` class. `App.jsx` adds/removes this class via `useEffect` when `isDark` changes.

### Custom Design Tokens

#### Colors
| Token | Value | Usage |
|---|---|---|
| `accent.DEFAULT` | `#ff4500` | Primary orange-red brand color |
| `accent.hover` | `#ff5722` | Hover shade |
| `accent.light` | `#ff6b35` | Gradient end |
| `dark.base` | `#0d1117` | Deepest background |
| `dark.card` | `#1c2128` | Card backgrounds |
| `dark.border` | `#30363d` | Border color |

#### Custom Animations
| Class | Duration | Effect |
|---|---|---|
| `animate-fade-up` | 0.5s | Fade in + slide up 20px |
| `animate-fade-in` | 0.4s | Opacity only |
| `animate-float` | 3s loop | Gentle vertical bob |
| `animate-pulse-dot` | 2s loop | Live indicator pulse |
| `animate-shimmer` | 1.4s loop | Skeleton shimmer sweep |

#### Custom Shadows
| Token | Value |
|---|---|
| `shadow-glow-sm` | `0 0 12px rgba(255,69,0,0.2)` |
| `shadow-glow-md` | `0 0 24px rgba(255,69,0,0.3)` |
| `shadow-card` | `0 4px 24px rgba(0,0,0,0.35)` |

### Custom CSS Utilities (`index.css`)
| Class | Description |
|---|---|
| `.skeleton` | Dark shimmer animation background |
| `.skeleton-light` | Light-mode shimmer variant |
| `.gradient-text` | Gradient text — dark mode |
| `.btn-accent` | Orange-red gradient background |
| `.glow-focus` | Orange focus ring on `:focus-within` |

---

## 🔄 Theme System

```
User clicks theme-toggle (Navbar)
          ↓
  toggleTheme() → setIsDark(!isDark)
          ↓
  useEffect fires → adds/removes "dark" on <html>
                 → saves to localStorage
          ↓
  All dark: Tailwind variants activate/deactivate
          ↓
  Full UI switches theme instantly, no flash
```

**Persistence:** Lazy `useState` initializer reads `localStorage` before first render — correct theme applied immediately.  
**System default:** Falls back to `prefers-color-scheme` if no `localStorage` entry exists.

---

## 🔁 Complete Application Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                            BROWSER                                  │
│                                                                     │
│  main.jsx                                                           │
│    └── BrowserRouter                                                │
│          └── App.jsx  [isDark, toggleTheme]                         │
│                ├── Navbar  [isDark, toggleTheme props]              │
│                │     └── Theme toggle + active nav links            │
│                ├── Routes                                           │
│                │     ├── "/" → Search.jsx  [query, result, loading] │
│                │     │         ├── <SearchBar value onChange />      │
│                │     │         └── <TrendCard trend index />        │
│                │     │         → api.searchQuery()                  │
│                │     │                                              │
│                │     ├── "/trends" → GlobalTrends.jsx               │
│                │     │         [trends[], loading, showGraph]       │
│                │     │         ├── <TrendCard> grid OR              │
│                │     │         └── <Graph data />                   │
│                │     │         → api.getTrends()                    │
│                │     │                                              │
│                │     └── "/region" → IndiaTrends.jsx                │
│                │               [state, data[], fetched, showGraph]  │
│                │               ├── <StateDropdown value onChange /> │
│                │               ├── <TrendCard> grid OR              │
│                │               └── <Graph data />                   │
│                │               → api.getRegionTrends()              │
│                └── Footer                                           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP GET
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend  (port 8000)                        │
│    GET /search?q=<keyword>   →  { query, trend_score }              │
│    GET /trends               →  [{ query, trend_score }, ...]       │
│    GET /region?state=<name>  →  [{ query, trend_score }, ...]       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Dependencies (`package.json`)

### Runtime
| Package | Version | Purpose |
|---|---|---|
| `react` | ^18.2.0 | Core UI library |
| `react-dom` | ^18.2.0 | DOM rendering |
| `react-router-dom` | ^7.13.2 | Client-side routing |

### Dev Dependencies
| Package | Version | Purpose |
|---|---|---|
| `vite` | ^5.0.0 | Dev server + build tool |
| `@vitejs/plugin-react` | ^4.0.0 | JSX transform + Fast Refresh |
| `tailwindcss` | ^3.x | Utility-first CSS |
| `postcss` | latest | CSS transformation pipeline |
| `autoprefixer` | latest | Vendor prefix generation |

---

## 🛠️ Build & Dev Scripts

| Command | What it does |
|---|---|
| `npm run dev` | Starts Vite dev server (port 5173, auto-increments if occupied) |
| `npm run build` | Compiles production bundle into `dist/` |
| `npm run preview` | Serves `dist/` locally to test the production build |

---

## 🧩 Full Component & Page Summary

| File | Export | Layer | Route | API Calls | Imports From |
|---|---|---|---|---|---|
| `main.jsx` | — | Entry | All | None | — |
| `App.jsx` | `App` | Shell | All | None | pages/* |
| `App.jsx` | `Navbar` | Component | All | None | — |
| `pages/Search.jsx` | `Search` | Page | `/` | `searchQuery()` | `SearchBar`, `TrendCard` |
| `pages/GlobalTrends.jsx` | `GlobalTrends` | Page | `/trends` | `getTrends()` | `TrendCard`, `Graph` |
| `pages/IndiaTrends.jsx` | `IndiaTrends` | Page | `/region` | `getRegionTrends()` | `StateDropdown`, `TrendCard`, `Graph` |
| `components/TrendCard.jsx` | `TrendCard` | Component | — | **None** | — |
| `components/SearchBar.jsx` | `SearchBar` | Component | — | **None** | — |
| `components/StateDropdown.jsx` | `StateDropdown`, `getFlag` | Component | — | **None** | — |
| `components/Graph.jsx` | `Graph` | Component | — | **None** | — |
| `services/api.js` | `searchQuery` | Service | — | Backend `/search` | — |
| `services/api.js` | `getTrends` | Service | — | Backend `/trends` | — |
| `services/api.js` | `getRegionTrends` | Service | — | Backend `/region` | — |

---

## ⚠️ Known Limitations & Future Improvements

| Area | Current State | Suggested Improvement |
|---|---|---|
| **API Base URL** | Hardcoded to `http://127.0.0.1:8000` | Use `import.meta.env.VITE_API_URL` env variable |
| **Category Filter Chips** | UI-only — not wired to any API filter | Add `?category=` query param to `/trends` endpoint |
| **URL encoding** | State names with spaces not URL-encoded | Use `encodeURIComponent(state)` in `getRegionTrends()` |
| **Error boundaries** | No React `<ErrorBoundary>` wrapper | Wrap pages to prevent full-app crash on unhandled errors |
| **Graph library** | Custom SVG — limited interactivity | Migrate to Recharts or Chart.js for tooltips, zoom, etc. |
| **Accessibility** | Minimal ARIA attributes | Add `aria-live` regions for search results, labels on inputs |
| **Score bar animation** | Only fires on first render | Re-trigger via a keyed remount or CSS transition on value change |

---

*Documentation last updated: March 2026 — reflects component extraction refactor*
