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
# PRECISION FINANCE – Unified High Contrast Design (v2.0 Stable)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

/* ══════════════════════════════════════════════════════════════════
   DARKMODE KOMPLETT DEAKTIVIEREN
   color-scheme: light only → Browser färbt native Elemente
   (Inputs, Selects, Scrollbars) IMMER hell ein, egal was das OS
   oder der Browser als Präferenz gesetzt hat.
══════════════════════════════════════════════════════════════════ */
:root, html, body, * {
    color-scheme: light only !important;
}

/* ══════════════════════════════════════════════════════════════════
   FORCE LIGHT MODE – Streamlit Dark-Theme komplett überschreiben
══════════════════════════════════════════════════════════════════ */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section[data-testid="stSidebarContent"],
[data-theme="dark"] .stApp,
[data-theme="dark"] [data-testid="stAppViewContainer"],
[data-theme="dark"] [data-testid="stMain"] {
    background-color: var(--c-bg) !important;
    color: var(--c-text) !important;
}

[data-theme="dark"] [data-testid="metric-container"] {
    background-color: var(--c-metric-bg) !important;
    color: var(--c-metric-value) !important;
}

[data-theme="dark"] [data-testid="stDataFrame"],
[data-theme="dark"] [data-testid="stDataFrame"] * {
    background-color: var(--c-surface) !important;
    color: var(--c-text) !important;
}

[data-theme="dark"] .stExpander > div:last-child {
    background-color: var(--c-expander-bg) !important;
}

[data-theme="dark"] input,
[data-theme="dark"] textarea,
[data-theme="dark"] select {
    background-color: var(--c-input-bg) !important;
    color: var(--c-input-text) !important;
    border-color: var(--c-input-border) !important;
}


