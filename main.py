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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

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
   DESIGN-SYSTEM – ALLE KONFIGURIERBAREN WERTE
   ──────────────────────────────────────────────────────────────
   Hier ist die zentrale Schaltzentrale für das gesamte Layout.
   Ändere einen Wert hier → er wirkt sich überall aus.
══════════════════════════════════════════════════════════════════ */
:root {

    /* ── HAUPTFARBEN ──────────────────────────────────────────── */
    --c-primary:        #2F4F6F;   /* Gedämpftes Stahlblau – Hauptakzent */
    --c-bg:             #F3F5F8;   /* Sehr helles Blaugrau – App Hintergrund */
    --c-surface:        #FFFFFF;   /* Karten / Panels – reines Weiß */
    --c-surface-2:      #EEF1F6;   /* Sekundäre Flächen – leicht grau-blau */

    /* ── TEXTFARBEN ───────────────────────────────────────────── */
    --c-text:           #1F2933;   /* Haupttext – dunkles Slate */
    --c-text-2:         #334155;   /* Sekundärtext */
    --c-text-muted:     #7C8799;   /* Gedimmter Text */
    --c-heading:        #111827;   /* Überschriften – fast schwarz */
    --c-subheading:     #6B7280;   /* Untertitel */

    /* ── STATUSFARBEN ─────────────────────────────────────────── */
    --value-pos:        #2E7D32;   /* Gedämpftes Grün */
    --value-neg:        #C0392B;   /* Dunkles Ziegelrot */
    --value-warn:       #C77700;   /* Gedämpftes Orange */
    --value-neon:       #3A7CA5;   /* CTA Sidebar – ruhiges Blau */

    /* ── RAHMEN & RADIEN ──────────────────────────────────────── */
    --border:           rgba(47, 79, 111, 0.08);  /* Subtile Linien */
    --border-strong:    rgba(47, 79, 111, 0.22);  /* Stärkere Linien */
    --r:                12px;   /* Karten Radius */
    --r-s:              8px;    /* Buttons / Inputs */

    /* ── TYPOGRAFIE ───────────────────────────────────────────── */
    --font:             'Outfit', sans-serif;
    --font-size-base:   0.9rem;
    --font-size-sm:     0.82rem;
    --font-size-xs:     0.72rem;

    /* ── SIDEBAR ──────────────────────────────────────────────── */
    --c-sidebar-bg:             #1E293B;   /* Dunkles Slate */
    --c-sidebar-text:           rgba(255,255,255,0.92); /* Sidebar Text */
    --c-sidebar-text-muted:     rgba(255,255,255,0.45); /* Gedimmt */
    --c-sidebar-divider:        rgba(255,255,255,0.10); /* Divider */
    --c-sidebar-avatar-bg:      rgba(199,119,0,0.15);   /* Warmes Akzentfeld */
    --c-sidebar-avatar-border:  #C77700;   /* Avatar Rahmen */
    --c-sidebar-avatar-text:    #C77700;   /* Avatar Text */
    --c-sidebar-btn-cta-bg:     #3A7CA5;   /* CTA Button */
    --c-sidebar-btn-cta-text:   #FFFFFF;   /* CTA Text */

    /* ── EXPANDER ─────────────────────────────────────────────── */
    --c-expander-bg:            #FFFFFF;   /* Expander Body */
    --c-expander-header-bg:     #334155;   /* Expander Header */
    --c-expander-header-hover:  #2F4F6F;   /* Hover */
    --c-expander-header-text:   #FFFFFF;   /* Header Text */
    --c-expander-border:        rgba(47,79,111,0.08);

    /* ── METRIKEN / KPI ───────────────────────────────────────── */
    --c-metric-bg:          #FFFFFF;
    --c-metric-border:      rgba(47,79,111,0.08);
    --c-metric-value:       #111827;
    --c-metric-label:       #334155;
    --c-metric-delta-pos:   #2E7D32;
    --c-metric-delta-neg:   #C0392B;

    /* ── INPUTS ───────────────────────────────────────────────── */
    --c-input-bg:           #F3F5F8;   /* Input Hintergrund */
    --c-input-bg-focus:     #FFFFFF;   /* Fokus */
    --c-input-text:         #1F2933;
    --c-input-border:       rgba(47,79,111,0.25);
    --c-input-border-focus: #2F4F6F;
    --c-input-focus-ring:   rgba(47,79,111,0.15);
    --c-input-label:        #475569;

    /* ── DROPDOWNS ────────────────────────────────────────────── */
    --c-dropdown-bg:                #F3F5F8;
    --c-dropdown-text:              #1F2933;
    --c-dropdown-border:            rgba(47,79,111,0.25);
    --c-dropdown-list-bg:           #FFFFFF;
    --c-dropdown-list-border:       rgba(47,79,111,0.18);
    --c-dropdown-list-shadow:       rgba(0,0,0,0.10);
    --c-dropdown-option-text:       #1F2933;
    --c-dropdown-option-hover-bg:   rgba(47,79,111,0.08);
    --c-dropdown-option-hover-text: #2F4F6F;
    --c-dropdown-option-sel-bg:     rgba(47,79,111,0.12);

    /* ── SEGMENTED CONTROL ────────────────────────────────────── */
    --c-seg-bg:             rgba(47,79,111,0.06);
    --c-seg-active-bg:      #2F4F6F;
    --c-seg-active-text:    #FFFFFF;
    --c-seg-active-shadow:  rgba(47,79,111,0.25);
    --c-seg-inactive-text:  #475569;

    /* ── BUTTONS ──────────────────────────────────────────────── */
    --c-btn-primary-bg:         #2F4F6F;   /* Primärbutton */
    --c-btn-primary-text:       #FFFFFF;
    --c-btn-primary-hover:      #243B55;   /* Dunkler Hover */
    --c-btn-primary-shadow:     rgba(47,79,111,0.35);
    --c-btn-secondary-bg:       #E8EDF3;   /* Sekundär hell */
    --c-btn-secondary-text:     #475569;
    --c-btn-secondary-border:   rgba(47,79,111,0.20);

    /* ── MODAL ───────────────────────────────────────────────── */
    --c-modal-bg:       #FFFFFF;
    --c-modal-text:     #1F2933;
    --c-modal-border:   rgba(47,79,111,0.15);
    --c-modal-shadow:   rgba(0,0,0,0.18);
    --c-modal-backdrop: rgba(15,23,42,0.55); /* Dunkle Abdunklung */

    /* ── LISTEN ───────────────────────────────────────────────── */
    --c-list-bg:            #EEF1F6;
    --c-list-border:        rgba(47,79,111,0.12);
    --c-list-row-divider:   rgba(47,79,111,0.08);
    --c-list-text-primary:  #111827;
    --c-list-text-sub:      #6B7280;

    /* ── BADGES ───────────────────────────────────────────────── */
    --c-badge-turnus-bg:     rgba(199,119,0,0.12);
    --c-badge-turnus-text:   #C77700;
    --c-badge-turnus-border: rgba(199,119,0,0.30);
    --c-badge-konto-bg:      rgba(47,79,111,0.10);
    --c-badge-konto-text:    #2F4F6F;
    --c-badge-konto-border:  rgba(47,79,111,0.20);
    --c-badge-count-bg:      rgba(47,79,111,0.10);
    --c-badge-count-text:    #2F4F6F;

    /* ── ALERTS ───────────────────────────────────────────────── */
    --c-alert-info-bg:      rgba(47,79,111,0.07);
    --c-alert-info-border:  #2F4F6F;
    --c-alert-info-text:    #1F2933;
    --c-alert-warn-bg:      rgba(199,119,0,0.08);
    --c-alert-warn-border:  #C77700;
    --c-alert-err-bg:       rgba(192,57,43,0.08);
    --c-alert-err-border:   #C0392B;

    /* ── DIVIDER ─────────────────────────────────────────────── */
    --c-divider:        rgba(47,79,111,0.12);

    /* ── TABELLEN ────────────────────────────────────────────── */
    --c-table-header-bg:    rgba(47,79,111,0.06);
    --c-table-header-text:  #2F4F6F;
    --c-table-row-even:     #FFFFFF;
    --c-table-row-odd:      #F3F5F8;
    --c-table-row-hover:    rgba(47,79,111,0.05);

    /* ── EMPTY STATE ─────────────────────────────────────────── */
    --c-empty-bg:       rgba(47,79,111,0.04);
    --c-empty-border:   rgba(47,79,111,0.20);
    --c-empty-text:     #6B7280;

    /* ── VALUE PILLS ─────────────────────────────────────────── */
    --c-pill-pos-bg:        rgba(46,125,50,0.10);
    --c-pill-pos-border:    rgba(46,125,50,0.25);
    --c-pill-neg-bg:        rgba(192,57,43,0.10);
    --c-pill-neg-border:    rgba(192,57,43,0.25);

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
    font-weight: 800;
    font-family: var(--font) !important;
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
}

