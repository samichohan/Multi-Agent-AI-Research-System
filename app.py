"""
Streamlit UI — Multi-Agent Research System (Black Theme, Production)
-------------------------------------------------------------------------------
Run with:
    streamlit run streamlit_app.py

Requirements (add to requirements.txt):
    streamlit
    fpdf2
    markdown
"""

import io
import re
import html
import queue
import textwrap
import threading
import time
from contextlib import redirect_stdout

import streamlit as st

from pipeline import run_search_agent

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import markdown as md_lib
    MARKDOWN_LIB = True
except ImportError:
    MARKDOWN_LIB = False


def md(html_str: str):
    """Render HTML safely, always dedented so Streamlit's markdown parser
    never mistakes indented lines for a code block."""
    st.markdown(textwrap.dedent(html_str), unsafe_allow_html=True)


# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Research Intelligence | Multi-Agent System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# THEME / CSS  —  pure black + blue accent
# =============================================================================
md(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #05070a !important; color: #f3f4f6; }
    #MainMenu, footer, header { visibility: hidden; }

    .hero {
        padding: 40px 42px;
        border-radius: 20px;
        background: linear-gradient(120deg, #0a0e18 0%, #0d1b3d 60%, #10254f 100%);
        border: 1px solid rgba(59,130,246,0.25);
        margin-bottom: 22px;
    }
    .hero-tag {
        color: #60a5fa; font-size: 12.5px; font-weight: 700; letter-spacing: 2.5px;
        text-transform: uppercase; margin: 0 0 10px 0;
    }
    .hero-title {
        font-size: 54px !important;
        font-weight: 900 !important;
        letter-spacing: -1.2px;
        margin: 0;
        color: #ffffff !important;
        line-height: 1.1;
        white-space: nowrap;
    }
    .hero-title span { color: #60a5fa !important; }
    .hero-sub { color: #9fb3d6; font-size: 16.5px; margin-top: 14px; font-weight: 500; }
    .hero-sub2 { color: #6b83ad; font-size: 13.5px; margin-top: 4px; font-weight: 600; letter-spacing: 0.4px; }

    .card {
        background: #0b0e14;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }
    .card h4 {
        margin-top: 0; color: #dbe4f7; font-weight: 800; font-size: 13.5px;
        letter-spacing: 0.6px; text-transform: uppercase;
    }

    /* Pipeline panel */
    .pipe-step { display:flex; align-items:flex-start; gap:12px; padding:8px 0 18px 0; position:relative; }
    .pipe-step:not(:last-child)::before { content:""; position:absolute; left:14px; top:32px; width:2px; height:calc(100% - 18px); background:rgba(255,255,255,0.08); }
    .pipe-dot { min-width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:800; z-index:1; flex-shrink:0; }
    .dot-pending { background:#12151d; color:#5b6472; border:1px solid rgba(255,255,255,0.08); }
    .dot-running { background:#0f2748; color:#60a5fa; border:1px solid #3b82f6; }
    .dot-done { background:#0f2a1a; color:#22c55e; border:1px solid #22c55e; }
    .dot-error { background:#2a1212; color:#f87171; border:1px solid #f87171; }
    .pipe-label { font-weight:700; font-size:14px; color:#f3f4f6; margin:0; }
    .pipe-status { font-size:11.5px; margin-top:2px; font-weight:500; }
    .status-pending { color:#5b6472; }
    .status-running { color:#60a5fa; }
    .status-done { color:#22c55e; }
    .status-error { color:#f87171; }

    div.stButton > button {
        background: #3b82f6;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 15px;
        border: none;
        border-radius: 10px;
        padding: 11px 18px;
        width: 100%;
        transition: all 0.15s ease;
    }
    div.stButton > button:hover { background:#2563eb; color:#ffffff !important; }

    div.stDownloadButton > button {
        background: #0b0e14;
        color: #60a5fa !important;
        font-weight: 700;
        border: 1.5px solid #3b82f6;
        border-radius: 10px;
        padding: 10px 16px;
        width: 100%;
    }
    div.stDownloadButton > button:hover { background:#0f2748; color:#93c5fd !important; }

    div[data-baseweb="input"] > div {
        background: #0b0e14 !important;
        border: 1.5px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
    }
    input { color: #f3f4f6 !important; font-size: 15px !important; }

    .stTabs [data-baseweb="tab-list"] { gap:4px; background:#0b0e14; padding:5px; border-radius:10px; border:1px solid rgba(255,255,255,0.08); }
    .stTabs [data-baseweb="tab"] { border-radius:7px; color:#8b95a8; font-weight:600; font-size:13px; padding:8px 14px; }
    .stTabs [aria-selected="true"] { background:#3b82f6; color:#ffffff !important; }

    /* ---- Report typography (real markdown -> HTML, sane spacing) ---- */
    .report-box {
        background:#05070a;
        border:1px solid rgba(255,255,255,0.10);
        border-radius:12px;
        padding:30px 34px;
        max-height:700px;
        overflow-y:auto;
    }
    .report-content { color:#e7eaf0; font-size:15.5px; }
    .report-content h1 { font-size:27px; font-weight:800; color:#ffffff; margin:0 0 16px 0; line-height:1.3; }
    .report-content h2 { font-size:20px; font-weight:800; color:#ffffff; margin:24px 0 10px 0; padding-top:14px; border-top:1px solid rgba(255,255,255,0.08); }
    .report-content h2:first-child { border-top:none; padding-top:0; margin-top:0; }
    .report-content h3 { font-size:16.5px; font-weight:700; color:#93c5fd; margin:16px 0 8px 0; }
    .report-content h4 { font-size:15px; font-weight:700; color:#93c5fd; margin:14px 0 6px 0; }
    .report-content p { margin:0 0 12px 0; line-height:1.75; }
    .report-content ul, .report-content ol { margin:0 0 12px 0; padding-left:22px; line-height:1.75; }
    .report-content li { margin-bottom:5px; }
    .report-content li > p { margin-bottom:4px; }
    .report-content strong { color:#ffffff; font-weight:700; }
    .report-content blockquote { margin:0 0 12px 0; padding:8px 16px; border-left:3px solid #3b82f6; background:rgba(59,130,246,0.06); color:#c7d2e3; }
    .report-content a {
        color:#60a5fa; text-decoration:none; border-bottom:1px solid rgba(96,165,250,0.4);
        word-break: break-word;
    }
    .report-content a:hover { text-decoration:underline; }
    .report-content table { width:100%; border-collapse:collapse; margin:0 0 14px 0; font-size:14px; }
    .report-content th, .report-content td { border:1px solid rgba(255,255,255,0.1); padding:8px 10px; text-align:left; }
    .report-content th { background:rgba(59,130,246,0.1); color:#ffffff; }
    .report-content hr { border:none; border-top:1px solid rgba(255,255,255,0.1); margin:18px 0; }

    .mono {
        font-family:'JetBrains Mono', monospace; font-size:12px; background:#000000;
        border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:16px;
        color:#9aa4b5; max-height:420px; overflow-y:auto; white-space:pre-wrap;
    }
    .badge {
        display:inline-block; padding:3px 10px; border-radius:20px; font-size:10.5px; font-weight:700;
        letter-spacing:0.3px; background:rgba(34,197,94,0.14); color:#22c55e; border:1px solid rgba(34,197,94,0.35);
    }
    </style>
    """
)

# =============================================================================
# STEP DEFINITIONS
# =============================================================================
STEPS = [
    {"key": "search", "label": "Search Agent", "desc": "Finding recent, reliable sources", "marker": "Step 1"},
    {"key": "reader", "label": "Reader Agent", "desc": "Scraping the most relevant page", "marker": "Step 2"},
    {"key": "writer", "label": "Writer Chain", "desc": "Drafting the research report", "marker": "Step 3"},
    {"key": "critic", "label": "Critic Chain", "desc": "Reviewing report quality", "marker": "Step 4"},
]
ICONS = {"pending": "○", "running": "◐", "done": "✓", "error": "✕"}


def render_pipeline(status_map, placeholder):
    rows = []
    for step in STEPS:
        s = status_map.get(step["key"], "pending")
        status_text = "Failed" if s == "error" else step["desc"]
        rows.append(
            f'<div class="pipe-step"><div class="pipe-dot dot-{s}">{ICONS[s]}</div>'
            f'<div><p class="pipe-label">{step["label"]}</p>'
            f'<div class="pipe-status status-{s}">{status_text}</div></div></div>'
        )
    out = '<div class="pipeline-wrap">' + "".join(rows) + "</div>"
    placeholder.markdown(out, unsafe_allow_html=True)


# =============================================================================
# TEXT CLEANUP
# =============================================================================
def to_text(value) -> str:
    """Safely convert any pipeline output (str, list, dict, message object,
    etc.) into plain text so rendering never crashes on unexpected types."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "\n\n".join(to_text(v) for v in value)
    if isinstance(value, dict):
        return "\n".join(f"{k}: {to_text(v)}" for k, v in value.items())
    if hasattr(value, "content"):  # e.g. LangChain message objects
        return to_text(value.content)
    return str(value)


def clean_text(value) -> str:
    text = to_text(value)
    if not text:
        return ""
    text = text.strip()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]{2,}", " ", text)     # collapse stray double/triple spaces
    text = re.sub(r"[ \t]+\n", "\n", text)     # trailing spaces before newline
    text = re.sub(r"\n{3,}", "\n\n", text)     # cap blank lines at 1
    return text


# =============================================================================
# MARKDOWN REPORT RENDERING
# (renders the report exactly the way the writer agent formatted it —
#  markdown links, bold text, section titles — instead of guessing)
# =============================================================================
HEADING_NUM_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.{2,90})$")
SCORE_LINE_RE = re.compile(r"^score\s*:\s*.+$", re.I)
TOP_LEVEL_TITLES = {
    "introduction", "key findings", "conclusion", "sources",
    "summary", "recommendations", "overview", "final report",
    "strengths", "areas to improve", "weaknesses", "verdict",
    "one line verdict",
}


def _looks_like_heading(line: str) -> bool:
    return bool(len(line) <= 90 and not line.endswith((".", ",", ";", ")")))


def fix_list_spacing(text: str) -> str:
    """Ensure every markdown list has a blank line before it starts.
    Without this, a line like 'Strengths:' directly followed by '- item'
    (no blank line) gets merged by the markdown parser into one run-on
    paragraph instead of a proper bullet list."""
    lines = text.split("\n")
    out = []
    for line in lines:
        stripped = line.strip()
        is_list_item = bool(re.match(r"^[-*+]\s+", stripped)) or bool(re.match(r"^\d+\.\s+", stripped))
        if is_list_item and out:
            prev = out[-1].strip()
            prev_is_list = bool(re.match(r"^[-*+]\s+", prev)) or bool(re.match(r"^\d+\.\s+", prev))
            if prev and not prev_is_list:
                out.append("")
        out.append(line)
    return "\n".join(out)


def add_heading_markers(text: str) -> str:
    """Detect outline-style section titles the writer/critic agent produced
    (e.g. '1. Introduction', 'Strengths:', 'Score: 8.5/10') and convert
    them to real markdown headings so they render as headings instead of
    plain paragraphs."""
    lines = text.split("\n")
    out = []
    prev_blank = True
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out.append(line)
            prev_blank = True
            continue

        if stripped.startswith("#"):
            out.append(line)
            prev_blank = False
            continue

        converted = None
        if prev_blank and _looks_like_heading(stripped):
            m = HEADING_NUM_RE.match(stripped)
            if m:
                num = m.group(1)
                depth = min(2 + num.count("."), 4)
                converted = "#" * depth + " " + stripped
            elif stripped.lower().rstrip(":") in TOP_LEVEL_TITLES:
                converted = "## " + stripped

        out.append(converted if converted else line)
        prev_blank = False
    return "\n".join(out)


def _fallback_markdown(text: str) -> str:
    """Minimal markdown -> HTML converter used only if the `markdown`
    package isn't installed."""
    blocks = re.split(r"\n\s*\n", text)
    parts = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("#### "):
            parts.append(f"<h4>{block[5:]}</h4>")
        elif block.startswith("### "):
            parts.append(f"<h3>{block[4:]}</h3>")
        elif block.startswith("## "):
            parts.append(f"<h2>{block[3:]}</h2>")
        elif block.startswith("# "):
            parts.append(f"<h1>{block[2:]}</h1>")
        elif re.match(r"^[-*]\s+", block):
            items = [re.sub(r"^[-*]\s+", "", ln.strip()) for ln in block.split("\n") if ln.strip()]
            parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
        else:
            block = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", block)
            block = re.sub(r"\[(.+?)\]\((https?://[^\s\)]+)\)", r'<a href="\2">\1</a>', block)
            block = block.replace("\n", " ")
            parts.append(f"<p>{block}</p>")
    return "".join(parts)


def _linkify_bare_urls(html_out: str) -> str:
    """Turn any remaining bare URLs (not already part of an <a> tag) into
    clickable links, without touching text/attributes already inside <a>."""
    anchors = []

    def stash(m):
        anchors.append(m.group(0))
        return f"@@ANCHOR{len(anchors) - 1}@@"

    protected = re.sub(r"<a\b[^>]*>.*?</a>", stash, html_out, flags=re.DOTALL)
    protected = re.sub(
        r'(https?://[^\s<>"\')\]]+)',
        lambda m: f'<a target="_blank" rel="noopener" href="{m.group(1)}">{m.group(1)}</a>',
        protected,
    )
    for i, a in enumerate(anchors):
        protected = protected.replace(f"@@ANCHOR{i}@@", a)
    return protected


def render_report_html(value) -> str:
    text = clean_text(value)
    if not text:
        return '<div class="report-content"><em>No content generated.</em></div>'

    text = add_heading_markers(text)

    if MARKDOWN_LIB:
        html_out = md_lib.markdown(text, extensions=["extra", "sane_lists"])
    else:
        html_out = _fallback_markdown(text)

    html_out = re.sub(r'<a href="', '<a target="_blank" rel="noopener" href="', html_out)
    html_out = _linkify_bare_urls(html_out)

    return f'<div class="report-content">{html_out}</div>'


# =============================================================================
# EXPORT HELPERS
# =============================================================================
def build_txt(topic: str, state: dict) -> str:
    parts = [
        f"RESEARCH REPORT: {topic}",
        "=" * 60,
        "",
        "FINAL REPORT",
        "-" * 60,
        clean_text(state.get("report", "")),
        "",
        "CRITIC FEEDBACK",
        "-" * 60,
        clean_text(state.get("feedback", "")),
        "",
        "SEARCH RESULTS",
        "-" * 60,
        clean_text(state.get("search_results", "")),
        "",
        "SCRAPED CONTENT",
        "-" * 60,
        clean_text(state.get("scraped_content", "")),
    ]
    return "\n".join(parts)


def wrap_long_tokens(text: str, max_len: int = 70) -> str:
    """Insert breakpoints into very long unbroken strings (e.g. raw URLs)
    so FPDF's multi_cell never hits 'not enough horizontal space' errors."""
    def wrap_word(word):
        if len(word) > max_len:
            return " ".join(word[i:i + max_len] for i in range(0, len(word), max_len))
        return word

    return "\n".join(
        " ".join(wrap_word(w) for w in line.split(" "))
        for line in text.split("\n")
    )


def build_pdf(topic: str, state: dict) -> bytes:
    pdf = FPDF(format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def section(title, body):
        pdf.set_x(15)
        pdf.set_font("Helvetica", "B", 13)
        pdf.multi_cell(0, 8, title, align="L")
        pdf.ln(1)
        pdf.set_x(15)
        pdf.set_font("Helvetica", "", 10.5)

        safe_body = clean_text(body)
        safe_body = wrap_long_tokens(safe_body, max_len=70)
        safe_body = safe_body.encode("latin-1", "replace").decode("latin-1")

        try:
            pdf.multi_cell(0, 6, safe_body, align="L")
        except Exception:
            safe_body = wrap_long_tokens(safe_body, max_len=25)
            pdf.set_x(15)
            pdf.multi_cell(0, 6, safe_body, align="L")
        pdf.ln(5)

    pdf.set_font("Helvetica", "B", 18)
    safe_topic = str(topic).encode("latin-1", "replace").decode("latin-1")
    safe_topic = wrap_long_tokens(safe_topic, max_len=70)
    pdf.multi_cell(0, 10, f"Research Report: {safe_topic}", align="L")
    pdf.ln(3)

    section("Final Report", state.get("report", ""))
    section("Critic Feedback", state.get("feedback", ""))
    section("Search Results", state.get("search_results", ""))
    section("Scraped Content", state.get("scraped_content", ""))

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1", "replace")
    return bytes(output)


class QueueStream(io.TextIOBase):
    def __init__(self, q: queue.Queue):
        self.q = q

    def write(self, text):
        if text:
            self.q.put(text)
        return len(text)

    def flush(self):
        pass


def run_pipeline_in_thread(topic, log_queue, result_box):
    stream = QueueStream(log_queue)
    try:
        with redirect_stdout(stream):
            result = run_search_agent(topic)
        result_box["state"] = result
        result_box["error"] = None
    except Exception as e:
        result_box["state"] = None
        result_box["error"] = str(e)
    finally:
        result_box["done"] = True


# =============================================================================
# SESSION STATE
# =============================================================================
for key, default in [("state", None), ("logs", ""), ("topic", ""), ("running", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# =============================================================================
# HEADER
# =============================================================================
md(
    """
    <div class="hero">
    <p class="hero-tag">Multi-Agent AI Research System</p>
    <p class="hero-title">🧠 Research <span>Intelligence</span></p>
    <p class="hero-sub">Autonomous multi-agent pipeline — Search · Read · Write · Critique</p>
    </div>
    """
)

main_col, side_col = st.columns([2.6, 1], gap="large")

# =============================================================================
# LEFT COLUMN — Input
# =============================================================================
with main_col:
    md('<div class="card"><h4>Research Topic</h4></div>')
    topic = st.text_input(
        "Enter a research topic",
        placeholder="e.g. Latest breakthroughs in quantum computing",
        label_visibility="collapsed",
    )
    run_clicked = st.button("🚀  Run Research Pipeline", use_container_width=True)
    results_area = st.container()

with side_col:
    md('<div class="card"><h4>Pipeline Status</h4></div>')
    pipeline_placeholder = st.empty()
    render_pipeline({}, pipeline_placeholder)

# =============================================================================
# EXECUTION
# =============================================================================
if run_clicked:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        log_queue = queue.Queue()
        result_box = {"state": None, "error": None, "done": False}
        status_map = {}

        worker = threading.Thread(
            target=run_pipeline_in_thread, args=(topic, log_queue, result_box), daemon=True
        )
        worker.start()

        collected_logs = ""

        with st.spinner("Agents are working..."):
            while not result_box["done"] or not log_queue.empty():
                try:
                    chunk = log_queue.get(timeout=0.15)
                    collected_logs += chunk
                    for i, step in enumerate(STEPS):
                        if step["marker"] in collected_logs:
                            for j in range(i):
                                status_map[STEPS[j]["key"]] = "done"
                            status_map[step["key"]] = "running"
                    render_pipeline(status_map, pipeline_placeholder)
                except queue.Empty:
                    if result_box["done"]:
                        break
                    time.sleep(0.1)

        if result_box["error"]:
            for s in STEPS:
                if status_map.get(s["key"]) == "running":
                    status_map[s["key"]] = "error"
            render_pipeline(status_map, pipeline_placeholder)
            st.error(f"Pipeline failed: {result_box['error']}")
        else:
            for s in STEPS:
                status_map[s["key"]] = "done"
            render_pipeline(status_map, pipeline_placeholder)
            st.session_state.state = result_box["state"]
            st.session_state.logs = collected_logs
            st.session_state.topic = topic
            st.success("✅ Research completed successfully.")

# =============================================================================
# RESULTS DISPLAY — one combined Final Report output
# =============================================================================
state = st.session_state.state

with results_area:
    if state:
        st.markdown("<br>", unsafe_allow_html=True)
        md('<div class="card"><h4>📄 Final Research Report <span class="badge">READY</span></h4></div>')
        md(f'<div class="report-box">{render_report_html(state.get("report", ""))}</div>')

        with st.expander("🧐 Show Critic Feedback & Raw Pipeline Data"):
            fc, fs, fr, fl = st.tabs(["Critic Feedback", "Search Results", "Scraped Content", "Logs"])
            with fc:
                md(f'<div class="report-box">{render_report_html(state.get("feedback", ""))}</div>')
            with fs:
                md(f'<div class="report-box">{render_report_html(state.get("search_results", ""))}</div>')
            with fr:
                md(f'<div class="report-box">{render_report_html(state.get("scraped_content", ""))}</div>')
            with fl:
                md(f'<div class="mono">{html.escape(st.session_state.logs or "No logs captured.")}</div>')

        st.markdown("<br>", unsafe_allow_html=True)
        md('<div class="card"><h4>⬇️ Export Report</h4></div>')

        c1, c2 = st.columns(2)
        txt_data = build_txt(st.session_state.topic, state)
        with c1:
            st.download_button(
                "Download as .TXT",
                data=txt_data,
                file_name=f"{st.session_state.topic.strip().replace(' ', '_')}_report.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with c2:
            if PDF_AVAILABLE:
                try:
                    pdf_data = build_pdf(st.session_state.topic, state)
                    st.download_button(
                        "Download as .PDF",
                        data=pdf_data,
                        file_name=f"{st.session_state.topic.strip().replace(' ', '_')}_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.caption(f"⚠️ PDF export failed: {e}")
            else:
                st.caption("Install `fpdf2` to enable PDF export: `pip install fpdf2`")
    else:
        md(
            """
            <div class="card" style="text-align:center; padding: 50px 20px;">
            <div style="font-size:38px;">🧭</div>
            <p style="color:#8b95a8; font-size:14.5px; margin-top:10px;">
            Enter a topic above and click <b style="color:#f3f4f6;">Run Research Pipeline</b> to begin.
            </p>
            </div>
            """
        )