/* ══════════════════════════════════════════════════════════════════
   DESIGN-SYSTEM – ALLE KONFIGURIERBAREN WERTE
   ──────────────────────────────────────────────────────────────
   Hier ist die zentrale Schaltzentrale für das gesamte Layout.
   Ändere einen Wert hier → er wirkt sich überall aus.
══════════════════════════════════════════════════════════════════ */
:root {

/* ═════════════════════════════════════════════
   HAUPTFARBEN
═════════════════════════════════════════════ */

--c-primary:        #0D7EA8;   /* Cyan-Teal – Hauptakzent */
--c-bg:             #F0F2F5;   /* Kühles Hellgrau – App Hintergrund */
--c-surface:        #FFFFFF;   /* Karten / Panels */
--c-surface-2:      #E4E8EE;   /* Sekundäre Flächen */

/* ═════════════════════════════════════════════
   TEXT
═════════════════════════════════════════════ */

--c-text:           #1A2035;   /* Haupttext – dunkles Navy */
--c-text-2:         #2D3A52;   /* Sekundärtext */
--c-text-muted:     #7B8AAB;   /* Gedimmter Text */
--c-heading:        #0D1526;   /* Überschriften */
--c-subheading:     #5A6A8A;   /* Untertitel */

/* ═════════════════════════════════════════════
   STATUS
═════════════════════════════════════════════ */

--value-pos:        #0E8A5F;   /* Smaragdgrün */
--value-neg:        #C0392B;   /* Klares Rot */
--value-warn:       #D4860A;   /* Sattes Amber */
--value-neon:       #0D7EA8;   /* CTA – Cyan-Teal */

/* ═════════════════════════════════════════════
   RAHMEN
═════════════════════════════════════════════ */

--border:           #CDD4E0;   /* Kühler Graurahmen */
--border-strong:    #AAB5C8;   /* Stärkerer Rahmen */
--r:                10px;
--r-s:              7px;

/* ═════════════════════════════════════════════
   TYPO
═════════════════════════════════════════════ */

--font:         'DM Sans', sans-serif;
--font-heading: 'Rajdhani', sans-serif;
--font-size-base:   0.9rem;
--font-size-sm:     0.82rem;
--font-size-xs:     0.72rem;

/* ═════════════════════════════════════════════
   SIDEBAR
═════════════════════════════════════════════ */

--c-sidebar-bg:             #111827;   /* Tiefes Midnight Navy */
--c-sidebar-text:           #E8EDF5;   /* Helles Blau-Weiß */
--c-sidebar-text-muted:     #7B8AAB;   /* Gedimmtes Slate */
--c-sidebar-divider:        #1E2D45;   /* Dunkler Divider */
--c-sidebar-avatar-bg:      #1A2A42;   /* Avatar Hintergrund */
--c-sidebar-avatar-border:  #0D7EA8;   /* Cyan Rahmen */
--c-sidebar-avatar-text:    #38C4E8;   /* Helles Cyan */
--c-sidebar-btn-cta-bg:     #0D7EA8;   /* Cyan CTA */
--c-sidebar-btn-cta-text:   #FFFFFF;   /* Weißer Text */

/* ═════════════════════════════════════════════
   EXPANDER
═════════════════════════════════════════════ */

--c-expander-bg:            #FFFFFF;
--c-expander-header-bg:     #1A2035;   /* Navy Dunkel */
--c-expander-header-hover:  #0D7EA8;   /* Cyan Hover */
--c-expander-header-text:   #FFFFFF;
--c-expander-border:        #CDD4E0;

/* ═════════════════════════════════════════════
   METRICS
═════════════════════════════════════════════ */

--c-metric-bg:          #FFFFFF;
--c-metric-border:      #CDD4E0;
--c-metric-value:       #0D1526;
--c-metric-label:       #5A6A8A;
--c-metric-delta-pos:   #0E8A5F;
--c-metric-delta-neg:   #C0392B;

/* ═════════════════════════════════════════════
   INPUTS
═════════════════════════════════════════════ */

--c-input-bg:           #F7F9FC;
--c-input-bg-focus:     #FFFFFF;
--c-input-text:         #1A2035;
--c-input-border:       #C5CEDC;
--c-input-border-focus: #0D7EA8;
--c-input-focus-ring:   #BAE0ED;   /* Helles Cyan */
--c-input-label:        #4A5870;

/* ═════════════════════════════════════════════
   DROPDOWN
═════════════════════════════════════════════ */

--c-dropdown-bg:                #F7F9FC;
--c-dropdown-text:              #1A2035;
--c-dropdown-border:            #C5CEDC;
--c-dropdown-list-bg:           #FFFFFF;
--c-dropdown-list-border:       #CDD4E0;
--c-dropdown-list-shadow:       rgba(13,21,38,0.14);
--c-dropdown-option-text:       #1A2035;
--c-dropdown-option-hover-bg:   #E0F2FA;
--c-dropdown-option-hover-text: #0D7EA8;
--c-dropdown-option-sel-bg:     #C8E8F5;

/* ═════════════════════════════════════════════
   SEGMENTED CONTROL
═════════════════════════════════════════════ */

--c-seg-bg:             #E4E8EE;
--c-seg-active-bg:      #0D7EA8;
--c-seg-active-text:    #FFFFFF;
--c-seg-active-shadow:  rgba(13,126,168,0.30);
--c-seg-inactive-text:  #4A5870;

/* ═════════════════════════════════════════════
   BUTTONS
═════════════════════════════════════════════ */

--c-btn-primary-bg:         #0D7EA8;
--c-btn-primary-text:       #FFFFFF;
--c-btn-primary-hover:      #0A6288;
--c-btn-primary-shadow:     rgba(13,126,168,0.30);
--c-btn-secondary-bg:       #E4E8EE;
--c-btn-secondary-text:     #4A5870;
--c-btn-secondary-border:   #C5CEDC;

/* ═════════════════════════════════════════════
   MODAL
═════════════════════════════════════════════ */

--c-modal-bg:       #FFFFFF;
--c-modal-text:     #1A2035;
--c-modal-border:   #CDD4E0;
--c-modal-shadow:   rgba(13,21,38,0.28);
--c-modal-backdrop: rgba(13,21,38,0.60);

/* ═════════════════════════════════════════════
   LISTEN
═════════════════════════════════════════════ */

--c-list-bg:            #F7F9FC;
--c-list-border:        #CDD4E0;
--c-list-row-divider:   #DDE3EC;
--c-list-text-primary:  #0D1526;
--c-list-text-sub:      #5A6A8A;

/* ═════════════════════════════════════════════
   BADGES
═════════════════════════════════════════════ */

--c-badge-turnus-bg:        #FEF3E0;
--c-badge-turnus-text:      #B36A00;
--c-badge-turnus-border:    #F0C070;
--c-badge-konto-bg:         #E0F4FA;
--c-badge-konto-text:       #0D7EA8;
--c-badge-konto-border:     #90CEDE;
--c-badge-count-bg:         #E4E8EE;
--c-badge-count-text:       #4A5870;

/* ═════════════════════════════════════════════
   ALERTS
═════════════════════════════════════════════ */

--c-alert-info-bg:      #E0F4FA;
--c-alert-info-border:  #0D7EA8;
--c-alert-info-text:    #1A2035;
--c-alert-warn-bg:      #FEF3E0;
--c-alert-warn-border:  #D4860A;
--c-alert-err-bg:       #FDECEA;
--c-alert-err-border:   #C0392B;

/* ═════════════════════════════════════════════
   HEADER / SECTION
═════════════════════════════════════════════ */

--c-page-header-border: #CDD4E0;
--c-section-dot:        #0D7EA8;

/* ═════════════════════════════════════════════
   EMPTY STATE
═════════════════════════════════════════════ */

--c-empty-bg:       #F0F2F5;
--c-empty-border:   #C5CEDC;
--c-empty-text:     #5A6A8A;

/* ═════════════════════════════════════════════
   DIVIDER
═════════════════════════════════════════════ */

--c-divider:        #CDD4E0;

/* ═════════════════════════════════════════════
   TABLE
═════════════════════════════════════════════ */

--c-table-header-bg:    #E4E8EE;
--c-table-header-text:  #1A2035;
--c-table-row-even:     #FFFFFF;
--c-table-row-odd:      #F7F9FC;
--c-table-row-hover:    #E0F2FA;

/* ═════════════════════════════════════════════
   SELECTION BAR
═════════════════════════════════════════════ */

--c-selection-text:     #5A6A8A;

/* ═════════════════════════════════════════════
   VALUE PILLS
═════════════════════════════════════════════ */

--c-pill-pos-bg:        #D6F0E6;
--c-pill-pos-border:    #82CBA8;
--c-pill-neg-bg:        #FDECEA;
--c-pill-neg-border:    #E8A09A;

/* Dialog Register */
--c-dialog-seg-bg: #E4E8EE;          /* Container */
--c-dialog-seg-hover: #D5DCE8;       /* Hover */
--c-dialog-seg-active: #C2CEDF;      /* Active Hintergrund */
--c-dialog-seg-active-text: #1A2035; /* Active Text */

/* Dialog Buttons */
--c-dialog-btn-bg: #0D7EA8;          /* Primärbutton */
--c-dialog-btn-text: #FFFFFF;
--c-dialog-btn-hover: #0A6288;

/* ═════════════════════════════════════════════
   STREAMLIT MODAL – DARKMODE STABIL
═════════════════════════════════════════════ */

/* Backdrop (Abdunklung außerhalb des Dialogs) */
div[data-baseweb="modal"] {
    background: var(--c-modal-backdrop) !important;
}

/* Modal Wrapper */
div[data-baseweb="modal"] > div {
    background: transparent !important;
}

/* Eigentliches Dialogfenster */
div[role="dialog"] {
    background: var(--c-modal-bg) !important;
    color: var(--c-modal-text) !important;
    border: 1px solid var(--c-modal-border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 20px 60px var(--c-modal-shadow) !important;
}

/* NUR Text-Elemente im Dialog, nicht alles */
div[role="dialog"] p,
div[role="dialog"] span,
div[role="dialog"] label,
div[role="dialog"] h1,
div[role="dialog"] h2,
div[role="dialog"] h3 {
    color: var(--c-modal-text) !important;
}


/* ═════════════════════════════════════════════
   PILL / TAG FIX – DARKMODE SAFE
═════════════════════════════════════════════ */

/* Alle BaseWeb Tags */
div[data-baseweb="tag"],
span[data-baseweb="tag"] {
    background-color: var(--c-surface-2) !important;
    color: var(--c-text) !important;
    border: 1px solid var(--border) !important;
}

/* Positive Pills */
.pos {
    background-color: var(--c-pill-pos-bg) !important;
    border: 1px solid var(--c-pill-pos-border) !important;
    color: var(--value-pos) !important;
}

/* Negative Pills */
.neg {
    background-color: var(--c-pill-neg-bg) !important;
    border: 1px solid var(--c-pill-neg-border) !important;
    color: var(--value-neg) !important;
}

/* Warn Pills */
.warn {
    background-color: #F8E7C9 !important;
    border: 1px solid #D6B47A !important;
    color: var(--value-warn) !important;
}

/* ═════════════════════════════════════════════
   DIALOG REGISTER – SLATE STYLE
═════════════════════════════════════════════ */

div[role="dialog"] [data-baseweb="button-group"] {
    background: var(--c-dialog-seg-bg) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid #D2CCC3 !important;
}

/* Buttons */
div[role="dialog"] [data-baseweb="button-group"] button {
    background: transparent !important;
    color: #4B4B4B !important;
    border-radius: 8px !important;
    transition: all 0.15s ease;
}

/* Hover */
div[role="dialog"] [data-baseweb="button-group"] button:hover {
    background: var(--c-dialog-seg-hover) !important;
}

/* Active */
div[role="dialog"] [data-baseweb="button-group"] button[aria-pressed="true"],
div[role="dialog"] [data-baseweb="button-group"] button[data-selected="true"] {
    background: var(--c-dialog-seg-active) !important;
    color: var(--c-dialog-seg-active-text) !important;
    font-weight: 600;
}

}

/* ══════════════════════════════════════════════════════════════════
   BASIS-TYPOGRAFIE
══════════════════════════════════════════════════════════════════ */
html, body {
    font-family: var(--font) !important;
    font-size: var(--font-size-base);
    color: var(--c-text);
}

[data-testid="stAppViewContainer"] {
    background: var(--c-bg);
}

/* Markdown & normale Fließtexte */
.stMarkdown p,
.stMarkdown span,
label,
small {
    color: var(--c-text-2);
    font-family: var(--font) !important;
}

/* SVG-Text in Diagrammen (Achsenbeschriftungen etc.) */
svg text {
    fill: var(--c-text-2) !important;
    font-family: var(--font) !important;
}

/* ══════════════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--c-sidebar-bg);
}

[data-testid="stSidebar"] * {
    color: var(--c-sidebar-text);
    font-family: var(--font) !important;
}

/* CTA-Button "Neuer Eintrag" */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--c-sidebar-btn-cta-bg) !important;
    color: var(--c-sidebar-btn-cta-text) !important;
    font-weight: 700;
    border: none !important;
}

