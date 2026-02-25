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
# PRECISION FINANCE – Dual Light/Dark CSS
# Palette:
#   Marine  #1B3A6B   → Navigation, Struktur, Links
#   Neongrün #39D353  → Positive Werte, CTAs, Einnahmen
#   Orange   #F07800  → Warnungen, Abos, Highlights
#   Hellgrau #F4F5F7  → Light-BG
#   Dunkelgrau #1A1F2E → Dark-BG / Light-Text
#   Rot      #D63B3B  → Negative Werte, Ausgaben
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/*
 * FARBSTEUERUNG NUR ÜBER config.toml:
 *
 *   primaryColor             → Sidebar, Akzente, Buttons, Hover
 *   backgroundColor          → App-Hintergrund
 *   secondaryBackgroundColor → Karten, Eingaben, Tabellen
 *   textColor                → Haupttext
 *
 * Streamlit setzt diese als CSS-Vars:
 *   --primary-color, --background-color,
 *   --secondary-background-color, --text-color
 *
 * Wir leiten daraus alle App-Variablen ab.
 */
:root {
    /* ── Von config.toml gesteuert ─────────── */
    --c-primary:  var(--primary-color,       #1B3A6B);
    --c-bg:       var(--background-color,    #E8EBF2);
    --c-surface:  var(--secondary-background-color, #F4F5F9);
    --c-text:     var(--text-color,          #1A1F2E);

    /* ── Semantische Ableitungen ─────────────
     * Alle anderen Farben werden aus den 4 Basis-Variablen
     * berechnet – kein hardcodierter Wert der config.toml widerspricht.
     */

    /* Semantische Wertfarben – bewusst fix, nicht theme-abhängig */
    --value-pos:   #1C9E3A;   /* Positive Werte / Einnahmen → immer grün  */
    --value-neg:   #D63B3B;   /* Negative Werte / Ausgaben  → immer rot   */
    --value-warn:  #F07800;   /* Warnungen / Abos           → immer orange */
    --value-neon:  #39D353;   /* CTA / Neon-Grün Sidebar    */

    /* Oberflächen-Abstufungen (relativ zu --c-surface) */
    --c-surface2:  color-mix(in srgb, var(--c-surface) 80%, var(--c-bg) 20%);
    --c-dialog:    color-mix(in srgb, var(--c-surface) 90%, var(--c-bg) 10%);

    /* Ränder aus primaryColor */
    --border:      color-mix(in srgb, var(--c-primary) 11%, transparent);
    --border-s:    color-mix(in srgb, var(--c-primary) 22%, transparent);

    /* Text-Abstufungen aus --c-text */
    --text-2:      color-mix(in srgb, var(--c-text) 70%, transparent);
    --text-3:      color-mix(in srgb, var(--c-text) 40%, transparent);

    /* Schatten */
    --shadow:      color-mix(in srgb, var(--c-primary) 8%, transparent);

    /* Akzent-Dimming */
    --primary-dim:  color-mix(in srgb, var(--c-primary) 9%, transparent);
    --primary-dim2: color-mix(in srgb, var(--c-primary) 5%, transparent);

    /* Radien */
    --r:   12px;
    --r-s:  8px;
}

/* ── DARK MODE ────────────────────────────────────────────────────
 * Überschreibt nur die 4 Basis-Variablen.
 * Dark-Mode-Farben ebenfalls nur hier ändern.
 *
 *   --dm-primary:  Akzentfarbe im Dark-Mode  (z.B. aufgehelltes Marine)
 *   --dm-bg:       App-Hintergrund           (z.B. dunkles Schieferblau)
 *   --dm-surface:  Karten / Eingaben         (z.B. mittleres Blaugrau)
 *   --dm-text:     Haupttext                 (z.B. weiches Eisblau)
 * ─────────────────────────────────────────────────────────────── */
:root {
    --dm-primary:  #3A6FBF;
    --dm-bg:       #1E2132;
    --dm-surface:  #262B40;
    --dm-text:     #DDE2F0;
}

[data-theme="dark"] {
    --c-primary:  var(--dm-primary);
    --c-bg:       var(--dm-bg);
    --c-surface:  var(--dm-surface);
    --c-text:     var(--dm-text);
}

/* ── BASE ─────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: var(--c-bg) !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
.main .block-container {
    padding: 1.8rem 2.8rem 3rem !important;
    max-width: 1500px !important;
}

/* ── SIDEBAR ──────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--c-primary) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    border-radius: var(--r-s) !important;
    color: rgba(255,255,255,0.75) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.13) !important;
    border-color: rgba(255,255,255,0.24) !important;
    color: white !important;
    transform: translateX(2px);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--value-neon) !important;
    border-color: var(--value-neon) !important;
    color: #0A1F0D !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(57,211,83,0.35);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    filter: brightness(1.1);
    box-shadow: 0 6px 20px rgba(57,211,83,0.45);
    transform: translateX(2px) translateY(-1px);
}
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label {
    border-radius: var(--r-s) !important;
    padding: 0.55rem 0.85rem !important;
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    transition: all 0.18s ease !important;
    border: 1px solid transparent !important;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(255,255,255,0.13) !important;
    border-color: rgba(255,255,255,0.22) !important;
    color: white !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stRadio label:hover:not(:has(input:checked)) {
    background: rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSidebar"] [data-testid="stRadioLabel"] { display: none !important; }
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2) !important;
}

/* Sidebar-Toggle */
[data-testid="stSidebarCollapseButton"] button,
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {
    background: rgba(255,255,255,0.18) !important;
    border: 1px solid rgba(255,255,255,0.32) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebarCollapseButton"] button svg,
button[aria-label="Close sidebar"] svg,
button[aria-label="Open sidebar"] svg {
    fill: white !important; stroke: white !important; opacity: 1 !important;
}
[data-testid="collapsedControl"] {
    background: var(--c-primary) !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="collapsedControl"] button svg {
    fill: white !important; stroke: white !important;
}

/* ── METRIKEN ─────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--c-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 1.1rem 1.3rem !important;
    box-shadow: 0 2px 6px var(--shadow) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::after {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    background: var(--c-primary);
    border-radius: 3px 0 0 3px;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 18px var(--shadow) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-3) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--c-text) !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── DATAFRAMES ───────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
}
[data-testid="stDataFrame"] thead th {
    background: var(--c-surface2) !important;
    color: var(--text-2) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-s) !important;
    padding: 0.65rem 1rem !important;
}
[data-testid="stDataFrame"] tbody tr {
    border-bottom: 1px solid var(--border) !important;
    transition: background 0.12s !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(odd) td {
    background: var(--c-surface) !important;
    color: var(--c-text) !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background: var(--c-surface2) !important;
    color: var(--c-text) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: var(--primary-dim) !important;
}
[data-testid="stDataFrame"] tbody td {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1rem !important;
}

/* ── EXPANDER ─────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--c-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 1px 4px var(--shadow);
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-s) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: var(--c-text) !important;
    font-size: 0.9rem !important;
    padding: 0.85rem 1.1rem !important;
}

/* ── TABS ─────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--c-surface2) !important;
    border-radius: var(--r-s) !important;
    padding: 3px !important;
    gap: 0 !important;
    border: 1px solid var(--border) !important;
    width: fit-content;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    color: var(--text-3) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.4rem 1.1rem !important;
    font-size: 0.87rem !important;
    transition: all 0.18s !important;
}
.stTabs [aria-selected="true"] {
    background: var(--c-surface) !important;
    color: var(--c-primary) !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
    border: 1px solid var(--border) !important;
}

/* ── BUTTONS ──────────────────────────────── */
.stButton > button {
    font-family: 'Outfit', sans-serif !important;
    border-radius: var(--r-s) !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    transition: all 0.18s ease !important;
    border: 1px solid var(--border-s) !important;
    background: var(--c-surface) !important;
    color: var(--text-2) !important;
    box-shadow: 0 1px 3px var(--shadow) !important;
}
.stButton > button[kind="primary"] {
    background: var(--c-primary) !important;
    border-color: var(--c-primary) !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 10px var(--primary-dim) !important;
}
.stButton > button[kind="primary"]:hover {
    filter: brightness(1.1) !important;
    box-shadow: 0 5px 16px var(--border-s) !important;
    transform: translateY(-1px);
}
.stButton > button:not([kind="primary"]):hover {
    border-color: var(--c-primary) !important;
    color: var(--c-primary) !important;
    background: var(--primary-dim2) !important;
}

/* ── SEGMENTED CONTROL ────────────────────── */
[data-testid="stSegmentedControl"] {
    background: var(--c-surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-s) !important;
    padding: 3px !important;
}
[data-testid="stSegmentedControl"] button {
    border-radius: 6px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--text-3) !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.18s !important;
}
[data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: var(--c-surface) !important;
    color: var(--c-primary) !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
    border: 1px solid var(--border) !important;
}

/* ── INPUTS & SELECTBOX ───────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: var(--c-surface) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: var(--r-s) !important;
    color: var(--c-text) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.18s, box-shadow 0.18s !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--c-primary) !important;
    box-shadow: 0 0 0 3px var(--primary-dim) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder {
    color: var(--text-3) !important;
    opacity: 1 !important;
}
[data-testid="stNumberInput"] button {
    background: var(--c-surface2) !important;
    border-color: var(--border) !important;
    color: var(--text-2) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: var(--c-surface) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: var(--r-s) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    color: var(--c-text) !important;
}
[data-testid="InputInstructions"],
[class*="InputInstructions"],
div[class*="instructionsContainer"] {
    color: var(--text-3) !important;
    opacity: 1 !important;
}

/* ── MODAL / DIALOG ───────────────────────── */
[data-testid="stModal"] > div {
    background: var(--c-dialog) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 50px var(--shadow), 0 4px 16px var(--primary-dim) !important;
}
[data-testid="stModal"] [data-testid="stTextInput"] input,
[data-testid="stModal"] [data-testid="stNumberInput"] input,
[data-testid="stModal"] [data-testid="stDateInput"] input,
[data-testid="stModal"] [data-testid="stSelectbox"] > div > div {
    background: var(--c-surface) !important;
    color: var(--c-text) !important;
}

/* ── ALERTS ───────────────────────────────── */
[data-testid="stInfo"] {
    background: var(--primary-dim2) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--c-primary) !important;
    border-radius: var(--r-s) !important;
    color: var(--c-primary) !important;
}
[data-testid="stSuccess"] {
    background: rgba(28,158,58,0.07) !important;
    border: 1px solid rgba(28,158,58,0.2) !important;
    border-left: 3px solid var(--value-pos) !important;
    border-radius: var(--r-s) !important;
}
[data-testid="stError"] {
    background: rgba(214,59,59,0.07) !important;
    border: 1px solid rgba(214,59,59,0.2) !important;
    border-left: 3px solid var(--value-neg) !important;
    border-radius: var(--r-s) !important;
}
[data-testid="stWarning"] {
    background: rgba(240,120,0,0.07) !important;
    border: 1px solid rgba(240,120,0,0.2) !important;
    border-left: 3px solid var(--value-warn) !important;
    border-radius: var(--r-s) !important;
}

/* ── PLOTLY ───────────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: var(--c-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
    padding: 0.25rem;
}

/* ── TYPO ─────────────────────────────────── */
h1 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: var(--c-text) !important;
}
h2 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    color: var(--c-text) !important;
    font-size: 1.15rem !important;
    letter-spacing: -0.015em !important;
}
h3 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-2) !important;
    font-size: 0.95rem !important;
}

