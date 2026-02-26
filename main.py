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

/* ═════════════════════════════════════════════
   HAUPTFARBEN
═════════════════════════════════════════════ */

--c-primary:        #1F6F78;   /* Petrol – Hauptakzent */
--c-bg:             #F4F1EA;   /* Warmes Off-White – App Hintergrund */
--c-surface:        #FFFFFF;   /* Karten / Panels */
--c-surface-2:      #EAE5DC;   /* Sekundäre Flächen */

/* ═════════════════════════════════════════════
   TEXT
═════════════════════════════════════════════ */

--c-text:           #2C2A28;   /* Haupttext – warmes Anthrazit */
--c-text-2:         #3A3733;   /* Sekundärtext */
--c-text-muted:     #8A8278;   /* Gedimmter Text */
--c-heading:        #1E1C19;   /* Überschriften */
--c-subheading:     #6F675E;   /* Untertitel */

/* ═════════════════════════════════════════════
   STATUS
═════════════════════════════════════════════ */

--value-pos:        #4C7A3F;   /* Moosgrün */
--value-neg:        #8E2F2F;   /* Bordeaux */
--value-warn:       #B7791F;   /* Warmes Ocker */
--value-neon:       #1F6F78;   /* CTA – Petrol */

/* ═════════════════════════════════════════════
   RAHMEN
═════════════════════════════════════════════ */

--border:           #D9D2C7;   /* Weicher Steinrahmen */
--border-strong:    #BFB6A8;   /* Stärkerer Rahmen */
--r:                12px;
--r-s:              8px;

/* ═════════════════════════════════════════════
   TYPO
═════════════════════════════════════════════ */

--font: 'Inter', 'Roboto', sans-serif;
--font-size-base:   0.9rem;
--font-size-sm:     0.82rem;
--font-size-xs:     0.72rem;

/* ═════════════════════════════════════════════
   SIDEBAR
═════════════════════════════════════════════ */

--c-sidebar-bg:             #2B2622;   /* Dunkles Espresso */
--c-sidebar-text:           #F4F1EA;   /* Heller Kontrast */
--c-sidebar-text-muted:     #B7AEA3;   /* Gedimmtes Beige */
--c-sidebar-divider:        #3B342E;   /* Dunkler Divider */
--c-sidebar-avatar-bg:      #3A332D;   /* Avatar Hintergrund */
--c-sidebar-avatar-border:  #B7791F;   /* Ocker Rahmen */
--c-sidebar-avatar-text:    #D6A756;   /* Goldener Text */
--c-sidebar-btn-cta-bg:     #1F6F78;   /* Petrol CTA */
--c-sidebar-btn-cta-text:   #FFFFFF;   /* Weißer Text */

/* ═════════════════════════════════════════════
   EXPANDER
═════════════════════════════════════════════ */

--c-expander-bg:            #FFFFFF;
--c-expander-header-bg:     #3A3733;   /* Warmes Dunkel */
--c-expander-header-hover:  #1F6F78;   /* Petrol Hover */
--c-expander-header-text:   #FFFFFF;
--c-expander-border:        #D9D2C7;

/* ═════════════════════════════════════════════
   METRICS
═════════════════════════════════════════════ */

--c-metric-bg:          #FFFFFF;
--c-metric-border:      #D9D2C7;
--c-metric-value:       #1E1C19;
--c-metric-label:       #6F675E;
--c-metric-delta-pos:   #4C7A3F;
--c-metric-delta-neg:   #8E2F2F;

/* ═════════════════════════════════════════════
   INPUTS
═════════════════════════════════════════════ */

--c-input-bg:           #F8F6F1;
--c-input-bg-focus:     #FFFFFF;
--c-input-text:         #2C2A28;
--c-input-border:       #CFC6B8;
--c-input-border-focus: #1F6F78;
--c-input-focus-ring:   #CDE3E6;   /* Helles Petrol */
--c-input-label:        #5C544C;

/* ═════════════════════════════════════════════
   DROPDOWN
═════════════════════════════════════════════ */

--c-dropdown-bg:                #F8F6F1;
--c-dropdown-text:              #2C2A28;
--c-dropdown-border:            #CFC6B8;
--c-dropdown-list-bg:           #FFFFFF;
--c-dropdown-list-border:       #D9D2C7;
--c-dropdown-list-shadow:       rgba(0,0,0,0.12);
--c-dropdown-option-text:       #2C2A28;
--c-dropdown-option-hover-bg:   #E6F0F1;
--c-dropdown-option-hover-text: #1F6F78;
--c-dropdown-option-sel-bg:     #DCEBED;