/* Abmelden- und sonstige sekundäre Buttons in Sidebar */
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
    background: transparent !important;
    color: var(--c-sidebar-text) !important;
    border: 1px solid var(--c-sidebar-divider) !important;
}

/* Radio-Navigation aktiver Punkt */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: var(--c-sidebar-text) !important;
}

/* ══════════════════════════════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════════════════════════════ */
.stExpander {
    border: 1px solid var(--c-expander-border);
    border-radius: var(--r);
    background: var(--c-expander-bg);
    margin-bottom: 1rem;
}

/* Titelzeile des Expanders */
.stExpander summary {
    background-color: var(--c-expander-header-bg);
    color: var(--c-expander-header-text);
    border-radius: var(--r-s);
}

.stExpander summary:hover {
    background-color: var(--c-expander-header-hover);
}

/* Pfeil-Icon im Expander-Header */
.stExpander svg {
    fill: var(--c-expander-header-text) !important;
}

/* ══════════════════════════════════════════════════════════════════
   METRIKEN / KPI-CARDS
══════════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: var(--c-metric-bg);
    border: 1px solid var(--c-metric-border);
    border-radius: var(--r);
}

[data-testid="stMetricValue"] {
    color: var(--c-metric-value);
    font-weight: 700;
    font-family: var(--font-heading) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--c-metric-label) !important;
    font-family: var(--font) !important;
}

/* Delta-Werte (Pfeile + Zahlen unter dem Hauptwert) */
[data-testid="stMetricDelta"] [data-testid="stMetricDeltaIcon-Up"] ~ div,
[data-testid="stMetricDelta"] span:last-child {
    color: var(--c-metric-delta-pos) !important;
}
[data-testid="stMetricDelta"][data-direction="down"] span:last-child {
    color: var(--c-metric-delta-neg) !important;
}

