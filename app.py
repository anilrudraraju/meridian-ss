"""
Meridian-SS — Spinoff & Special-Situations Research Workstation
Scaffold v1: four-tab shell + New Analysis 6-step wizard (UI only)
"""

import os
from datetime import date, datetime

import pandas as pd
import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Meridian-SS",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "2026-05-22-v1-scaffold"

# ── Constants ──────────────────────────────────────────────────────────────────
SITUATION_TYPES = [
    "Spinoff",
    "Carve-out",
    "Split-off",
    "Recap",
    "Rights offering",
    "Risk arbitrage",
    "Post-bankruptcy",
]

REQUIRED_DOCS = [
    ("Form 10 / 10-12B/A",         "form10"),
    ("Parent 10-K",                 "parent_10k"),
    ("Earnings transcript (last)",  "transcript_1"),
    ("Earnings transcript (prior)", "transcript_2"),
    ("Investor day / deck",         "investor_deck"),
    ("Newsletter writeup",          "newsletter"),
]

STEPS = [
    (1, "Intake"),
    (2, "Documents"),
    (3, "Ingest"),
    (4, "Explore"),
    (5, "Committee"),
    (6, "Memo"),
]

AGENTS = [
    ("🔬", "Setup Specialist",          "Dimension 1 · Setup Quality",      "#8b5cf6"),
    ("📈", "Business Quality Analyst",  "Dimension 2 · Business Quality",   "#3b82f6"),
    ("🏗️", "Capital Structure Analyst", "Dimension 3 · Capital Structure",  "#f59e0b"),
    ("💰", "Valuation Analyst",         "Dimension 4 · Valuation",          "#10b981"),
    ("😈", "Devil's Advocate",          "Cross-cutting · Governance / Risk", "#ef4444"),
]

# ── Session state defaults ─────────────────────────────────────────────────────
def _init():
    defaults = {
        "active_tab":        "dashboard",
        # New Analysis wizard
        "na_step":           1,
        "na_ticker":         "",
        "na_parent_ticker":  "",
        "na_sit_type":       "Spinoff",
        "na_seed_url":       "",
        "na_step1_done":     False,
        "na_doc_states":     {k: "—" for _, k in REQUIRED_DOCS},
        "na_step2_done":     False,
        "na_ingest_done":    False,
        "na_qa_history":     [],
        "na_committee_done": False,
        "na_scorecard":      None,
        # Decision journal
        "dj_open":           False,
        "dj_verdict":        None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ── Helpers ────────────────────────────────────────────────────────────────────
def _go(tab: str):
    st.session_state.active_tab = tab
    st.rerun()


def _step_indicator(current: int):
    """Horizontal step progress bar."""
    cols = st.columns(len(STEPS))
    for col, (n, label) in zip(cols, STEPS):
        with col:
            if n < current:
                st.markdown(
                    f"<div style='text-align:center;padding:6px 0;"
                    f"border-bottom:3px solid #22c55e;color:#22c55e;font-size:13px'>"
                    f"✓ {n}. {label}</div>",
                    unsafe_allow_html=True,
                )
            elif n == current:
                st.markdown(
                    f"<div style='text-align:center;padding:6px 0;"
                    f"border-bottom:3px solid #3b82f6;color:#3b82f6;"
                    f"font-weight:700;font-size:13px'>"
                    f"● {n}. {label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align:center;padding:6px 0;"
                    f"border-bottom:2px solid #e2e8f0;color:#94a3b8;font-size:13px'>"
                    f"○ {n}. {label}</div>",
                    unsafe_allow_html=True,
                )
    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)


def _doc_badge(state: str) -> str:
    return {"fetched": "✅", "uploaded": "📎", "url": "🔗", "missing": "⚠️", "—": "○"}.get(state, "○")


def _docs_resolved() -> int:
    return sum(
        1 for v in st.session_state.na_doc_states.values()
        if v in ("fetched", "uploaded", "url")
    )


def _score_color(score: int) -> str:
    if score >= 80:
        return "#22c55e"
    if score >= 60:
        return "#f59e0b"
    return "#ef4444"