/* ═════════════════════════════════════════════
   SEGMENTED CONTROL
═════════════════════════════════════════════ */

--c-seg-bg:             #EAE5DC;
--c-seg-active-bg:      #1F6F78;
--c-seg-active-text:    #FFFFFF;
--c-seg-active-shadow:  rgba(0,0,0,0.18);
--c-seg-inactive-text:  #5C544C;

/* ═════════════════════════════════════════════
   BUTTONS
═════════════════════════════════════════════ */

--c-btn-primary-bg:         #1F6F78;
--c-btn-primary-text:       #FFFFFF;
--c-btn-primary-hover:      #16555C;
--c-btn-primary-shadow:     rgba(0,0,0,0.20);
--c-btn-secondary-bg:       #EAE5DC;
--c-btn-secondary-text:     #5C544C;
--c-btn-secondary-border:   #CFC6B8;

/* ═════════════════════════════════════════════
   MODAL
═════════════════════════════════════════════ */

--c-modal-bg:       #FFFFFF;
--c-modal-text:     #2C2A28;
--c-modal-border:   #D9D2C7;
--c-modal-shadow:   rgba(0,0,0,0.25);
--c-modal-backdrop: rgba(0,0,0,0.55);

/* ═════════════════════════════════════════════
   LISTEN
═════════════════════════════════════════════ */

--c-list-bg:            #F1ECE3;
--c-list-border:        #D9D2C7;
--c-list-row-divider:   #E0D9CF;
--c-list-text-primary:  #1E1C19;
--c-list-text-sub:      #6F675E;

/* ═════════════════════════════════════════════
   BADGES
═════════════════════════════════════════════ */

--c-badge-turnus-bg:        #F3E3C8;
--c-badge-turnus-text:      #B7791F;
--c-badge-turnus-border:    #D6B47A;
--c-badge-konto-bg:         #DCEBED;
--c-badge-konto-text:       #1F6F78;
--c-badge-konto-border:     #A8CDD1;
--c-badge-count-bg:         #EAE5DC;
--c-badge-count-text:       #5C544C;

/* ═════════════════════════════════════════════
   ALERTS
═════════════════════════════════════════════ */

--c-alert-info-bg:      #E6F0F1;
--c-alert-info-border:  #1F6F78;
--c-alert-info-text:    #2C2A28;
--c-alert-warn-bg:      #F8E7C9;
--c-alert-warn-border:  #B7791F;
--c-alert-err-bg:       #F3D6D6;
--c-alert-err-border:   #8E2F2F;

/* ═════════════════════════════════════════════
   HEADER / SECTION
═════════════════════════════════════════════ */

--c-page-header-border: #D9D2C7;
--c-section-dot:        #1F6F78;

/* ═════════════════════════════════════════════
   EMPTY STATE
═════════════════════════════════════════════ */

--c-empty-bg:       #F1ECE3;
--c-empty-border:   #CFC6B8;
--c-empty-text:     #6F675E;

/* ═════════════════════════════════════════════
   DIVIDER
═════════════════════════════════════════════ */

--c-divider:        #D9D2C7;

/* ═════════════════════════════════════════════
   TABLE
═════════════════════════════════════════════ */

--c-table-header-bg:    #EAE5DC;
--c-table-header-text:  #3A3733;
--c-table-row-even:     #FFFFFF;
--c-table-row-odd:      #F4F1EA;
--c-table-row-hover:    #E6F0F1;

/* ═════════════════════════════════════════════
   SELECTION BAR
═════════════════════════════════════════════ */

--c-selection-text:     #6F675E;

/* ═════════════════════════════════════════════
   VALUE PILLS
═════════════════════════════════════════════ */

--c-pill-pos-bg:        #E4F0E1;
--c-pill-pos-border:    #A7C59F;
--c-pill-neg-bg:        #F3D6D6;
--c-pill-neg-border:    #C99A9A;

/* Dialog Register */
--c-dialog-seg-bg: #E9E6E1;          /* Container */
--c-dialog-seg-hover: #DCD7CF;       /* Hover */
--c-dialog-seg-active: #C7BDAF;      /* Active Hintergrund */
--c-dialog-seg-active-text: #3F3A33; /* Active Text */

/* Dialog Buttons */
--c-dialog-btn-bg: #4A5560;          /* Primärbutton */
--c-dialog-btn-text: #FFFFFF;
--c-dialog-btn-hover: #3C4650;

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