/* ══════════════════════════════════════════════════════════════════
   INPUTS & TEXTFELDER
══════════════════════════════════════════════════════════════════ */
input[type="text"],
input[type="number"],
input[type="email"],
input[type="password"],
textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: var(--c-input-bg) !important;
    color: var(--c-input-text) !important;
    border: 1px solid var(--c-input-border) !important;
    border-radius: var(--r-s) !important;
    font-family: var(--font) !important;
}

/* Fokus-Zustand */
input[type="text"]:focus,
input[type="number"]:focus,
textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--c-input-border-focus) !important;
    box-shadow: 0 0 0 3px var(--c-input-focus-ring) !important;
    background: var(--c-input-bg-focus) !important;
}

/* ══════════════════════════════════════════════════════════════════
   DROPDOWNS / SELECTBOX
══════════════════════════════════════════════════════════════════ */

/* Geschlossenes Dropdown */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: var(--c-dropdown-bg) !important;
    color: var(--c-dropdown-text) !important;
    border: 1px solid var(--c-dropdown-border) !important;
    border-radius: var(--r-s) !important;
}

/* Fokus-Zustand geschlossenes Dropdown */
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
    border-color: var(--c-input-border-focus) !important;
    box-shadow: 0 0 0 3px var(--c-input-focus-ring) !important;
}