def _traffic_light(score: int) -> str:
    if score >= 80:
        return "🟢 Intact"
    if score >= 60:
        return "🟡 Review"
    return "🔴 Concern"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**Meridian-SS**")
    st.caption(f"Spinoff Research Workstation · {APP_VERSION}")
    st.divider()

    nav_items = [
        ("dashboard",      "📊", "Dashboard"),
        ("new_analysis",   "🔍", "New Analysis"),
        ("updates",        "🔔", "Updates"),
        ("company_detail", "🏢", "Company Detail"),
    ]
    for key, icon, label in nav_items:
        is_active = st.session_state.active_tab == key
        prefix = "▶ " if is_active else "    "
        if st.button(
            f"{prefix}{icon} {label}",
            key=f"nav_{key}",
            use_container_width=True,
        ):
            st.session_state.active_tab = key
            st.rerun()

    st.divider()
    with st.expander("🔑 API keys"):
        oai = st.text_input("OpenAI", type="password", key="sk_openai")
        ant = st.text_input("Anthropic", type="password", key="sk_anthropic")
        if oai:
            os.environ["OPENAI_API_KEY"] = oai
        if ant:
            os.environ["ANTHROPIC_API_KEY"] = ant
        st.caption("Keys are not persisted between sessions.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "dashboard":
    st.title("📊 Dashboard")
    st.caption("Your spinoff research portfolio at a glance.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Invested", "—",  help="Situations with status = invest")
    c2.metric("Watchlist", "—", help="Situations with status = watch")
    c3.metric(
        "Pending Review", "—",
        delta="New filings",
        delta_color="normal",
        help="10-Qs and 8-Ks awaiting re-run",
    )
    c4.metric("Avg Composite Score", "—", help="Weighted average across invested positions")

    st.divider()

    st.subheader("Portfolio")
    st.info("No invested positions yet. Complete a New Analysis and click **Invest** to populate this table.")

    st.subheader("Watchlist")
    st.info("No watchlist positions. Click **Watch** in a New Analysis to add a name here.")

    st.subheader("Pending Review")
    st.info("No pending updates. Once you have invested or watched positions, new filings appear here.")

    st.divider()
    col_cta, _ = st.columns([1, 3])
    with col_cta:
        if st.button("🔍 Start New Analysis", type="primary", use_container_width=True):
            _go("new_analysis")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: NEW ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "new_analysis":

    # Persistent header strip
    ticker_display = st.session_state.na_ticker or "New situation"
    st.markdown(
        f"<h2 style='margin-bottom:2px'>🔍 New Analysis"
        f"<span style='font-size:16px;font-weight:400;color:#64748b;margin-left:12px'>"
        f"{ticker_display} · {st.session_state.na_sit_type}</span></h2>",
        unsafe_allow_html=True,
    )
    if not st.session_state.na_step1_done:
        st.warning(
            "Analysis is not complete until all 6 steps and the "
            "**Invest / Watch / Reject** decision are logged."
        )

    current_step = st.session_state.na_step
    _step_indicator(current_step)

    # Prev / Next navigation
    nav_l, _, nav_r = st.columns([1, 6, 1])
    with nav_l:
        if current_step > 1:
            if st.button("← Back", key="step_back"):
                st.session_state.na_step -= 1
                st.rerun()
    with nav_r:
        if current_step < 6:
            if st.button("Next →", key="step_fwd", type="primary"):
                st.session_state.na_step += 1
                st.rerun()

    st.markdown("---")

    # ── Step 1: Intake ─────────────────────────────────────────────────────────
    if current_step == 1:
        st.subheader("Step 1 · Intake")
        st.caption(
            "Enter the SpinCo ticker and situation details. "
            "The system validates the ticker against SEC EDGAR and fetches the entity record."
        )

        with st.form("intake_form"):
            col_t, col_s = st.columns(2)
            with col_t:
                ticker = st.text_input(
                    "SpinCo Ticker *",
                    value=st.session_state.na_ticker,
                    placeholder="e.g. KVYO, WK, GXO",
                    help="Must resolve to a valid CIK on SEC EDGAR.",
                )
            with col_s:
                sit_type = st.selectbox(
                    "Situation Type *",
                    SITUATION_TYPES,
                    index=SITUATION_TYPES.index(st.session_state.na_sit_type),
                )

            col_p, col_u = st.columns(2)
            with col_p:
                parent = st.text_input(
                    "Parent Ticker",
                    value=st.session_state.na_parent_ticker,
                    placeholder="Auto-populated from EDGAR",
                )
            with col_u:
                seed_url = st.text_input(
                    "Seed Thesis URL (optional)",
                    value=st.session_state.na_seed_url,
                    placeholder="Newsletter, blog post, or writeup URL",
                )

            submitted = st.form_submit_button("Validate & Continue →", type="primary")
            if submitted:
                if not ticker.strip():
                    st.error("Ticker is required.")
                else:
                    st.session_state.na_ticker         = ticker.strip().upper()
                    st.session_state.na_sit_type       = sit_type
                    st.session_state.na_parent_ticker  = parent.strip().upper()
                    st.session_state.na_seed_url       = seed_url.strip()
                    st.session_state.na_step1_done     = True
                    # TODO: validate CIK on EDGAR; auto-populate parent ticker
                    st.session_state.na_step           = 2
                    st.rerun()

        if st.session_state.na_sit_type == "Spinoff":
            st.info(
                "For Spinoffs the system checks for a Form 10 or 10-12B/A on EDGAR. "
                "If none exists it will warn you in Step 2."
            )

    # ── Step 2: Documents ──────────────────────────────────────────────────────
    elif current_step == 2:
        ticker = st.session_state.na_ticker or "—"
        resolved = _docs_resolved()

        st.subheader("Step 2 · Documents")
        st.caption(
            f"Gather source documents for **{ticker}**. "
            f"{resolved} / {len(REQUIRED_DOCS)} resolved — "
            f"Step 3 unlocks when at least 4 are resolved."
        )

        # Three input affordances
        aff1, aff2, aff3 = st.columns(3, gap="medium")

        with aff1:
            st.markdown("**📡 EDGAR Auto-fetch**")
            st.caption("Fetches Form 10, 10-K, 10-Q, 8-K, DEF 14A for the entered ticker.")
            if st.button("Fetch from EDGAR", use_container_width=True, key="edgar_fetch"):
                # TODO: call fetch_edgar_filing() for each document type
                st.session_state.na_doc_states["form10"]     = "fetched"
                st.session_state.na_doc_states["parent_10k"] = "fetched"
                st.toast("EDGAR fetch complete (placeholder). Wiring in Package 2.")
                st.rerun()

        with aff2:
            st.markdown("**📎 Upload PDF**")
            st.caption("Drag-and-drop one or more filings.")
            uploaded = st.file_uploader(
                "Upload", accept_multiple_files=True, type=["pdf"],
                key="doc_upload", label_visibility="collapsed",
            )
            if uploaded:
                # TODO: route file to the correct doc_type based on filename / user selection
                for f in uploaded:
                    st.success(f"Received: {f.name} (backend not wired yet)")

        with aff3:
            st.markdown("**🔗 Paste URL**")
            st.caption("Earnings transcript, investor deck, newsletter.")
            paste_url  = st.text_input("URL", key="paste_url",
                                        label_visibility="collapsed",
                                        placeholder="https://…")
            paste_type = st.selectbox(
                "Type", [lbl for lbl, _ in REQUIRED_DOCS],
                key="paste_doc_type", label_visibility="collapsed",
            )
            if st.button("Add URL", key="add_url") and paste_url:
                key_map = {lbl: k for lbl, k in REQUIRED_DOCS}
                st.session_state.na_doc_states[key_map[paste_type]] = "url"
                st.rerun()

        st.divider()
        st.markdown("**Required documents checklist**")

        for label, key in REQUIRED_DOCS:
            state = st.session_state.na_doc_states[key]
            badge = _doc_badge(state)
            col_b, col_l, col_a = st.columns([0.05, 0.65, 0.30])

            with col_b:
                st.markdown(badge)
            with col_l:
                st.markdown(f"`{label}`")
                state_labels = {
                    "—":       "Not yet provided",
                    "fetched": "Auto-fetched from EDGAR",
                    "uploaded":"Uploaded",
                    "url":     "URL provided",
                    "missing": "Marked as unavailable",
                }
                st.caption(state_labels.get(state, ""))
            with col_a:
                if state == "—":
                    if st.button("Mark missing", key=f"miss_{key}", use_container_width=True):
                        st.session_state.na_doc_states[key] = "missing"
                        st.rerun()
                elif state == "missing":
                    if st.button("Unmark", key=f"unmiss_{key}", use_container_width=True):
                        st.session_state.na_doc_states[key] = "—"
                        st.rerun()

        st.divider()
        resolved = _docs_resolved()
        if resolved >= 4:
            st.success(f"{resolved} / {len(REQUIRED_DOCS)} documents resolved. Ready to ingest.")
            if st.button("Proceed to Ingest →", type="primary"):
                st.session_state.na_step2_done = True
                st.session_state.na_step       = 3
                st.rerun()
        else:
            st.warning(
                f"{resolved} / {len(REQUIRED_DOCS)} resolved. "
                f"Resolve at least 4 to continue."
            )

    # ── Step 3: Ingest ─────────────────────────────────────────────────────────
    elif current_step == 3:
        st.subheader("Step 3 · Ingest")
        st.caption(
            "Documents are parsed with LlamaParse, split into chunks, and indexed in "
            "both a vector store (cosine similarity) and a keyword store (BM25). "
            "Failures appear in red with retry options."
        )

        PIPELINE = [
            ("LlamaParse PDF extraction",  "Layout-aware markdown conversion; tables preserved as atomic units"),
            ("Markdown-header chunking",   "Section splitting via LangChain MarkdownHeaderTextSplitter (H1–H3)"),
            ("Embedding (ada-002)",        "1,536-dim vectors per chunk, batched in groups of 100"),
            ("Chroma index build",         "Per-situation collection: meridian_ss_{situation_id}"),
            ("BM25 index build",           "Keyword retrieval index via rank-bm25; persisted alongside Chroma"),
            ("Financial pre-extraction",   "Haiku call extracts EBIT, EBITDA, net debt, ROIC components"),
        ]

        if not st.session_state.na_ingest_done:
            col_btn, col_cost = st.columns([1, 3])
            with col_btn:
                run_ingest = st.button("▶ Run Ingestion", type="primary", use_container_width=True)
            with col_cost:
                st.caption("Estimated cost: ~$0.02–$0.05 per document (Haiku pre-extraction only)")

            if run_ingest:
                # TODO: call ingestion pipeline (LlamaParse → chunk → embed → index → pre-extract)
                with st.spinner("Running ingestion pipeline…"):
                    import time
                    time.sleep(1)  # placeholder delay
                st.session_state.na_ingest_done = True
                st.rerun()
        else:
            for stage, desc in PIPELINE:
                ci, cs, cd = st.columns([0.04, 0.32, 0.64])
                ci.markdown("✅")
                cs.markdown(f"**{stage}**")
                cd.caption(desc)

            st.success(
                "Ingestion complete. Step 4 (Explore) is optional — "
                "you can skip directly to the Committee."
            )
            col_e, col_c = st.columns(2)
            with col_e:
                if st.button("Step 4: Explore →", use_container_width=True):
                    st.session_state.na_step = 4
                    st.rerun()
            with col_c:
                if st.button("Skip to Committee →", use_container_width=True, type="primary"):
                    st.session_state.na_step = 5
                    st.rerun()

    # ── Step 4: Explore ────────────────────────────────────────────────────────
    elif current_step == 4:
        st.subheader("Step 4 · Explore (optional)")
        st.caption(
            "Ask questions against the indexed corpus. Answers include inline citations. "
            "Save useful exchanges as notes for the memo."
        )

        # Retrieval filter pills
        fp1, fp2, fp3, fp4 = st.columns(4)
        fp1.checkbox("Form 10 only",    key="filt_form10")
        fp2.checkbox("10-K only",       key="filt_10k")
        fp3.checkbox("MD&A section",    key="filt_mdna")
        fp4.checkbox("Risk factors",    key="filt_risks")

        question = st.text_input(
            "Ask a question",
            placeholder="e.g. What was SpinCo's ROIC for the last 3 years?",
            key="qa_input",
        )
        col_ask, _ = st.columns([1, 5])
        with col_ask:
            ask_clicked = st.button("Ask", type="primary", use_container_width=True)

        if ask_clicked and question:
            # TODO: hybrid retrieval (BM25 + cosine) → Claude Sonnet synthesis with citations
            mock_answer = (
                f"[Backend not wired — Package 2+3] "
                f"The hybrid retrieval answer to *'{question}'* will appear here, "
                f"with inline citations such as *(Form 10, §Item 7 MD&A, p. 42)*."
            )
            st.session_state.na_qa_history.append({
                "q":     question,
                "a":     mock_answer,
                "ts":    datetime.now().strftime("%H:%M"),
                "saved": False,
            })
            st.rerun()

        if st.session_state.na_qa_history:
            st.divider()
            st.markdown(f"**Session Q&A** ({len(st.session_state.na_qa_history)} exchanges)")
            for i, entry in enumerate(reversed(st.session_state.na_qa_history)):
                with st.expander(f"Q: {entry['q']}  ·  {entry['ts']}"):
                    st.markdown(entry["a"])
                    sb1, sb2, sb3 = st.columns(3)
                    sb1.button("💾 Save to notes", key=f"qa_save_{i}")
                    sb2.button("🏷️ Tag",           key=f"qa_tag_{i}")
                    sb3.button("🔎 Dig deeper",     key=f"qa_dig_{i}")
        else:
            st.info("No questions yet. Ask something about the indexed documents.")

        st.divider()
        if st.button("Proceed to Committee →", type="primary"):
            st.session_state.na_step = 5
            st.rerun()

    # ── Step 5: Committee ──────────────────────────────────────────────────────
    elif current_step == 5:
        ticker = st.session_state.na_ticker or "—"
        st.subheader("Step 5 · Committee")
        st.caption(
            f"Five agents debate **{ticker}** against the 35-criterion Greenblatt scorecard "
            f"in 3 rounds via MessageBus. Each agent scores its assigned dimension with evidence citations."
        )

        if not st.session_state.na_committee_done:
            # Agent roster preview
            st.markdown("**Agent roster**")
            for icon, role, dim, color in AGENTS:
                st.markdown(
                    f"<div style='border-left:3px solid {color};"
                    f"padding:4px 10px;margin:4px 0;font-size:14px'>"
                    f"<strong>{icon} {role}</strong> — {dim}</div>",
                    unsafe_allow_html=True,
                )

            st.divider()
            col_btn, col_cost = st.columns([1, 3])
            with col_btn:
                run_committee = st.button(
                    "▶ Convene Committee", type="primary", use_container_width=True
                )
            with col_cost:
                st.caption(
                    "Estimated cost: ~$0.35–$0.55  "
                    "(Sonnet 4.6 × 4 agents + Opus 4.7 × 1 agent · 3 rounds · ~12k tokens)"
                )

            if run_committee:
                # TODO: call InvestmentCommittee with spinoff agents + Greenblatt skill loaded
                with st.spinner("Agents debating… Round 1 → Round 2 → Round 3"):
                    import time
                    time.sleep(2)  # placeholder

                # Placeholder scorecard (replace with real committee output)
                st.session_state.na_scorecard = {
                    "setup":       72,
                    "business":    81,
                    "capital":     58,
                    "valuation":   65,
                    "incentives":  70,
                    "composite":   71,
                }
                st.session_state.na_committee_done = True
                st.rerun()

        else:
            # Agent output bubbles
            for icon, role, dim, color in AGENTS:
                with st.expander(f"{icon} {role}  ·  {dim}", expanded=False):
                    st.markdown(
                        f"<div style='border-left:3px solid {color};padding-left:12px;"
                        f"color:#64748b;font-style:italic'>"
                        f"{role}'s per-criterion scores and evidence citations for "
                        f"{st.session_state.na_ticker} will appear here once the "
                        f"committee backend is wired (Package 6).</div>",
                        unsafe_allow_html=True,
                    )

            # Dimension score tiles
            sc = st.session_state.na_scorecard
            if sc:
                st.divider()
                st.markdown("**Scorecard summary**")
                dims = [
                    ("Setup",       sc["setup"],       0.20),
                    ("Business",    sc["business"],    0.30),
                    ("Capital",     sc["capital"],     0.20),
                    ("Valuation",   sc["valuation"],   0.15),
                    ("Incentives",  sc["incentives"],  0.15),
                    ("Composite",   sc["composite"],   1.00),
                ]
                score_cols = st.columns(6)
                for col, (name, score, weight) in zip(score_cols, dims):
                    color = _score_color(score)
                    col.markdown(
                        f"<div style='text-align:center;background:{color}18;"
                        f"border:1px solid {color};border-radius:8px;padding:10px 4px'>"
                        f"<div style='font-size:26px;font-weight:700;color:{color}'>{score}</div>"
                        f"<div style='font-size:12px;font-weight:600'>{name}</div>"
                        f"<div style='font-size:11px;color:#94a3b8'>{int(weight*100)}% wt</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            st.divider()
            if st.button("Proceed to Memo →", type="primary"):
                st.session_state.na_step = 6
                st.rerun()

    # ── Step 6: Memo & Decision ────────────────────────────────────────────────
    elif current_step == 6:
        ticker = st.session_state.na_ticker or "—"
        sc     = st.session_state.na_scorecard

        st.subheader("Step 6 · Memo & Decision")

        # Composite score + traffic light
        if sc:
            composite = sc["composite"]
            st.markdown(
                f"<div style='font-size:52px;font-weight:700;margin:4px 0;line-height:1'>"
                f"{composite}</div>"
                f"<div style='font-size:18px;margin-bottom:12px'>"
                f"{_traffic_light(composite)} · {ticker}</div>",
                unsafe_allow_html=True,
            )

            # 5-dimension ribbon
            ribbon_cols = st.columns(5)
            dim_map = [
                ("Setup",      sc["setup"]),
                ("Business",   sc["business"]),
                ("Capital",    sc["capital"]),
                ("Valuation",  sc["valuation"]),
                ("Incentives", sc["incentives"]),
            ]
            for col, (name, score) in zip(ribbon_cols, dim_map):
                color = _score_color(score)
                col.markdown(
                    f"<div style='text-align:center;background:{color}18;"
                    f"border:1px solid {color};border-radius:6px;padding:8px 4px'>"
                    f"<div style='font-size:22px;font-weight:700;color:{color}'>{score}</div>"
                    f"<div style='font-size:12px'>{name}</div></div>",
                    unsafe_allow_html=True,
                )

        st.divider()

        # Memo body
        st.markdown("**Investment Memo — Draft**")
        with st.container(border=True):
            st.markdown(
                f"> **{ticker} — Spinoff Investment Memo**  \n"
                f"> *Placeholder · Generated by Claude Opus 4.7 (not yet wired)*\n\n"
                f"**I. Executive Summary**  \n"
                f"[Thesis summary, composite score, recommendation]\n\n"
                f"**II. Setup Quality** *(score: {sc['setup'] if sc else '—'})*  \n"
                f"[Canonical setups identified, forced-selling dynamics, index mismatch]\n\n"
                f"**III. Business Quality** *(score: {sc['business'] if sc else '—'})*  \n"
                f"[ROIC methodology, growth decomposition, FCF conversion, margin trajectory]\n\n"
                f"**IV. Capital Structure** *(score: {sc['capital'] if sc else '—'})*  \n"
                f"[Leverage, debt quality, maturity wall, hidden liabilities, dis-synergies]\n\n"
                f"**V. Valuation** *(score: {sc['valuation'] if sc else '—'})*  \n"
                f"[EV/EBIT, peer comp table, SOTP if applicable]\n\n"
                f"**VI. Incentives & Catalyst** *(score: {sc['incentives'] if sc else '—'})*  \n"
                f"[Insider ownership, management movement, hard catalysts with dates]\n\n"
                f"**VII. Risk Factors**  \n"
                f"[Top 3 risks with mitigants; any disqualification flags]\n\n"
                f"**VIII. Recommendation**  \n"
                f"[Invest / Watch / Reject with rationale]"
            )

        st.divider()

        # Tendency Coach pre-flight warning
        st.warning(
            "**🧠 Coach's Pre-Flight Check** — "
            "No behavioral history on record yet. After your first decision is logged, "
            "the Tendency Coach will flag patterns like #SetupParalysis or #AnalysisParalysis "
            "here before you decide."
        )

        # Decision buttons
        st.markdown("**Your decision:**")
        d1, d2, d3 = st.columns(3)
        with d1:
            if st.button("🔴 Reject", use_container_width=True):
                st.session_state.dj_open    = True
                st.session_state.dj_verdict = "Reject"
                st.rerun()
        with d2:
            if st.button("👁️ Watch", use_container_width=True):
                st.session_state.dj_open    = True
                st.session_state.dj_verdict = "Watch"
                st.rerun()
        with d3:
            if st.button("✅ Invest", type="primary", use_container_width=True):
                st.session_state.dj_open    = True
                st.session_state.dj_verdict = "Invest"
                st.rerun()

        # Decision journal (required modal)
        if st.session_state.dj_open:
            verdict      = st.session_state.dj_verdict
            verdict_icon = {"Invest": "✅", "Watch": "👁️", "Reject": "🔴"}.get(verdict, "")

            st.divider()
            st.markdown(f"### {verdict_icon} Decision Journal — {verdict}")
            st.caption(
                "Required before the decision is saved. "
                "This data powers the Tendency Coach during quarterly re-runs."
            )

            with st.form("decision_journal"):
                st.markdown(f"**Verdict:** {verdict_icon} {verdict} on **{ticker}**")

                primary_driver = st.selectbox(
                    "Primary driver *",
                    [
                        "Business quality",
                        "Valuation discount",
                        "Hard catalyst identified",
                        "Management alignment",
                        "Forced-selling setup",
                        "Other",
                    ],
                )
                conviction = st.slider(
                    "Conviction level *", 1, 10, 6,
                    help="1 = highly speculative, 10 = highest conviction",
                )
                biggest_risk = st.text_input(
                    "Biggest acknowledged risk *",
                    placeholder="e.g. Debt maturity wall in 18 months could force equity dilution",
                )
                mental_tags = st.multiselect(
                    "Mental state tags (optional)",
                    ["#SetupParalysis", "#AnalysisParalysis", "#RiskAmplifier", "#LossAversion"],
                    help="Tag any biases you recognise in yourself right now.",
                )
                thesis_summary = st.text_area(
                    "Core thesis (1–3 sentences) *",
                    placeholder=(
                        "e.g. Small spinco from large parent; management heavily incentivised; "
                        "ROIC 21%; trading at 9x EV/EBIT vs peer median 15x. "
                        "Hard catalyst: buyback authorisation expected Q3."
                    ),
                    height=100,
                )

                if verdict == "Watch":
                    st.text_input(
                        "Watch reason *",
                        placeholder="e.g. Business quality high but catalyst uncertain — monitor next 10-Q",
                        key="dj_watch_reason",
                    )
                    st.text_input(
                        "Trigger condition to upgrade to Invest",
                        placeholder="e.g. Net Debt/EBITDA drops below 2x, or buyback announced",
                        key="dj_trigger",
                    )

                col_submit, col_cancel = st.columns([1, 1])
                with col_submit:
                    submit_dj = st.form_submit_button(
                        f"Log {verdict} Decision →", type="primary", use_container_width=True
                    )
                with col_cancel:
                    cancel_dj = st.form_submit_button("Cancel", use_container_width=True)

                if cancel_dj:
                    st.session_state.dj_open    = False
                    st.session_state.dj_verdict = None
                    st.rerun()

                if submit_dj:
                    if not biggest_risk.strip() or not thesis_summary.strip():
                        st.error("Biggest acknowledged risk and core thesis are required.")
                    else:
                        # TODO: write decision_logs row to SQLite; update Situation.status
                        st.session_state.dj_open    = False
                        st.session_state.dj_verdict = None
                        st.success(
                            f"{verdict_icon} **{verdict}** logged for **{ticker}** · "
                            f"Conviction {conviction}/10  \n"
                            f"Routing to Company Detail… (not yet wired)"
                        )
                        st.balloons()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: UPDATES
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "updates":
    st.title("🔔 Updates")
    st.caption(
        "New filings and quarterly re-runs for your invested and watched positions. "
        "On each app open, the system polls EDGAR for new 10-Qs, 10-Ks, and 8-Ks."
    )

    st.radio(
        "Filter",
        ["All", "Quarterly", "8-K events", "Pending docs"],
        horizontal=True,
        key="updates_filter",
    )
    st.divider()

    st.info(
        "No updates yet. Once you have invested or watched positions, "
        "new filings will appear here as re-run cards."
    )

    # Canonical update card layout (example)
    with st.expander("Example update card — KVYO quarterly re-run (placeholder)"):
        head_c, badge_c = st.columns([3, 1])
        with head_c:
            st.markdown("**KVYO · Klaviyo Inc.** · Quarterly Re-run")
            st.caption("Triggered by: 10-Q filed 2026-05-12")
        with badge_c:
            st.markdown(
                "<div style='background:#fef3c7;border:1px solid #f59e0b;"
                "border-radius:4px;padding:4px 8px;text-align:center;font-size:12px'>"
                "🟡 Pending review</div>",
                unsafe_allow_html=True,
            )

        score_data = {
            "Dimension": ["Setup", "Business", "Capital", "Valuation", "Incentives", "**Composite**"],
            "Prior":     [72, 81, 58, 65, 70, 71],
            "Current":   [72, 83, 55, 61, 70, 70],
            "Delta":     ["—", "+2", "−3 ⚠️", "−4", "—", "−1"],
        }
        st.dataframe(pd.DataFrame(score_data), hide_index=True, use_container_width=True)
        st.caption(
            "Committee verdict: thesis intact but capital structure weakened "
            "(Net D/EBITDA moved 2.1x → 2.6x per latest 10-Q)."
        )
        st.markdown(
            "**🧠 Tendency Review:** Your original #LossAversion flag on capital risk "
            "has partially materialised — leverage increased. Original biggest risk: "
            "*'Debt maturity wall in 18 months'* — now 15 months away."
        )
        ua, ub = st.columns(2)
        ua.button("View full memo →",    key="ex_view")
        ub.button("Open Company Detail", key="ex_detail")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: COMPANY DETAIL
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "company_detail":
    st.title("🏢 Company Detail")
    st.caption(
        "Per-ticker deep-dive: memos, scorecard, metrics, documents, notes, Q&A. "
        "Click any ticker from Dashboard, Updates, or New Analysis to open this view."
    )

    section = st.radio(
        "Section",
        ["Overview", "Memos", "Scorecard", "Metrics", "Documents", "Notes", "Q&A"],
        horizontal=True,
        key="cd_section",
    )
    st.divider()

    # No ticker selected yet
    st.info(
        "No company selected. Complete a **New Analysis** and click **Invest** or **Watch** "
        "to populate Company Detail."
    )

    # Example layout per section
    if section == "Overview":
        with st.expander("Example Overview — KVYO (placeholder)"):
            hd1, hd2, hd3 = st.columns([2, 1, 1])
            with hd1:
                st.markdown("**KVYO · Klaviyo Inc.** · Spinoff from Shopify (2023)")
                st.caption("Status: 🟢 Invested · Composite: 71 (Review)")
            with hd2:
                st.button("↻ Re-run committee", key="cd_rerun")
            with hd3:
                st.button("⬇ Export memo",      key="cd_export")

            st.markdown(
                "*Thesis: Small-cap SaaS platform spun from large parent; "
                "management heavily incentivised; ROIC 21%; trading at 9x EV/EBIT "
                "vs peer median 15x. Hard catalyst: buyback expected Q3 2026.*"
            )
            oc1, oc2, oc3, oc4, oc5 = st.columns(5)
            for col, name, score in zip(
                [oc1, oc2, oc3, oc4, oc5],
                ["Setup", "Business", "Capital", "Valuation", "Incentives"],
                [72, 81, 58, 65, 70],
            ):
                color = _score_color(score)
                col.markdown(
                    f"<div style='text-align:center;background:{color}18;"
                    f"border:1px solid {color};border-radius:6px;padding:8px'>"
                    f"<div style='font-size:22px;font-weight:700;color:{color}'>{score}</div>"
                    f"<div style='font-size:12px'>{name}</div></div>",
                    unsafe_allow_html=True,
                )

    elif section == "Memos":
        st.info("Versioned memo history will appear here once a company is selected.")

    elif section == "Scorecard":
        st.info(
            "Full 35-criterion scorecard grouped by dimension — "
            "with per-criterion score, evidence citation, and assigning agent — "
            "will appear here once a company is selected."
        )

    elif section == "Metrics":
        st.info(
            "Quarterly charts (Revenue, EBIT margin, ROIC, Net Debt/EBITDA, FCF) "
            "with management guidance overlays will appear here."
        )

    elif section == "Documents":
        st.info("Document library — type, filing date, source, parse status — will appear here.")

    elif section == "Notes":
        st.info("Saved Q&A excerpts and freeform notes with tag filters will appear here.")

    elif section == "Q&A":
        st.info(
            "Full Q&A history for this company — searchable, re-askable — will appear here."
        )
