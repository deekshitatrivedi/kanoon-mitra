"""
app.py — Kanoon Mitra: Indian Legal Rights Chatbot
"""
import os, re, sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# ── Page config MUST be the very first Streamlit command in the app ─
st.set_page_config(
    page_title="Kanoon Mitra — Indian Legal Rights",
    page_icon="⚖️",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))
load_dotenv(BASE_DIR / ".env")

from rag_chain import KanoonMitraChain

# ── Topic documents (Covered Topics -> full section text) ──────────
# Looks for legal_knowledge_base.txt in a few likely locations so this
# works regardless of exactly where it lives in your project. Adjust
# KB_CANDIDATES if your file lives somewhere else.
KB_CANDIDATES = [
    BASE_DIR / "data" / "legal_knowledge_base.txt",
    BASE_DIR / "legal_knowledge_base.txt",
    BASE_DIR / "src" / "legal_knowledge_base.txt",
    BASE_DIR / "knowledge_base" / "legal_knowledge_base.txt",
]
KB_PATH = next((p for p in KB_CANDIDATES if p.exists()), KB_CANDIDATES[0])

# Order here MUST match SECTION 1, SECTION 2, ... in legal_knowledge_base.txt
TOPICS = [
    (1, "🏛️", "Fundamental Rights"),
    (2, "🚔", "Arrest Rights"),
    (3, "🏠", "Tenant Rights"),
    (4, "🛒", "Consumer Rights"),
    (5, "📋", "RTI"),
    (6, "👩", "Women's Rights"),
    (7, "💼", "Labour Rights"),
    (8, "🏗️", "RERA / Property"),
    (9, "💻", "Cyber Crime"),
    (10, "⚖️", "Free Legal Aid"),
]