/* Ausgewählter Text im Dropdown */
[data-testid="stSelectbox"] span,
[data-testid="stSelectbox"] div[class*="ValueContainer"] span {
    color: var(--c-dropdown-text) !important;
    font-family: var(--font) !important;
}

/* Aufgeklappte Optionsliste */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"],
[role="listbox"] {
    background: var(--c-dropdown-list-bg) !important;
    border: 1px solid var(--c-dropdown-list-border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 8px 32px var(--c-dropdown-list-shadow) !important;
}

/* Einzelne Option in der Liste */
li[role="option"],
[data-baseweb="menu"] li,
[role="option"] {
    background: var(--c-dropdown-list-bg) !important;
    color: var(--c-dropdown-option-text) !important;
    font-family: var(--font) !important;
}

/* Hover-Zustand einer Option */
li[role="option"]:hover,
[role="option"]:hover {
    background: var(--c-dropdown-option-hover-bg) !important;
    color: var(--c-dropdown-option-hover-text) !important;
}

/* Aktuell ausgewählte Option */
[aria-selected="true"],
[aria-selected="true"][role="option"] {
    background: var(--c-dropdown-option-sel-bg) !important;
    font-weight: 600 !important;
}

/* ══════════════════════════════════════════════════════════════════
   SEGMENTED CONTROL (z.B. Art-Auswahl: Buchung / Abo / Finanzierung)
══════════════════════════════════════════════════════════════════ */

/* Gesamte Leiste */
[data-testid="stSegmentedControl"] {
    background: var(--c-seg-bg) !important;
    border-radius: var(--r) !important;
    padding: 3px !important;
    border: 1px solid var(--border) !important;
}

/* Inaktive Segmente – explizit var(--c-seg-bg) statt transparent,
   damit kein dunkler Theme-Hintergrund durchscheint */
[data-testid="stSegmentedControl"] button {
    background: var(--c-seg-bg) !important;
    color: var(--c-seg-inactive-text) !important;
    border-radius: var(--r-s) !important;
    font-weight: 500 !important;
    border: none !important;
    font-family: var(--font) !important;
}

/* Alle Text-Nodes im Button explizit hell färben */
[data-testid="stSegmentedControl"] button p,
[data-testid="stSegmentedControl"] button span {
    color: var(--c-seg-inactive-text) !important;
}

/* Aktives / ausgewähltes Segment */
[data-testid="stSegmentedControl"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[data-active="true"] {
    background: var(--c-seg-active-bg) !important;
    color: var(--c-seg-active-text) !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px var(--c-seg-active-shadow) !important;
}

[data-testid="stSegmentedControl"] button[aria-checked="true"] p,
[data-testid="stSegmentedControl"] button[aria-checked="true"] span,
[data-testid="stSegmentedControl"] button[data-active="true"] p,
[data-testid="stSegmentedControl"] button[data-active="true"] span {
    color: var(--c-seg-active-text) !important;
}

/* ══════════════════════════════════════════════════════════════════
   DATE INPUT
══════════════════════════════════════════════════════════════════ */
[data-testid="stDateInput"] > div {
    background: var(--c-input-bg) !important;
    border: 1px solid var(--c-input-border) !important;
    border-radius: var(--r-s) !important;
}

/* ══════════════════════════════════════════════════════════════════
   BUTTONS (global, außerhalb Sidebar und Modal)
══════════════════════════════════════════════════════════════════ */

/* Primär-Buttons */
.stButton > button[kind="primary"] {
    background: var(--c-btn-primary-bg) !important;
    color: var(--c-btn-primary-text) !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: var(--r-s) !important;
    font-family: var(--font) !important;
}

.stButton > button[kind="primary"]:hover {
    background: var(--c-btn-primary-hover) !important;
    box-shadow: 0 4px 14px var(--c-btn-primary-shadow) !important;
}

/* Sekundär-Buttons */
.stButton > button:not([kind="primary"]) {
    background: var(--c-btn-secondary-bg) !important;
    color: var(--c-btn-secondary-text) !important;
    border: 1px solid var(--c-btn-secondary-border) !important;
    border-radius: var(--r-s) !important;
    font-family: var(--font) !important;
}

/* ══════════════════════════════════════════════════════════════════
   MODAL / DIALOG
══════════════════════════════════════════════════════════════════ */

/* Backdrop-Abdunkelung hinter dem Dialog */
[data-testid="stModal"] > div:first-child {
    background: var(--c-modal-backdrop) !important;
    backdrop-filter: blur(4px);
}

/* Dialog-Fenster selbst */
[data-testid="stModal"] [role="dialog"],
div[class*="dialog"],
div[class*="Modal"] {
    background: var(--c-modal-bg) !important;
    color: var(--c-modal-text) !important;
    border: 1px solid var(--c-modal-border) !important;
    border-radius: var(--r) !important;
    box-shadow: 0 20px 60px var(--c-modal-shadow) !important;
}

/* Texte im Dialog – gezielt, kein * */
[data-testid="stModal"] p,
[data-testid="stModal"] label,
[data-testid="stModal"] span:not(.pos):not(.neg):not(.warn) {
    color: var(--c-modal-text) !important;
    font-family: var(--font) !important;
}

[data-testid="stModal"] h1,
[data-testid="stModal"] h2,
[data-testid="stModal"] h3 {
    color: var(--c-heading) !important;
    font-weight: 700 !important;
}

/* Formular-Hintergrund im Dialog */
[data-testid="stModal"] [data-testid="stForm"] {
    background: transparent !important;
}

/* X-Schließen-Button: heller Hintergrund, dunkles Icon */
[data-testid="stModal"] button[aria-label="Close"],
[data-testid="stModal"] button[title="Close"],
div[role="dialog"] button[aria-label="Close"],
div[role="dialog"] button[title="Close"] {
    background: var(--c-surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--c-text) !important;
}

[data-testid="stModal"] button[aria-label="Close"] svg,
[data-testid="stModal"] button[title="Close"] svg,
div[role="dialog"] button[aria-label="Close"] svg,
div[role="dialog"] button[title="Close"] svg {
    fill: var(--c-text) !important;
    stroke: var(--c-text) !important;
}

/* Primär-Button im Dialog */
[data-testid="stModal"] .stButton > button[kind="primary"],
[data-testid="stModal"] button[data-testid="stFormSubmitButton"][kind="primary"],
div[role="dialog"] .stButton > button[kind="primary"],
div[role="dialog"] button[data-testid="stFormSubmitButton"][kind="primary"] {
    background: var(--c-btn-primary-bg) !important;
    color: var(--c-btn-primary-text) !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: var(--r-s) !important;
}

[data-testid="stModal"] .stButton > button[kind="primary"]:hover,
div[role="dialog"] .stButton > button[kind="primary"]:hover {
    background: var(--c-btn-primary-hover) !important;
    box-shadow: 0 4px 14px var(--c-btn-primary-shadow) !important;
}

/* Sekundär-Button (Abbrechen) im Dialog */
[data-testid="stModal"] .stButton > button:not([kind="primary"]),
[data-testid="stModal"] button[data-testid="stFormSubmitButton"]:not([kind="primary"]),
div[role="dialog"] .stButton > button:not([kind="primary"]),
div[role="dialog"] button[data-testid="stFormSubmitButton"]:not([kind="primary"]) {
    background: var(--c-btn-secondary-bg) !important;
    color: var(--c-btn-secondary-text) !important;
    border: 1px solid var(--c-btn-secondary-border) !important;
    border-radius: var(--r-s) !important;
}

/* Trennlinie im Dialog */
[data-testid="stModal"] hr,
div[role="dialog"] hr {
    border-color: var(--c-divider) !important;
}

/* ══════════════════════════════════════════════════════════════════
   ALERT / INFO / WARNING / ERROR BOXEN
══════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: var(--r-s) !important;
    font-family: var(--font) !important;
}

/* Info-Box (blau) */
[data-testid="stAlert"][data-baseweb="notification"][kind="info"],
[data-testid="stModal"] [data-testid="stAlert"][data-type="info"] {
    background: var(--c-alert-info-bg) !important;
    border-left: 3px solid var(--c-alert-info-border) !important;
    color: var(--c-alert-info-text) !important;
}

/* Warn-Box (orange) */
[data-testid="stAlert"][kind="warning"] {
    background: var(--c-alert-warn-bg) !important;
    border-left: 3px solid var(--c-alert-warn-border) !important;
}

/* Fehler-Box (rot) */
[data-testid="stAlert"][kind="error"] {
    background: var(--c-alert-err-bg) !important;
    border-left: 3px solid var(--c-alert-err-border) !important;
}

/* ══════════════════════════════════════════════════════════════════
   DIVIDER / TRENNLINIEN
══════════════════════════════════════════════════════════════════ */
hr,
[data-testid="stDivider"] hr {
    border-color: var(--c-divider) !important;
}

/* ══════════════════════════════════════════════════════════════════
   LABEL-TEXTE (Widget-Bezeichnungen über Inputs, Selects etc.)
══════════════════════════════════════════════════════════════════ */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: var(--c-input-label) !important;
    font-weight: 500 !important;
    font-size: var(--font-size-sm) !important;
    font-family: var(--font) !important;
}

/* ══════════════════════════════════════════════════════════════════
   TABELLEN (st.dataframe)
══════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] th {
    background: var(--c-table-header-bg) !important;
    color: var(--c-table-header-text) !important;
    font-family: var(--font) !important;
    font-weight: 700 !important;
}

[data-testid="stDataFrame"] tr:nth-child(even) td {
    background: var(--c-table-row-even) !important;
}

[data-testid="stDataFrame"] tr:nth-child(odd) td {
    background: var(--c-table-row-odd) !important;
}

[data-testid="stDataFrame"] tr:hover td {
    background: var(--c-table-row-hover) !important;
}

/* ══════════════════════════════════════════════════════════════════
   WERTFARBEN-KLASSEN (für inline HTML in ui.py)
   Verwendung: class="pos" / class="neg" / class="warn"
══════════════════════════════════════════════════════════════════ */
.pos  { color: var(--value-pos) !important; font-weight: 600; }
.neg  { color: var(--value-neg) !important; font-weight: 600; }
.warn { color: var(--value-warn) !important; font-weight: 600; }

/* ══════════════════════════════════════════════════════════════════
   TABS (st.tabs)
══════════════════════════════════════════════════════════════════ */

/* Tab-Leiste Hintergrund */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--c-surface-2) !important;
    border-radius: var(--r) var(--r) 0 0 !important;
    padding: 4px 4px 0 !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 2px !important;
}

