import streamlit as st
from db import get_conn
from auth import auth_page
from ui import eintrag_dialog, dashboard_page, entries_page, settings_page

st.set_page_config(
    page_title="Finanz-Master",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# FINANCE PRO – Marine Neon Edition (v3.0)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --marine:        #0F2747;
    --marine-light:  #1B3A6B;
    --neon:          #39FF14;
    --orange:        #FF8C42;
    --bg:            #F4F6F9;
    --surface:       #FFFFFF;
    --surface-soft:  #F1F3F6;
    --text:          #1E293B;
    --text-soft:     #64748B;

    --value-pos:     #2BB34F;
    --value-neg:     #F44336;

    --border:        rgba(15,39,71,0.08);
    --radius:        14px;
    --radius-small:  8px;
}

/* ───────────── Base ───────────── */

html, body {
    font-family: 'Outfit', sans-serif !important;
    color: var(--text);
}

[data-testid="stAppViewContainer"] {
    background: var(--bg);
}

/* Typography */
h1, h2, h3, h4 {
    font-weight: 700 !important;
    color: var(--marine);
}

.stMarkdown p,
label,
small,
[data-testid="stMetricLabel"],
[data-testid="stWidgetLabel"] {
    color: var(--text-soft);
}

/* ───────────── Sidebar ───────────── */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--marine), var(--marine-light));
    box-shadow: 4px 0 20px rgba(0,0,0,0.08);
}

[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.95);
}

/* Primary Button (Neon CTA) */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--neon);
    color: #05220A;
    font-weight: 700;
    border-radius: var(--radius-small);
    border: none;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(57,255,20,0.4);
}

/* Secondary Button */
.stButton > button {
    border-radius: var(--radius-small);
}

/* ───────────── Cards / Metrics ───────────── */

[data-testid="metric-container"] {
    background: var(--surface);
    border-radius: var(--radius);
    border: 1px solid var(--border);
    padding: 1rem;
    box-shadow: 0 4px 14px rgba(15,39,71,0.05);
}

[data-testid="stMetricValue"] {
    font-weight: 800;
    color: var(--text);
}

/* ───────────── Expander ───────────── */

.stExpander {
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background: var(--surface);
    box-shadow: 0 3px 10px rgba(0,0,0,0.04);
}

.stExpander summary {
    background: var(--marine-light);
    color: white;
    border-radius: var(--radius-small);
    font-weight: 600;
}

.stExpander summary:hover {
    background: var(--marine);
}

.stExpander svg {
    fill: white !important;
}

/* ───────────── Charts (SVG Fix) ───────────── */

svg text {
    fill: var(--text-soft) !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ───────────── Modal Styling ───────────── */

div[data-testid="stDialogOverlay"] {
    background: rgba(15,39,71,0.45) !important;
}

div[data-testid="stDialog"] {
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

div[data-testid="stDialog"] * {
    color: var(--text) !important;
}

/* ───────────── Selectbox / Dropdown ───────────── */

div[data-baseweb="select"] > div {
    background: var(--surface);
    border-radius: var(--radius-small);
    border: 1px solid var(--border);
    color: var(--text);
}

div[role="listbox"] {
    background: var(--surface);
    border-radius: var(--radius-small);
    border: 1px solid var(--border);
}

div[role="option"] {
    background: var(--surface);
    color: var(--text);
}

div[role="option"]:hover {
    background: var(--surface-soft);
}

div[aria-selected="true"] {
    background: var(--marine-light) !important;
    color: white !important;
}

/* ───────────── Inputs ───────────── */

input, textarea {
    border-radius: var(--radius-small) !important;
    border: 1px solid var(--border) !important;
}

/* ───────────── Value Classes (unchanged logic) ───────────── */

.pos { color: var(--value-pos) !important; font-weight:600; }
.neg { color: var(--value-neg) !important; font-weight:600; }

/* ───────────── Accent Elements ───────────── */

.orange-accent {
    color: var(--orange);
    font-weight: 600;
}

.neon-accent {
    color: var(--neon);
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ───────────── Routing ─────────────

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth_page()
else:
    conn = get_conn()
    u_id = st.session_state.user_id
    username = st.session_state.get('username', 'User')
    display_name = st.session_state.get('vorname', username)

    with st.sidebar:
        initials = (display_name[:2]).upper()

        st.markdown(f"""
        <div style="padding:1.6rem 0.5rem 1rem;
                    text-align:center;
                    border-bottom:1px solid rgba(255,255,255,0.15);
                    margin-bottom:1rem;">
            <div style="width:52px;height:52px;border-radius:16px;
                        background:rgba(57,255,20,0.15);
                        border:2px solid var(--neon);
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 0.8rem;
                        font-weight:800;
                        font-size:1.1rem;
                        color:var(--neon);">
                {initials}
            </div>
            <div style="font-weight:700;color:white;font-size:1.05rem;">
                {display_name}
            </div>
            <div style="font-size:0.75rem;
                        color:rgba(255,255,255,0.45);">
                @{username}
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📝 Einträge", "⚙️ Verwaltung"],
            label_visibility="collapsed"
        )

        st.divider()

        if st.button("＋ Neuer Eintrag", use_container_width=True, type="primary"):
            eintrag_dialog(conn, u_id)

        if st.button("↩ Abmelden", use_container_width=True):
            for key in ['logged_in', 'user_id', 'username', 'vorname']:
                st.session_state.pop(key, None)
            st.rerun()

    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