@st.cache_data(show_spinner=False)
def load_topic_sections(path: str):
    """Parse legal_knowledge_base.txt into {section_number: {title, content}}."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    pattern = r"={10,}\s*\nSECTION (\d+):\s*(.+?)\s*\n={10,}\s*\n(.*?)(?=\n={10,}\s*\nSECTION|\Z)"
    sections = {}
    for num, title, content in re.findall(pattern, text, re.DOTALL):
        sections[int(num)] = {"title": title.strip(), "content": content.strip()}
    return sections

KB_SECTIONS = load_topic_sections(str(KB_PATH))


def _render_topic_body(section_num: int):
    section = KB_SECTIONS.get(section_num)
    if not section:
        st.error(
            f"Couldn't find this topic's document. Checked: `{KB_PATH}`. "
            "Make sure legal_knowledge_base.txt is at that path, or update "
            "KB_CANDIDATES in app.py."
        )
        return
    st.markdown(f"## {section['title']}")
    st.markdown(section["content"])


if hasattr(st, "dialog"):
    @st.dialog("📄 Legal Topic", width="large")
    def show_topic_dialog(section_num: int):
        _render_topic_body(section_num)
        if st.button("Close"):
            st.session_state.selected_topic = None
            st.rerun()
else:
    show_topic_dialog = None  # older Streamlit: falls back to inline expander

st.markdown("""
<style>
.main .block-container { padding-top:1.5rem; max-width:920px; }
.km-header {
  background: linear-gradient(135deg,#1a3c5e,#2d6a4f);
  border-radius:12px; padding:1.2rem 1.6rem; margin-bottom:1rem; color:white;
}
.km-header h1 { margin:0; font-size:1.7rem; }
.km-header p  { margin:.2rem 0 0; font-size:.88rem; opacity:.85; }
.disclaimer {
  background:#fff8e1; border-left:4px solid #f9a825;
  border-radius:8px; padding:.55rem 1rem;
  font-size:.78rem; color:#5d4037; margin-bottom:1rem;
}
.helplines {
  background:#e8f5e9; border-radius:8px;
  padding:.55rem 1rem; font-size:.8rem; color:#1b5e20; margin-top:.8rem;
}
div[data-testid="stChatMessage"] { border-radius:12px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────
for key, val in [("messages",[]),("chain",None),("show_src",False),("selected_topic",None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# Open the topic document modal if a topic was just clicked
if st.session_state.selected_topic is not None:
    if show_topic_dialog is not None:
        show_topic_dialog(st.session_state.selected_topic)
    # else: handled inline in the sidebar below (older Streamlit fallback)

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ Kanoon Mitra")
    st.caption("Indian Legal Rights Assistant")
    st.divider()

    groq_key = os.getenv("GROQ_API_KEY", "")
    

    st.markdown("### Topics covered")
    st.caption("Click a topic to open its full legal document")
    for num, icon, label in TOPICS:
        if st.button(f"{icon} {label}", key=f"topic_{num}", use_container_width=True):
            st.session_state.selected_topic = num
            st.rerun()
        # Fallback for Streamlit versions without st.dialog: show inline
        if show_topic_dialog is None and st.session_state.selected_topic == num:
            with st.expander(f"{icon} {label} — full document", expanded=True):
                _render_topic_body(num)
                if st.button("Close", key=f"close_{num}"):
                    st.session_state.selected_topic = None
                    st.rerun()

    st.divider()
    st.markdown("### Helplines")
    st.markdown("- **NALSA (free legal aid):** `15100`\n- **Cybercrime:** `1930`\n- **Women:** `1091`\n- **Consumer:** `1915`\n- **NHRC:** `14433`")

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────
st.markdown("""
<div class="km-header">
  <h1>⚖️ Kanoon Mitra</h1>
  <p>Your free Indian Legal Rights Assistant — Know your rights, in plain language.</p>
</div>
<div class="disclaimer">
  ⚠️ <strong>Disclaimer:</strong> This is general legal information only, not professional legal advice.
  For urgent matters, consult a qualified lawyer or call NALSA free legal aid: <strong>15100</strong>.
</div>
""", unsafe_allow_html=True)

# ── Load chain ─────────────────────────────────────────────────────
vstore = BASE_DIR / "vectorstore" / "chunks.json"
if not vstore.exists():
    st.error("⚠️ Knowledge base not found. Run `python3 src/ingest.py` first.")
    st.stop()

if not groq_key:
    st.info("👈 Enter your **Groq API key** in the sidebar. Free key at [console.groq.com](https://console.groq.com)")
    st.stop()

if st.session_state.chain is None:
    with st.spinner("Loading legal knowledge base..."):
        try:
            st.session_state.chain = KanoonMitraChain(groq_key)
        except Exception as e:
            st.error(f"Failed to load: {e}")
            st.stop()

chain: KanoonMitraChain = st.session_state.chain

# ── Quick question buttons ─────────────────────────────────────────
QUICK = {
    "🚔 Police arrested me": "What are my rights when I am arrested by police?",
    "🏠 Landlord evicting me": "Can my landlord forcibly evict me or cut off electricity?",
    "🛒 Consumer fraud": "Where and how do I file a consumer complaint in India?",
    "📋 File RTI": "How do I file an RTI application?",
    "👩 Domestic violence": "What are my rights under the Domestic Violence Act 2005?",
    "💼 Salary not paid": "My employer is not paying my salary. What legal action can I take?",
    "💻 Online scam": "I was cheated online. How do I report cybercrime in India?",
    "⚖️ Free lawyer": "How can I get a free lawyer through NALSA legal aid?",
}

st.markdown("**Quick questions:**")
cols = st.columns(4)
for i, (label, question) in enumerate(QUICK.items()):
    with cols[i % 4]:
        if st.button(label, use_container_width=True, key=f"q{i}"):
            st.session_state.messages.append({"role":"user","content":question})
            with st.spinner("Looking up your rights..."):
                answer = chain.invoke(question)
                if st.session_state.show_src:
                    srcs = chain.get_sources(question)
                    answer += "\n\n---\n**📚 Retrieved context:**\n" + "\n".join(f"- _{s}_" for s in srcs)
            st.session_state.messages.append({"role":"assistant","content":answer})
            st.rerun()

st.divider()

# ── Chat history ───────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "⚖️"):
        st.markdown(msg["content"])

if not st.session_state.messages:
    st.markdown("""
    <div style='text-align:center;color:#888;padding:2rem 0;'>
      👋 Ask me anything about your legal rights in India.<br>
      <small>Try a quick question above or type below.</small>
    </div>""", unsafe_allow_html=True)

# ── Chat input ─────────────────────────────────────────────────────
if user_input := st.chat_input("Ask about your legal rights... e.g. 'Can police arrest without a warrant?'"):
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Looking up your rights..."):
            try:
                answer = chain.invoke(user_input)
                if st.session_state.show_src:
                    srcs = chain.get_sources(user_input)
                    answer += "\n\n---\n**📚 Retrieved context:**\n" + "\n".join(f"- _{s}_" for s in srcs)
            except Exception as e:
                answer = f"Sorry, I encountered an error: {e}. Please try again."
        st.markdown(answer)

    st.session_state.messages.append({"role":"assistant","content":answer})

# ── Helpline strip ─────────────────────────────────────────────────
st.markdown("""
<div class="helplines">
📞 <strong>Helplines:</strong>
NALSA Free Legal Aid: <strong>15100</strong> &nbsp;|&nbsp;
Cybercrime: <strong>1930</strong> &nbsp;|&nbsp;
Women: <strong>1091</strong> &nbsp;|&nbsp;
Consumer: <strong>1915</strong> &nbsp;|&nbsp;
NHRC: <strong>14433</strong>
</div>
""", unsafe_allow_html=True)