/* Einzelner inaktiver Tab */
[data-testid="stTabs"] button[role="tab"] {
    background: transparent !important;
    color: var(--c-text-muted) !important;
    font-family: var(--font) !important;
    font-weight: 500 !important;
    font-size: var(--font-size-sm) !important;
    border: none !important;
    border-radius: var(--r-s) var(--r-s) 0 0 !important;
    padding: 0.5rem 1.2rem !important;
}

/* Hover */
[data-testid="stTabs"] button[role="tab"]:hover {
    background: var(--c-surface) !important;
    color: var(--c-text) !important;
}

/* Aktiver Tab */
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: var(--c-surface) !important;
    color: var(--c-primary) !important;
    font-weight: 700 !important;
    border-bottom: 2px solid var(--c-primary) !important;
}

/* Tab-Text-Spans explizit färben */
[data-testid="stTabs"] button[role="tab"] p,
[data-testid="stTabs"] button[role="tab"] span {
    color: inherit !important;
    font-family: var(--font) !important;
}

/* Tab-Inhalt-Bereich */
[data-testid="stTabs"] [role="tabpanel"] {
    background: var(--c-surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r) var(--r) !important;
    padding: 1.2rem !important;
}

/* ══════════════════════════════════════════════════════════════════
   INTERNE WIDGET-BUTTONS
   Passwort-Auge, +/- Spinner, Abbrechen (form_submit_button)
   haben gemeinsam: kein .stButton-Wrapper oder kind=tertiary
══════════════════════════════════════════════════════════════════ */

