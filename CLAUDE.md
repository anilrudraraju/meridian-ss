# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

No build step. No tests yet. The only runtime dependencies are `streamlit>=1.32.0` and `pandas>=2.0.0`.

## What this is

Meridian-SS is a Streamlit-based research workstation for spinoff and special-situation investing. The current state is a **UI-only scaffold (v1)** — the full multi-agent backend is planned but not yet wired. Backend stubs are marked with `# TODO:` comments throughout `app.py`.

## Architecture

The entire application is a single file: [app.py](app.py). `core/__init__.py` exists but is empty — it is the package that will house backend modules as they are built.

### Navigation model

The app uses a manual tab system driven by `st.session_state.active_tab` (values: `"dashboard"`, `"new_analysis"`, `"updates"`, `"company_detail"`). There is no `st.tabs()` — navigation happens via sidebar buttons that set `active_tab` and call `st.rerun()`. The main body is a series of `if/elif` blocks keyed on `active_tab`.

### New Analysis wizard (6 steps)

The core user flow is a wizard controlled by `st.session_state.na_step` (1–6):

| Step | Name | Purpose |
|------|------|---------|
| 1 | Intake | Ticker + situation type; TODO: validate CIK on SEC EDGAR |
| 2 | Documents | Gather Form 10, 10-K, transcripts, etc. via EDGAR fetch / PDF upload / URL paste |
| 3 | Ingest | LlamaParse → chunk → embed (ada-002) → Chroma + BM25; TODO: wire pipeline |
| 4 | Explore | Hybrid retrieval Q&A with citations; TODO: wire Sonnet synthesis |
| 5 | Committee | 5-agent debate via `InvestmentCommittee` + Greenblatt 35-criterion scorecard; TODO: wire |
| 6 | Memo | Opus 4.7-generated investment memo + Invest/Watch/Reject decision journal; TODO: wire |

### Planned backend (from inline TODOs)

- **SEC EDGAR**: ticker → CIK validation; HTML filing fetches (Form 10, 10-K, 10-Q, 8-K, DEF 14A); XBRL company facts for structured financial data

- **Ingestion pipeline — per document type**:

  | Document | Source format | Parsing | Financial numbers |
  |---|---|---|---|
  | Form 10 / 10-12B | HTML (EDGAR or manual URL) | BeautifulSoup section split on H-tags | Haiku sidecar (no XBRL on registration statements) |
  | Parent 10-K / 10-Q | HTML (EDGAR or manual URL) | BeautifulSoup section split | XBRL company facts API (primary); Haiku for non-XBRL gaps (pension, adjusted EBITDA) |
  | Investor day deck | PDF upload | LlamaParse → section split | Haiku for projection tables |
  | Earnings transcript | Text paste or URL | Paragraph-level split (Q&A blocks intact) | Vector index only |
  | Newsletter / writeup | Text paste, URL, or PDF | Paragraph-level split | Vector index only |

  All chunks → OpenAI ada-002 embeddings → Chroma (`meridian_ss_{situation_id}`) + BM25 (`rank-bm25`) hybrid retrieval.

  HTML chunking uses `MarkdownHeaderTextSplitter` after BeautifulSoup extraction, with a `RecursiveCharacterTextSplitter` (1,200 token max, 150 overlap) fallback for oversized sections.

- **XBRL sidecar**: `data.sec.gov/api/xbrl/companyfacts/CIK{n}.json` → structured JSON of all GAAP-tagged metrics. Stored in SQLite alongside situation. Committee agents query this directly — no vector search for standard financial numbers.

- **Haiku sidecar**: Narrow scope — targeted at specific HTML sections that XBRL doesn't cover (Form 10 distribution/capitalization sections, pension footnotes, debt maturity schedules, adjusted EBITDA definitions). One Haiku call per section, not per document.

- **InvestmentCommittee**: 5 agents — Setup Specialist, Business Quality Analyst, Capital Structure Analyst, Valuation Analyst, Devil's Advocate — debating in 3 rounds via a MessageBus. Sonnet 4.6 × 4 agents + Opus 4.7 × Devil's Advocate. Agents use XBRL sidecar for numbers + vector retrieval for qualitative context.

- **Memo generation**: Claude Opus 4.7 producing a structured 8-section memo

- **Persistence**: SQLite (`meridian.db`) for `notes`, `documents`, `decision_logs`, XBRL sidecar, Haiku sidecar, and `Situation.status`

- **Tendency Coach**: behavioral pattern detection (#SetupParalysis, #AnalysisParalysis, etc.) displayed before decisions on re-runs

### Session state keys

All wizard state lives in `st.session_state` with `na_` prefix (new analysis) or `dj_` prefix (decision journal). `_init()` sets defaults on first load without overwriting existing values.

### Score colors

Scores ≥ 80 → green (`#22c55e`), 60–79 → amber (`#f59e0b`), < 60 → red (`#ef4444`). The `_score_color()` and `_traffic_light()` helpers implement this.

## Key constants

- `SITUATION_TYPES` — 7 situation categories (Spinoff, Carve-out, etc.)
- `REQUIRED_DOCS` — 6 required document types with their state keys
- `AGENTS` — 5 committee agents with icon, role, dimension, and brand color
- `STEPS` — 6 wizard step labels

## API keys

OpenAI and Anthropic keys are entered via a sidebar expander and written to `os.environ` at runtime. They are **not persisted** between sessions. When wiring the backend, read from `os.environ["OPENAI_API_KEY"]` / `os.environ["ANTHROPIC_API_KEY"]`.