/* Inaktive Segmente */
[data-testid="stSegmentedControl"] button {
    background: transparent !important;
    color: var(--c-seg-inactive-text) !important;
    border-radius: var(--r-s) !important;
    font-weight: 500 !important;
    border: none !important;
    font-family: var(--font) !important;
}

/* Aktives / ausgewähltes Segment */
[data-testid="stSegmentedControl"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[data-active="true"] {
    background: var(--c-seg-active-bg) !important;
    color: var(--c-seg-active-text) !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px var(--c-seg-active-shadow) !important;
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

/* Alle Texte im Dialog */
[data-testid="stModal"] *,
[data-testid="stModal"] p,
[data-testid="stModal"] label,
[data-testid="stModal"] span:not(.pos):not(.neg):not(.warn),
[data-testid="stModal"] div {
    color: var(--c-modal-text) !important;
    font-family: var(--font) !important;
}

/* Überschriften im Dialog */
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

/* Primär-Button im Dialog */
[data-testid="stModal"] .stButton > button[kind="primary"],
[data-testid="stModal"] button[data-testid="stFormSubmitButton"][kind="primary"] {
    background: var(--c-btn-primary-bg) !important;
    color: var(--c-btn-primary-text) !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: var(--r-s) !important;
}

[data-testid="stModal"] .stButton > button[kind="primary"]:hover {
    background: var(--c-btn-primary-hover) !important;
    box-shadow: 0 4px 14px var(--c-btn-primary-shadow) !important;
}

/* Sekundär-Button (Abbrechen) im Dialog */
[data-testid="stModal"] .stButton > button:not([kind="primary"]) {
    background: var(--c-btn-secondary-bg) !important;
    color: var(--c-btn-secondary-text) !important;
    border: 1px solid var(--c-btn-secondary-border) !important;
    border-radius: var(--r-s) !important;
}

/* Trennlinie im Dialog */
[data-testid="stModal"] hr {
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