/* Passwort-Sichtbarkeits-Toggle */
[data-testid="stTextInput"] button {
    background: var(--c-input-bg) !important;
    color: var(--c-text-muted) !important;
    border: none !important;
    border-radius: 0 var(--r-s) var(--r-s) 0 !important;
}
[data-testid="stTextInput"] button:hover {
    background: var(--c-surface-2) !important;
    color: var(--c-text) !important;
}
[data-testid="stTextInput"] button svg {
    fill: var(--c-text-muted) !important;
    stroke: var(--c-text-muted) !important;
}

/* Number-Input +/- Spinner */
[data-testid="stNumberInput"] button {
    background: var(--c-surface-2) !important;
    color: var(--c-text) !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stNumberInput"] button:hover {
    background: var(--c-btn-secondary-bg) !important;
}
[data-testid="stNumberInput"] button svg {
    fill: var(--c-text) !important;
    stroke: var(--c-text) !important;
}

/* form_submit_button ohne type=primary (Abbrechen-Button) */
[data-testid="stFormSubmitButton"] > button:not([kind="primary"]) {
    background: var(--c-btn-secondary-bg) !important;
    color: var(--c-btn-secondary-text) !important;
    border: 1px solid var(--c-btn-secondary-border) !important;
    border-radius: var(--r-s) !important;
}