/* ── DIVIDER ──────────────────────────────── */
hr {
    border: none !important;
    height: 1px !important;
    background: var(--border) !important;
    margin: 1rem 0 !important;
}

/* ── SCROLLBAR ────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-s); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--c-primary); }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# --- THEME INJECTOR ---
def _inject_theme():
    val = "dark" if st.session_state.dark_mode else "light"
    st.markdown(f"""<script>
        (function() {{
            var el = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
            if (el) el.setAttribute('data-theme', '{val}');
        }})();
    </script>""", unsafe_allow_html=True)

# --- ROUTING ---
_inject_theme()
if not st.session_state.logged_in:
    auth_page()
else:
    conn = get_conn()
    u_id         = st.session_state.user_id
    username     = st.session_state.get('username', 'User')
    vorname      = st.session_state.get('vorname', '')
    display_name = vorname if vorname else username

    with st.sidebar:
        # User-Badge
        initials = (display_name[:2]).upper()
        st.markdown(f"""
        <div style="padding:1.4rem 0.5rem 1rem;text-align:center;
                    border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:0.8rem;">
            <div style="
                width:48px;height:48px;border-radius:12px;
                background:rgba(57,211,83,0.2);
                border:2px solid rgba(57,211,83,0.5);
                display:flex;align-items:center;justify-content:center;
                margin:0 auto 0.7rem;
                font-family:'Outfit',sans-serif;font-weight:800;font-size:1rem;
                color:#39D353;letter-spacing:-0.02em;
            ">{initials}</div>
            <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:0.95rem;
                        color:rgba(255,255,255,0.95);letter-spacing:-0.01em;">{display_name}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.35);margin-top:1px;">
                @{username}
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📝 Einträge", "⚙️ Verwaltung"],
            label_visibility="collapsed"
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.divider()

        if st.button("＋  Neuer Eintrag", width='stretch', type="primary"):
            eintrag_dialog(conn, u_id)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        # Dark/Light Toggle
        dm = st.session_state.dark_mode
        toggle_icon = "☀️" if dm else "🌙"
        toggle_label = f"{toggle_icon}  {'Hell-Modus' if dm else 'Dunkel-Modus'}"
        if st.button(toggle_label, width='stretch'):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

        if st.button("↩  Abmelden", width='stretch'):
            for key in ['logged_in', 'user_id', 'username', 'vorname', 'conn']:
                st.session_state.pop(key, None)
            st.rerun()

        st.markdown("""
        <div style="position:absolute;bottom:1rem;left:0;right:0;text-align:center;">
            <span style="font-size:0.65rem;color:rgba(255,255,255,0.15);
                         font-family:'Outfit',sans-serif;letter-spacing:0.08em;">
                FINANZ-MASTER  v1.5
            </span>
        </div>""", unsafe_allow_html=True)

    if page == "📊 Dashboard":
        dashboard_page(conn, u_id)
    elif page == "📝 Einträge":
        entries_page(conn, u_id)
    elif page == "⚙️ Verwaltung":
        settings_page(conn, u_id)
