"""
Meridian-SS — Spinoff & Special-Situations Research Workstation
v3: st.tabs() nav, compact HTML, dark theme
"""

import os
from datetime import datetime
import streamlit as st

st.set_page_config(
    page_title="Meridian-SS",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Constants ──────────────────────────────────────────────────────────────────
SITUATION_TYPES = [
    "Spinoff","Carve-out","Split-off","Recap",
    "Rights offering","Risk arbitrage","Post-bankruptcy",
]
REQUIRED_DOCS = [
    ("Form 10 / 10-12B/A",         "form10"),
    ("Parent 10-K",                  "parent_10k"),
    ("Investor day / deck",          "investor_deck"),
    ("Earnings transcript (last)",   "transcript_1"),
    ("Earnings transcript (prior)",  "transcript_2"),
    ("Newsletter writeup",           "newsletter"),
]
STEPS = [
    (1,"Intake","30 sec"),
    (2,"Documents","2 min"),
    (3,"Ingest","3 min"),
    (4,"Explore","optional"),
    (5,"Committee","4 min"),
    (6,"Memo","review"),
]
AGENTS = [
    ("S","Setup specialist",  "#8b5cf6", 82, "$1.6B cap excludes 3 indices CTL sits in. Forced selling highly likely."),
    ("B","Business quality",  "#3b82f6", 84, "ROIC 18.4% top-quartile. FCF conversion 92%. Growth 6-8%."),
    ("C","Capital structure", "#f59e0b", 65, "Net D/EBITDA 3.1x. Pension liability $340M — material risk."),
    ("V","Valuation",         "#10b981", 80, "EV/EBIT 9x vs peer median 15x. 40% discount."),
    ("D","Devil's advocate",  "#ef4444", None, "Pension transfer materially under-disclosed. ~$90M extra funding implied."),
]

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""<style>
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important;}
.stApp{background-color:#161616!important;}
.main .block-container{padding:0!important;max-width:100%!important;}

/* ── Tabs nav ── */
.stTabs [data-baseweb="tab-list"]{background:#161616;border-bottom:1px solid #2a2a2a;gap:0;padding:0 32px;}
.stTabs [data-baseweb="tab"]{background:transparent!important;border-radius:0!important;color:#94a3b8!important;font-size:14px!important;padding:14px 22px!important;border-bottom:2px solid transparent;}
.stTabs [aria-selected="true"]{color:#f1f5f9!important;border-bottom:2px solid #f1f5f9!important;font-weight:600!important;background:transparent!important;}
.stTabs [data-baseweb="tab-highlight"]{display:none!important;}
.stTabs [data-baseweb="tab-border"]{display:none!important;}
.stTabs [data-testid="stTabsContent"]{background:transparent;padding:0;}

/* ── Text ── */
p,span,div,h1,h2,h3,h4,label{color:#f1f5f9;}
.stMarkdown p{color:#f1f5f9;}

/* ── Metric tiles ── */
.mtile{background:#262626;border-radius:12px;padding:20px 24px;}
.mlabel{color:#94a3b8;font-size:13px;margin-bottom:6px;}
.mval{font-size:36px;font-weight:700;color:#f1f5f9;line-height:1.1;}
.mamber{color:#f59e0b!important;}

/* ── Portfolio ── */
.ptable{background:#262626;border-radius:12px;overflow:hidden;margin-bottom:8px;}
.phdr{display:grid;grid-template-columns:110px 120px 70px 180px 1fr 80px;padding:10px 20px;color:#64748b;font-size:12px;border-bottom:1px solid #333;}
.prow{display:grid;grid-template-columns:110px 120px 70px 180px 1fr 80px;align-items:center;padding:13px 20px;border-bottom:1px solid #222;cursor:pointer;}
.prow:hover{background:#2e2e2e;}
.prow:last-child{border-bottom:none;}
.pticker{font-weight:700;font-size:15px;}
.pmuted{color:#64748b;font-size:13px;}
.dsquares{display:flex;gap:5px;}
.dsq{width:22px;height:22px;border-radius:4px;}
.badge{display:inline-block;padding:3px 10px;border-radius:6px;font-size:12px;font-weight:600;}
.b-intact{background:#14532d40;color:#4ade80;border:1px solid #166534;}
.b-review{background:#451a0340;color:#f59e0b;border:1px solid #92400e;}
.b-reject{background:#450a0a40;color:#f87171;border:1px solid #991b1b;}

/* ── Update cards ── */
.ucard{background:#262626;border-radius:12px;padding:20px 24px;margin-bottom:12px;}

/* ── Step sidebar ── */
.srow{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:8px;margin-bottom:2px;}
.srow.active{background:#2a2a2a;}
.scircle{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0;}
.sc-done{background:#14532d;color:#4ade80;}
.sc-cur{background:#1e3a5f;color:#60a5fa;}
.sc-pend{background:transparent;color:#64748b;border:1px solid #3a3a3a;}
.sname{font-size:14px;color:#f1f5f9;}
.sname-bold{font-weight:700;}
.sname-dim{color:#64748b;}
.stime{font-size:11px;color:#64748b;margin-top:1px;}

/* ── Step card (st.container border wrapper) ── */
[data-testid="stVerticalBlockBorderWrapper"]{background:#262626!important;border-radius:14px!important;border:1px solid #2e2e2e!important;padding:28px 32px!important;}
.stitle{font-size:22px;font-weight:700;margin-bottom:4px;color:#f1f5f9;}
.ssub{color:#94a3b8;font-size:14px;margin-bottom:20px;}

/* ── Doc method cards ── */
.mcard{background:#1e1e1e;border:1px solid #2e2e2e;border-radius:10px;padding:16px;}
.mcardtitle{font-size:14px;font-weight:600;margin-bottom:4px;}
.mcarddesc{color:#94a3b8;font-size:12px;margin-bottom:12px;}

/* ── Doc tags ── */
.tag-edgar{background:#14532d40;color:#4ade80;border:1px solid #166534;font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600;}
.tag-up{background:#1e3a8a40;color:#60a5fa;border:1px solid #1d4ed8;font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600;}
.tag-pend{background:#451a0340;color:#f59e0b;border:1px solid #92400e;font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600;}

/* ── Ingest ── */
.irow{display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid #2a2a2a;font-size:14px;}
.ick{color:#4ade80;margin-right:10px;}
.itime{color:#64748b;font-size:13px;}
.ierr{background:#2d0f0f;border:1px solid #5a1f1f;border-radius:8px;padding:12px 16px;color:#f87171;font-size:14px;margin:6px 0;}

/* ── Chat ── */
.chatq{display:flex;align-items:center;gap:12px;background:#2a2a2a;border-radius:10px;padding:12px 16px;margin-bottom:8px;}
.chata{background:#1a2744;border:1px solid #243554;border-radius:10px;padding:16px;margin-bottom:6px;}
.av{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0;}
.av-m{background:#1d4ed8;color:#bfdbfe;}
.av-u{background:#333;color:#94a3b8;border:1px solid #444;}
.ctag{display:inline-block;background:#2a2a2a;border:1px solid #3a3a3a;border-radius:5px;padding:2px 8px;font-size:11px;color:#94a3b8;margin:3px 3px 0 0;}

/* ── Agent rows ── */
.agrow{display:flex;align-items:flex-start;gap:12px;background:#2a2a2a;border-radius:10px;padding:14px 16px;margin-bottom:8px;}
.agav{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0;}

/* ── Score tiles ── */
.stile{background:#2a2a2a;border-radius:10px;padding:16px 10px;text-align:center;}
.slabel{color:#94a3b8;font-size:12px;margin-bottom:6px;}
.snum{font-size:28px;font-weight:700;line-height:1.1;}
.sbar-t{height:3px;background:#3a3a3a;border-radius:2px;margin-top:10px;}
.sbar-f{height:3px;border-radius:2px;}

/* ── Company detail nav ── */
.cdnav{display:flex;align-items:center;justify-content:space-between;padding:9px 14px;border-radius:8px;font-size:14px;color:#94a3b8;cursor:pointer;margin-bottom:2px;}
.cdnav.active{background:#2a2a2a;color:#f1f5f9;font-weight:600;}
.cdcnt{font-size:12px;color:#64748b;}

/* ── Buttons ── */
.stButton>button{background:#2a2a2a!important;border:1px solid #3a3a3a!important;color:#f1f5f9!important;border-radius:8px!important;font-size:13px!important;transition:background 0.1s!important;}
.stButton>button:hover{background:#333!important;border-color:#555!important;}
[data-testid="baseButton-primary"]{background:#f1f5f9!important;color:#161616!important;font-weight:600!important;border:none!important;}
[data-testid="baseButton-primary"]:hover{background:#e2e8f0!important;}

/* ── Inputs ── */
.stTextInput>div>div{background:#2a2a2a!important;border:1px solid #3a3a3a!important;border-radius:8px!important;}
.stTextInput input{color:#f1f5f9!important;}
.stTextArea textarea{background:#2a2a2a!important;border:1px solid #3a3a3a!important;color:#f1f5f9!important;border-radius:8px!important;}
.stSelectbox>div>div{background:#2a2a2a!important;border:1px solid #3a3a3a!important;border-radius:8px!important;}
.stSelectbox span{color:#f1f5f9!important;}
[data-baseweb="select"]{background:#2a2a2a!important;}
[data-baseweb="popover"] li{background:#2a2a2a!important;color:#f1f5f9!important;}
[data-testid="stForm"]{background:transparent!important;border:none!important;padding:0!important;}
label{color:#94a3b8!important;font-size:13px!important;}
[data-testid="stAlertContainer"]{border-radius:8px!important;}
[data-testid="stAlertContainer"] p{color:#f59e0b!important;}
hr{border-color:#2a2a2a!important;}
[data-testid="column"]{padding:0 6px!important;}
.stMultiSelect>div>div{background:#2a2a2a!important;border:1px solid #3a3a3a!important;border-radius:8px!important;}
</style>""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "na_step":1,"na_ticker":"","na_parent_ticker":"","na_sit_type":"Spinoff",
        "na_seed_url":"","na_step1_done":False,
        "na_validated":False,"na_cik":"","na_entity_name":"","na_state":"","na_sic_desc":"",
        "na_doc_states":{k:"—" for _,k in REQUIRED_DOCS},
        "na_step2_done":False,"na_ingest_done":False,"na_qa_history":[],
        "na_committee_done":False,"na_scorecard":None,
        "dj_open":False,"dj_verdict":None,"cd_section":"Overview",
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v
_init()

# ── Helpers ────────────────────────────────────────────────────────────────────
def sc(s):
    if not isinstance(s,int): return "#64748b"
    return "#22c55e" if s>=75 else "#f59e0b" if s>=55 else "#ef4444"

def _docs_resolved():
    return sum(1 for v in st.session_state.na_doc_states.values() if v in ("fetched","uploaded","url"))

@st.cache_data(ttl=3600)
def _edgar_lookup(ticker: str):
    import urllib.request, json
    ticker = ticker.upper().strip()
    hdrs = {"User-Agent": "meridian-ss research@meridian-ss.app"}
    try:
        req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers=hdrs)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
    except Exception:
        return None
    match = next((v for v in data.values() if v.get("ticker","").upper() == ticker), None)
    if not match:
        return None
    cik = str(match["cik_str"])
    try:
        req2 = urllib.request.Request(f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json", headers=hdrs)
        with urllib.request.urlopen(req2, timeout=12) as r2:
            sub = json.loads(r2.read())
        return {"cik": cik, "name": sub.get("name", match["title"]),
                "sic_desc": sub.get("sicDescription",""), "state": sub.get("stateOfIncorporation","")}
    except Exception:
        return {"cik": cik, "name": match["title"], "sic_desc": "", "state": ""}

PAD = "padding:28px 40px;"

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_d, tab_na, tab_u, tab_cd = st.tabs([
    "⊞  Dashboard",
    "+  New analysis",
    "✉  Updates · 3",
    "⊟  Company detail",
])

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_d:
    st.markdown(f'<div style="{PAD}">', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    for col,label,val,amber in [(c1,"Invested","7",False),(c2,"Watchlist","14",False),(c3,"Pending review","3",True),(c4,"Avg score","71",False)]:
        vcls = "mval mamber" if amber else "mval"
        col.markdown(f'<div class="mtile"><div class="mlabel">{label}</div><div class="{vcls}">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("**Portfolio**")

    PORTFOLIO = [
        ("LUMN","Spinoff",78,[72,81,64,78,75],"intact","Q1 '26"),
        ("VNTR","Spinoff",58,[45,62,45,60,48],"review","Q1 '26"),
        ("STHO","Spinoff",82,[80,85,78,83,84],"intact","Q4 '25"),
        ("LTRPA","Tracking",74,[70,78,68,75,79],"intact","Q1 '26"),
    ]
    rows = ""
    for ticker,typ,score,dims,status,qtr in PORTFOLIO:
        sqs = "".join(f'<div class="dsq" style="background:{sc(d)}"></div>' for d in dims)
        rows += f'<div class="prow"><span class="pticker">{ticker}</span><span class="pmuted">{typ}</span><span style="font-weight:700">{score}</span><div class="dsquares">{sqs}</div><span class="badge b-{status}">{status.capitalize()}</span><span class="pmuted">{qtr}</span></div>'
    st.markdown(f'<div class="ptable"><div class="phdr"><span>Ticker</span><span>Type</span><span>Score</span><span>Dimensions (S/B/C/V/I)</span><span>Status</span><span></span></div>{rows}</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b;font-size:12px;margin-top:6px">Dimensions key: S Setup · B Business · C Capital · V Valuation · I Incentives. Click any row to open company detail.</p>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    pl,pr = st.columns(2)
    pl.markdown("**Pending review**")
    pr.markdown('<p style="text-align:right;color:#64748b;font-size:13px">3 updates · click to go to the inbox</p>', unsafe_allow_html=True)
    st.markdown('<div class="ucard" style="display:flex;align-items:center;justify-content:space-between"><div style="display:flex;align-items:center;gap:12px"><span style="font-size:18px;color:#64748b">📄</span><div><div style="font-weight:600;font-size:14px">VNTR Q1 2026 quarterly update ready</div><div style="color:#64748b;font-size:13px">Committee flags 2 missed promises. + 2 more pending.</div></div></div><span style="color:#64748b">→</span></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# NEW ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_na:
    ticker_d  = st.session_state.na_ticker or "New situation"
    parent_d  = st.session_state.na_parent_ticker
    ename_d   = st.session_state.na_entity_name
    base_d    = f"{ticker_d} · {ename_d}" if ename_d else ticker_d
    title_d   = f"{base_d} spinoff from {parent_d}" if parent_d else base_d

    st.markdown(f'<div style="padding:24px 40px 0 40px"><div style="font-size:22px;font-weight:700">{title_d}</div><div style="color:#f59e0b;font-size:13px;margin-top:4px">ⓘ Analysis is marked complete only after all 6 steps and your final invest / watch / reject decision.</div></div><div style="height:16px"></div>', unsafe_allow_html=True)

    left, right = st.columns([1, 3], gap="medium")

    # ── Step list ──────────────────────────────────────────────────────────────
    with left:
        st.markdown('<div style="padding:0 8px 0 40px">', unsafe_allow_html=True)
        cur = st.session_state.na_step
        done_map = {
            1: st.session_state.na_step1_done,
            2: st.session_state.na_step2_done,
            3: st.session_state.na_ingest_done,
            4: len(st.session_state.na_qa_history) > 0,
            5: st.session_state.na_committee_done,
            6: False,
        }
        for n, label, est in STEPS:
            is_done = done_map.get(n, False)
            is_cur  = (n == cur)
            if is_done:
                circle = '<div class="scircle sc-done">✓</div>'
                ncls   = "sname"
            elif is_cur:
                circle = f'<div class="scircle sc-cur">{n}</div>'
                ncls   = "sname sname-bold"
            else:
                circle = f'<div class="scircle sc-pend">{n}</div>'
                ncls   = "sname sname-dim"
            row_cls = "active" if is_cur else ""
            st.markdown(f'<div class="srow {row_cls}">{circle}<div><div class="{ncls}">{label}</div><div class="stime">{est}</div></div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Step content ───────────────────────────────────────────────────────────
    with right:
        with st.container(border=True):

            # STEP 1
            if cur == 1:
                st.markdown('<div class="stitle">Step 1 · Intake</div><div class="ssub">Enter the spinoff ticker — we\'ll validate it on SEC EDGAR and pull the entity record.</div>', unsafe_allow_html=True)

                fc1, fc2 = st.columns(2)
                with fc1:
                    ticker_in = st.text_input("Spinoff ticker *", value=st.session_state.na_ticker, placeholder="LUMN")
                with fc2:
                    sit_in = st.selectbox("Situation type *", SITUATION_TYPES, index=SITUATION_TYPES.index(st.session_state.na_sit_type))
                parent_in = st.text_input("Parent ticker", value=st.session_state.na_parent_ticker, placeholder="CTL — auto-detected when possible")
                seed_in   = st.text_input("Seed URL (optional)", value=st.session_state.na_seed_url, placeholder="https://newsletter.com/writeup…")

                # Entity card — shown after a successful validation
                if st.session_state.na_validated:
                    st.markdown(
                        f'<div style="background:#0f2d1f;border:1px solid #166534;border-radius:10px;padding:16px 20px;margin:14px 0">'
                        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">'
                        f'<span style="color:#4ade80;font-size:15px">✓</span>'
                        f'<span style="font-weight:700;font-size:14px;color:#4ade80">Validated on SEC EDGAR</span>'
                        f'</div>'
                        f'<div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:14px">'
                        f'<div><div style="color:#64748b;font-size:11px;margin-bottom:3px">COMPANY NAME</div><div style="font-size:14px;font-weight:600">{st.session_state.na_entity_name}</div></div>'
                        f'<div><div style="color:#64748b;font-size:11px;margin-bottom:3px">CIK</div><div style="font-size:14px;font-weight:600">{st.session_state.na_cik}</div></div>'
                        f'<div><div style="color:#64748b;font-size:11px;margin-bottom:3px">STATE</div><div style="font-size:14px;font-weight:600">{st.session_state.na_state or "—"}</div></div>'
                        f'<div><div style="color:#64748b;font-size:11px;margin-bottom:3px">SECTOR</div><div style="font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{st.session_state.na_sic_desc or "—"}</div></div>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                _, bc = st.columns([2, 1])
                with bc:
                    already_ok = (st.session_state.na_validated
                                  and ticker_in.strip().upper() == st.session_state.na_ticker)
                    btn_label = "Continue →" if already_ok else "Validate on EDGAR →"
                    if st.button(btn_label, type="primary", use_container_width=True, key="s1_go"):
                        if not ticker_in.strip():
                            st.error("Ticker is required.")
                        elif already_ok:
                            st.session_state.na_sit_type      = sit_in
                            st.session_state.na_parent_ticker = parent_in.strip().upper()
                            st.session_state.na_seed_url      = seed_in.strip()
                            st.session_state.na_step          = 2
                            st.rerun()
                        else:
                            with st.spinner(f"Looking up {ticker_in.upper()} on EDGAR…"):
                                entity = _edgar_lookup(ticker_in.strip())
                            if entity is None:
                                st.error(f"**{ticker_in.upper()}** not found on SEC EDGAR. Check the ticker spelling — EDGAR uses the exchange ticker (e.g. `LUMN` not `LU`).")
                            else:
                                st.session_state.na_ticker        = ticker_in.strip().upper()
                                st.session_state.na_sit_type      = sit_in
                                st.session_state.na_parent_ticker = parent_in.strip().upper()
                                st.session_state.na_seed_url      = seed_in.strip()
                                st.session_state.na_cik           = entity["cik"]
                                st.session_state.na_entity_name   = entity["name"]
                                st.session_state.na_state         = entity.get("state","")
                                st.session_state.na_sic_desc      = entity.get("sic_desc","")
                                st.session_state.na_validated     = True
                                st.session_state.na_step1_done    = True
                                st.session_state.na_step          = 2
                                st.rerun()

            # STEP 2
            elif cur == 2:
                resolved = _docs_resolved()
                st.markdown('<div class="stitle">Step 2 · Documents</div><div class="ssub">Add documents three ways: EDGAR auto-fetch, PDF upload, or URL paste.</div>', unsafe_allow_html=True)
                mc1,mc2,mc3 = st.columns(3)
                with mc1:
                    st.markdown('<div class="mcard"><div class="mcardtitle">⬇ EDGAR fetch</div><div class="mcarddesc">Form 10, 10-K, 10-Q, 8-K, DEF 14A</div></div>', unsafe_allow_html=True)
                    if st.button("Fetch ↗", key="edgar_fetch", use_container_width=True):
                        st.session_state.na_doc_states["form10"]     = "fetched"
                        st.session_state.na_doc_states["parent_10k"] = "fetched"
                        st.toast("EDGAR fetch complete (placeholder)")
                        st.rerun()
                with mc2:
                    st.markdown('<div class="mcard"><div class="mcardtitle">⬆ Upload PDF</div><div class="mcarddesc">Decks, paywalled writeups</div></div>', unsafe_allow_html=True)
                    up = st.file_uploader("", accept_multiple_files=True, type=["pdf"], key="doc_upload", label_visibility="collapsed")
                    if up:
                        st.session_state.na_doc_states["investor_deck"] = "uploaded"
                        st.rerun()
                with mc3:
                    st.markdown('<div class="mcard"><div class="mcardtitle">🔗 Paste URL</div><div class="mcarddesc">Newsletters, transcripts, articles</div></div>', unsafe_allow_html=True)
                    purl = st.text_input("", key="paste_url", placeholder="https://...", label_visibility="collapsed")
                    if purl and st.button("Add", key="add_url"):
                        st.session_state.na_doc_states["newsletter"] = "url"
                        st.rerun()

                st.markdown(f"<div style='height:16px'></div><div style='font-weight:600;margin-bottom:10px'>Checklist · {resolved} of {len(REQUIRED_DOCS)} resolved</div>", unsafe_allow_html=True)
                for lbl2, key2 in REQUIRED_DOCS:
                    state = st.session_state.na_doc_states[key2]
                    if state == "fetched":
                        st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #222"><div style="display:flex;align-items:center;gap:10px"><span style="color:#4ade80">✓</span><span style="font-size:14px">{lbl2}</span></div><span class="tag-edgar">EDGAR</span></div>', unsafe_allow_html=True)
                    elif state == "uploaded":
                        st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #222"><div style="display:flex;align-items:center;gap:10px"><span style="color:#4ade80">✓</span><span style="font-size:14px">{lbl2}</span></div><span class="tag-up">Uploaded</span></div>', unsafe_allow_html=True)
                    elif state == "url":
                        st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #222"><div style="display:flex;align-items:center;gap:10px"><span style="color:#4ade80">✓</span><span style="font-size:14px">{lbl2}</span></div><span class="tag-up">URL</span></div>', unsafe_allow_html=True)
                    else:
                        rl,rb = st.columns([3,2])
                        rl.markdown(f'<div style="display:flex;align-items:center;gap:10px;padding:6px 0"><span style="color:#64748b">☐</span><span style="font-size:14px">{lbl2}</span></div>', unsafe_allow_html=True)
                        b1,b2,b3 = rb.columns(3)
                        b1.button("Upload", key=f"ul_{key2}", use_container_width=True)
                        b2.button("URL",    key=f"ur_{key2}", use_container_width=True)
                        b3.button("Skip",   key=f"sk_{key2}", use_container_width=True)

                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                if resolved >= 4:
                    _,pb = st.columns([2,1])
                    with pb:
                        if st.button("Index documents →", type="primary", use_container_width=True):
                            st.session_state.na_step2_done = True
                            st.session_state.na_step       = 3
                            st.rerun()
                else:
                    st.warning(f"{resolved} / {len(REQUIRED_DOCS)} resolved — need at least 4 to continue.")

            # STEP 3
            elif cur == 3:
                st.markdown('<div class="stitle">Step 3 · Ingest</div><div class="ssub">LlamaParse + markdown chunking + hybrid retrieval. Failures highlighted in red.</div>', unsafe_allow_html=True)
                if not st.session_state.na_ingest_done:
                    if st.button("▶  Run ingestion", type="primary"):
                        import time
                        with st.spinner("Running ingestion pipeline…"):
                            time.sleep(1)
                        st.session_state.na_ingest_done = True
                        st.rerun()
                else:
                    for lbl3, ok, timing in [
                        ("Parsing PDFs · 5 of 5 · 1,847 pages", True,  "42s"),
                        ("Markdown chunking · 3,201 chunks",     True,  "18s"),
                        ("Hybrid index · BM25 + embeddings",     True,  "31s"),
                        ("Newsletter URL · 403 forbidden",       False, None),
                        ("Pre-extracted financials",              True,  "22s"),
                    ]:
                        if ok:
                            st.markdown(f'<div class="irow"><div><span class="ick">✓</span>{lbl3}</div><span class="itime">{timing}</span></div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="ierr"><div style="font-weight:600">⚠ Newsletter URL · 403 forbidden</div><div style="color:#f8717180;font-size:12px;margin-top:2px">Paywalled. Retry or upload PDF.</div></div>', unsafe_allow_html=True)
                            _,ec1,ec2,_2 = st.columns([3,1,1,2])
                            ec1.button("Retry",  key="ir")
                            ec2.button("Upload", key="iu")
                    _,pb = st.columns([2,1])
                    with pb:
                        if st.button("Explore the corpus →", type="primary", use_container_width=True):
                            st.session_state.na_step = 4
                            st.rerun()

            # STEP 4
            elif cur == 4:
                st.markdown('<div class="stitle">Step 4 · Explore</div><div class="ssub">Grounded Q&A with save-to-notes and tags.</div>', unsafe_allow_html=True)
                for i, entry in enumerate(st.session_state.na_qa_history):
                    st.markdown(f'<div class="chatq"><div class="av av-u">👤</div><span style="font-size:14px">{entry["q"]}</span></div><div class="chata"><div style="display:flex;align-items:flex-start;gap:10px"><div class="av av-m">M</div><div><div style="font-size:14px;line-height:1.6;margin-bottom:8px">{entry["a"]}</div><div><span class="ctag">Form 10 p. 87</span><span class="ctag">Q1 transcript</span><span class="ctag">10-K note 14</span></div></div></div></div>', unsafe_allow_html=True)
                    sa,ta,da,_ = st.columns([1,1,1,3])
                    sa.button("🔖 Save",       key=f"sv_{i}")
                    ta.button("🏷 #pension",   key=f"tg_{i}")
                    da.button("🔍 Dig deeper", key=f"dg_{i}")
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                qi,rb = st.columns([4,1])
                with qi: q = st.text_input("", placeholder="Ask another question...", key="qa_input", label_visibility="collapsed")
                with rb:
                    if st.button("Run committee →", type="primary", use_container_width=True):
                        st.session_state.na_step = 5
                        st.rerun()
                if q and st.button("Ask", key="ask_q"):
                    st.session_state.na_qa_history.append({"q":q,"a":"$1.2B net debt (3.1x EBITDA). Form 10 p. 87: $340M pension liability. CFO declined to quantify funding shortfall on Q1 call.","saved":False})
                    st.rerun()

            # STEP 5
            elif cur == 5:
                st.markdown('<div class="stitle">Step 5 · Committee</div><div class="ssub">5 agents debate the Greenblatt scorecard.</div>', unsafe_allow_html=True)
                if not st.session_state.na_committee_done:
                    if st.button("▶  Convene committee", type="primary"):
                        import time
                        with st.spinner("Agents debating…"):
                            time.sleep(2)
                        st.session_state.na_scorecard = {"setup":82,"business":84,"capital":65,"valuation":80,"incentives":78,"composite":78}
                        st.session_state.na_committee_done = True
                        st.rerun()
                else:
                    for letter,role,color,score,summary in AGENTS:
                        s_str = f" · {score}" if score else ""
                        st.markdown(f'<div class="agrow"><div class="agav" style="background:{color}30;color:{color}">{letter}</div><div><div style="font-weight:600;font-size:14px">{role}{s_str}</div><div style="color:#94a3b8;font-size:13px;margin-top:2px">{summary}</div></div></div>', unsafe_allow_html=True)
                    st.markdown('<p style="color:#64748b;font-size:13px;margin-top:4px">+ Valuation and Incentives agents weighing in…</p>', unsafe_allow_html=True)
                    _,pb = st.columns([2,1])
                    with pb:
                        if st.button("View memo →", type="primary", use_container_width=True):
                            st.session_state.na_step = 6
                            st.rerun()

            # STEP 6
            elif cur == 6:
                sc_d = st.session_state.na_scorecard
                comp = sc_d["composite"] if sc_d else "—"
                st.markdown(f'<div class="stitle">Step 6 · Memo and decision</div><div class="ssub">Composite {comp}/100. Click Approve / Watch / Reject.</div>', unsafe_allow_html=True)
                if sc_d:
                    st.markdown('<div style="background:#2a2a2a;border-radius:10px;padding:16px;margin-bottom:16px"><div style="font-weight:600;font-size:14px;margin-bottom:8px">Recommendation</div><div style="color:#94a3b8;font-size:14px;line-height:1.6">4 of 5 agents approve. Strong setup, strong business quality, attractive valuation. Material concern: pension liability disclosure incomplete. Suggest entry sized 5% pending May 22 footnote.</div></div>', unsafe_allow_html=True)
                    dims = [("Setup",sc_d["setup"]),("Business",sc_d["business"]),("Capital",sc_d["capital"]),("Valuation",sc_d["valuation"]),("Incentives",sc_d["incentives"])]
                    dcols = st.columns(5)
                    for col,(name,score) in zip(dcols,dims):
                        c = sc(score)
                        col.markdown(f'<div class="stile"><div class="slabel">{name}</div><div class="snum" style="color:{c}">{score}</div><div class="sbar-t"><div class="sbar-f" style="width:{score}%;background:{c}"></div></div></div>', unsafe_allow_html=True)
                    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                if not st.session_state.dj_open:
                    d1,d2,d3 = st.columns(3)
                    with d1:
                        if st.button("Reject", use_container_width=True):
                            st.session_state.dj_open=True; st.session_state.dj_verdict="Reject"; st.rerun()
                    with d2:
                        if st.button("Watch", use_container_width=True):
                            st.session_state.dj_open=True; st.session_state.dj_verdict="Watch"; st.rerun()
                    with d3:
                        if st.button("Invest", type="primary", use_container_width=True):
                            st.session_state.dj_open=True; st.session_state.dj_verdict="Invest"; st.rerun()
                else:
                    verdict = st.session_state.dj_verdict
                    icon = {"Invest":"✅","Watch":"👁","Reject":"🔴"}.get(verdict,"")
                    st.markdown(f"<hr><div style='font-size:16px;font-weight:700;margin-bottom:12px'>{icon} Decision Journal — {verdict}</div>", unsafe_allow_html=True)
                    with st.form("dj_form"):
                        pd_sel = st.selectbox("Primary driver *",["Business quality","Valuation discount","Hard catalyst","Management alignment","Forced-selling setup","Other"])
                        conv   = st.slider("Conviction *",1,10,6)
                        risk   = st.text_input("Biggest acknowledged risk *", placeholder="e.g. Debt maturity wall in 18 months")
                        thesis = st.text_area("Core thesis (1–3 sentences) *", placeholder="e.g. Small-cap spinoff…", height=80)
                        sc1,sc2 = st.columns(2)
                        with sc1: sub_dj = st.form_submit_button(f"Log {verdict} →", type="primary", use_container_width=True)
                        with sc2: cancel = st.form_submit_button("Cancel", use_container_width=True)
                        if cancel:
                            st.session_state.dj_open=False; st.session_state.dj_verdict=None; st.rerun()
                        if sub_dj:
                            if not risk.strip() or not thesis.strip():
                                st.error("Risk and thesis are required.")
                            else:
                                st.session_state.dj_open=False; st.session_state.dj_verdict=None
                                st.success(f"{icon} **{verdict}** logged · Conviction {conv}/10")
                                st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# UPDATES
# ══════════════════════════════════════════════════════════════════════════════
with tab_u:
    st.markdown(f'<div style="{PAD}">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;gap:8px;margin-bottom:24px"><span style="background:#f1f5f9;color:#161616;font-weight:600;padding:5px 14px;border-radius:20px;font-size:13px">All · 3</span><span style="color:#94a3b8;padding:5px 14px;font-size:13px">Quarterly · 1</span><span style="color:#94a3b8;padding:5px 14px;font-size:13px">8-K · 1</span><span style="color:#94a3b8;padding:5px 14px;font-size:13px">Pending docs · 1</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="ucard"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px"><div style="display:flex;align-items:center;gap:10px"><span style="font-size:18px;color:#64748b">📄</span><div><div style="font-weight:700;font-size:15px">VNTR Q1 2026 quarterly update</div><div style="color:#64748b;font-size:13px">10-Q filed May 9 · click to open VNTR detail</div></div></div><span class="badge b-review">Review</span></div><div style="font-weight:600;font-size:13px;margin-bottom:10px">5-dimension score change vs. v2</div></div>', unsafe_allow_html=True)
    dcols = st.columns(5)
    for col,(name,val,delta) in zip(dcols,[("Setup","Played",None),("Business","62",-8),("Capital","45",-15),("Valuation","60",-5),("Incentives","48",-12)]):
        dstr = f' <span style="color:#f87171;font-size:12px">{delta}</span>' if delta else ""
        col.markdown(f'<div class="stile"><div class="slabel">{name}</div><div style="font-size:20px;font-weight:700;line-height:1.2">{val}{dstr}</div></div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b;font-size:13px;margin:10px 0 20px">Memo v3 ready · click anywhere on this card to open VNTR detail</p>', unsafe_allow_html=True)

    st.markdown('<div class="ucard"><div style="display:flex;align-items:flex-start;gap:12px"><span style="font-size:20px">🔔</span><div><div style="font-weight:700;font-size:15px">LUMN · 8-K filed May 18, 2026</div><div style="color:#94a3b8;font-size:13px;margin:4px 0 12px">Material agreement amendment. Add the 8-K and any related news, then re-run the committee.</div></div></div></div>', unsafe_allow_html=True)
    ba,bb,_ = st.columns([1,2,3])
    ba.button("Dismiss",                    key="dis_8k")
    bb.button("Add documents and re-run ↗", key="rer_8k")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="ucard"><div style="display:flex;align-items:flex-start;gap:12px"><span style="font-size:20px">⏱</span><div><div style="font-weight:700;font-size:15px">LUMN · pension footnote expected today</div><div style="color:#94a3b8;font-size:13px;margin:4px 0 12px">You flagged this missing on Apr 22. Has it been disclosed?</div></div></div></div>', unsafe_allow_html=True)
    p1,p2,p3,_ = st.columns([1,1.5,1.5,2])
    p1.button("Still missing", key="stil")
    p2.button("Check EDGAR ↗", key="chk")
    p3.button("Upload now ↗",  key="upn")

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COMPANY DETAIL
# ══════════════════════════════════════════════════════════════════════════════
with tab_cd:
    st.markdown(f'<div style="{PAD}">', unsafe_allow_html=True)
    hl,hr = st.columns([3,1])
    with hl:
        st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:4px"><span style="font-size:26px;font-weight:700">VNTR · Vontier</span><span class="badge b-review">Invested · review</span></div><div style="color:#64748b;font-size:14px">Spinoff from Fortive (FTV) · Composite score 58 / 100</div>', unsafe_allow_html=True)
    with hr:
        ra,rb = st.columns(2)
        ra.button("↻ Re-run", key="cd_r")
        rb.button("⬇ Export", key="cd_e")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    nav_c, content_c = st.columns([1,3], gap="medium")

    CD_SECTIONS = [("Overview",None,"👁"),("Memos",3,"📄"),("Scorecard",None,"📊"),("Metrics",None,"📈"),("Promises",5,"✓"),("Documents",18,"📁"),("Notes",12,"🔖"),("Q&A",27,"💬")]

    with nav_c:
        cur_sec = st.session_state.cd_section
        for name,cnt,icon in CD_SECTIONS:
            is_a = (name == cur_sec)
            cls  = "active" if is_a else ""
            cnt_html = f'<span class="cdcnt">{cnt}</span>' if cnt else ""
            st.markdown(f'<div class="cdnav {cls}"><span>{icon} {name}</span>{cnt_html}</div>', unsafe_allow_html=True)
            if st.button(name, key=f"cdn_{name}", use_container_width=True):
                st.session_state.cd_section = name
                st.rerun()

    with content_c:
        sec = st.session_state.cd_section
        if sec == "Overview":
            st.markdown("<div style='font-weight:600;font-size:16px;margin-bottom:14px'>Scorecard summary</div>", unsafe_allow_html=True)
            dims = [("Setup","Played"),("Business",62),("Capital",45),("Valuation",60),("Incentives",48)]
            dcols = st.columns(5)
            for col,(name,val) in zip(dcols,dims):
                if isinstance(val,int):
                    c   = sc(val)
                    bar = f'<div class="sbar-t"><div class="sbar-f" style="width:{val}%;background:{c}"></div></div>'
                    num = f'<div class="snum" style="color:{c}">{val}</div>'
                else:
                    c   = "#64748b"
                    bar = f'<div class="sbar-t"><div class="sbar-f" style="width:100%;background:{c}"></div></div>'
                    num = f'<div class="snum" style="color:{c}">{val}</div>'
                col.markdown(f'<div class="stile"><div class="slabel">{name}</div>{num}{bar}</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            st.markdown("<div style='font-weight:600;font-size:16px;margin-bottom:12px'>Business quality detail</div>", unsafe_allow_html=True)
            st.markdown('<div style="background:#2a2a2a;border-radius:10px;padding:20px 24px"><div style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px"><div><div style="color:#94a3b8;font-size:12px;margin-bottom:4px">ROIC</div><div style="font-size:20px;font-weight:700">15.8%</div></div><div><div style="color:#94a3b8;font-size:12px;margin-bottom:4px">Growth</div><div style="font-size:20px;font-weight:700">2.1%</div></div><div><div style="color:#94a3b8;font-size:12px;margin-bottom:4px">FCF conv.</div><div style="font-size:20px;font-weight:700">78%</div></div><div><div style="color:#94a3b8;font-size:12px;margin-bottom:4px">Margin</div><div style="font-size:18px;font-weight:700;color:#f59e0b">Deteriorating</div></div><div><div style="color:#94a3b8;font-size:12px;margin-bottom:4px">Durability</div><div style="font-size:20px;font-weight:700">3 / 5</div></div></div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:#64748b;padding:24px 0">{sec} will appear here once a company is fully analysed.</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