/* ══════════════════════════════════════════════════════════════════
   RADIO BUTTONS (horizontal, z.B. Monatsumschaltung Dashboard)
══════════════════════════════════════════════════════════════════ */

/* Wrapper */
[data-testid="stRadio"] > div {
    background: var(--c-surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 4px 6px !important;
    gap: 4px !important;
    display: inline-flex !important;
}

/* Jede einzelne Radio-Option als Pill */
[data-testid="stRadio"] label {
    background: transparent !important;
    color: var(--c-seg-inactive-text) !important;
    font-family: var(--font) !important;
    font-weight: 500 !important;
    font-size: var(--font-size-sm) !important;
    border-radius: var(--r-s) !important;
    padding: 0.25rem 0.9rem !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
}

[data-testid="stRadio"] label:hover {
    background: var(--c-surface) !important;
    color: var(--c-text) !important;
}

/* Ausgewählte Option */
[data-testid="stRadio"] label:has(input:checked) {
    background: var(--c-seg-active-bg) !important;
    color: var(--c-seg-active-text) !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px var(--c-seg-active-shadow) !important;
}

/* Natives Radio-Kreis verstecken */
[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}

/* Text-Span in Label erbt Farbe */
[data-testid="stRadio"] label p,
[data-testid="stRadio"] label span {
    color: inherit !important;
    font-family: var(--font) !important;
}

/* Tertiary BaseWeb-Buttons (allgemeiner Fallback) */
button[kind="tertiary"],
[data-baseweb="button"][kind="tertiary"] {
    background: var(--c-surface-2) !important;
    color: var(--c-text) !important;
    border: 1px solid var(--border) !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────
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
        <div style="padding:1.4rem 0.5rem 1rem;
                    text-align:center;
                    border-bottom:1px solid var(--c-sidebar-divider);
                    margin-bottom:0.8rem;">
            <div style="width:48px;height:48px;border-radius:12px;
                        background:var(--c-sidebar-avatar-bg);
                        border:2px solid var(--c-sidebar-avatar-border);
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 0.7rem;
                        font-weight:800;
                        color:var(--c-sidebar-avatar-text);">
                {initials}
            </div>
            <div style="font-weight:700;color:var(--c-sidebar-text);">
                {display_name}
            </div>
            <div style="font-size:var(--font-size-xs);
                        color:var(--c-sidebar-text-muted);">
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
