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

    /* ── HAUPTFARBEN ────────────────────────────────────────────
       --c-primary   : Akzentfarbe für Buttons, Links, aktive Elemente
       --c-bg        : Hintergrundfarbe der gesamten App
       --c-surface   : Hintergrund für Karten, Panels, Eingabefelder
       --c-surface-2 : Leicht abgehobene Fläche (Listenzeilen, Tabellen-BG)
    ──────────────────────────────────────────────────────────── */
    --c-primary:        #1B3A6B;
    --c-bg:             #F8F9FA;
    --c-surface:        #FFFFFF;
    --c-surface-2:      #F4F5F9;

    /* ── TEXTFARBEN ─────────────────────────────────────────────
       --c-text        : Haupttext (Überschriften, Werte, Labels)
       --c-text-2      : Sekundärtext (Unterzeilen, Beschreibungen)
       --c-text-muted  : Gedimmter Text (Metainfos, Zeitstempel)
       --c-heading     : Seitenüberschriften (h1)
       --c-subheading  : Untertitel unter Seitenüberschriften
    ──────────────────────────────────────────────────────────── */
    --c-text:           #1E293B;
    --c-text-2:         #2D3748;
    --c-text-muted:     #7A84A0;
    --c-heading:        #1A1F2E;
    --c-subheading:     #8892AA;

    /* ── STATUSFARBEN ───────────────────────────────────────────
       --value-pos  : Einnahmen, positive Salden, Erfolgsmeldungen
       --value-neg  : Ausgaben, negative Salden, Fehlermeldungen
       --value-warn : Warnungen, ausstehende Posten, Avatar-Rahmen
       --value-neon : CTA-Button in der Sidebar ("Neuer Eintrag")
    ──────────────────────────────────────────────────────────── */
    --value-pos:        #2BB34F;
    --value-neg:        #F44336;
    --value-warn:       #FF9800;
    --value-neon:       #39D353;

    /* ── RAHMEN & RADIEN ────────────────────────────────────────
       --border        : Standard-Rahmenfarbe (subtil, für Trennlinien)
       --border-strong : Stärkerer Rahmen (Inputs im Fokus, Karten)
       --r             : Großer Border-Radius (Karten, Dialoge, Panels)
       --r-s           : Kleiner Border-Radius (Buttons, Inputs, Badges)
    ──────────────────────────────────────────────────────────── */
    --border:           rgba(27, 58, 107, 0.08);
    --border-strong:    rgba(27, 58, 107, 0.20);
    --r:                12px;
    --r-s:              8px;

    /* ── TYPOGRAFIE ─────────────────────────────────────────────
       --font          : Schriftart der gesamten App
       --font-size-base: Basisgröße für Fließtext
       --font-size-sm  : Kleine Texte (Labels, Badges, Metainfos)
       --font-size-xs  : Sehr kleine Texte (Zeitstempel, Einheiten)
    ──────────────────────────────────────────────────────────── */
    --font:             'Outfit', sans-serif;
    --font-size-base:   0.9rem;
    --font-size-sm:     0.82rem;
    --font-size-xs:     0.72rem;

    /* ── SIDEBAR ────────────────────────────────────────────────
       --c-sidebar-bg          : Hintergrund der linken Navigationsleiste
       --c-sidebar-text        : Textfarbe aller Elemente in der Sidebar
       --c-sidebar-text-muted  : Gedimmter Text (z.B. @username)
       --c-sidebar-divider     : Trennlinie unter dem User-Avatar-Block
       --c-sidebar-avatar-bg   : Hintergrund des Initialen-Quadrats
       --c-sidebar-avatar-border: Rahmen des Initialen-Quadrats
       --c-sidebar-avatar-text : Textfarbe der Initialen
       --c-sidebar-btn-cta-bg  : Hintergrund "Neuer Eintrag"-Button
       --c-sidebar-btn-cta-text: Textfarbe "Neuer Eintrag"-Button
    ──────────────────────────────────────────────────────────── */
    --c-sidebar-bg:             #1B3A6B;
    --c-sidebar-text:           rgba(255, 255, 255, 0.90);
    --c-sidebar-text-muted:     rgba(255, 255, 255, 0.35);
    --c-sidebar-divider:        rgba(255, 255, 255, 0.10);
    --c-sidebar-avatar-bg:      rgba(255, 152, 0, 0.15);
    --c-sidebar-avatar-border:  #FF9800;
    --c-sidebar-avatar-text:    #FF9800;
    --c-sidebar-btn-cta-bg:     #39D353;
    --c-sidebar-btn-cta-text:   #0A1F0D;

    /* ── EXPANDER ───────────────────────────────────────────────
       --c-expander-bg          : Hintergrund des aufgeklappten Inhaltsbereichs
       --c-expander-header-bg   : Hintergrund der Titelzeile (eingeklappt)
       --c-expander-header-hover: Hintergrund beim Hover über die Titelzeile
       --c-expander-header-text : Textfarbe der Titelzeile
       --c-expander-border      : Rahmen des gesamten Expanders
    ──────────────────────────────────────────────────────────── */
    --c-expander-bg:            #FFFFFF;
    --c-expander-header-bg:     #2D3748;
    --c-expander-header-hover:  #1B3A6B;
    --c-expander-header-text:   #FFFFFF;
    --c-expander-border:        rgba(27, 58, 107, 0.08);

    /* ── METRIKEN / KPI-CARDS ───────────────────────────────────
       --c-metric-bg      : Kartenhintergrund der KPI-Kacheln
       --c-metric-border  : Rahmen der KPI-Kacheln
       --c-metric-value   : Farbe des großen Zahlenwerts
       --c-metric-label   : Farbe des Beschriftungstexts über dem Wert
       --c-metric-delta-pos: Deltafarbe wenn positiv (Pfeil + Zahl)
       --c-metric-delta-neg: Deltafarbe wenn negativ
    ──────────────────────────────────────────────────────────── */
    --c-metric-bg:          #FFFFFF;
    --c-metric-border:      rgba(27, 58, 107, 0.08);
    --c-metric-value:       #1E293B;
    --c-metric-label:       #2D3748;
    --c-metric-delta-pos:   #2BB34F;
    --c-metric-delta-neg:   #F44336;

    /* ── INPUTS & FORMFELDER ────────────────────────────────────
       --c-input-bg          : Hintergrund von Textfeldern, Number-Inputs
       --c-input-bg-focus    : Hintergrund wenn das Feld aktiv ist
       --c-input-text        : Eingabetext-Farbe
       --c-input-border      : Rahmen im Normalzustand
       --c-input-border-focus: Rahmen wenn aktiv (Fokus)
       --c-input-focus-ring  : Leuchtring um aktives Eingabefeld
       --c-input-label       : Farbe der Feldbezeichnung über dem Input
    ──────────────────────────────────────────────────────────── */
    --c-input-bg:           #F8F9FA;
    --c-input-bg-focus:     #FFFFFF;
    --c-input-text:         #1E293B;
    --c-input-border:       rgba(27, 58, 107, 0.20);
    --c-input-border-focus: #1B3A6B;
    --c-input-focus-ring:   rgba(27, 58, 107, 0.12);
    --c-input-label:        #4A5270;

    /* ── DROPDOWNS / SELECTBOX ──────────────────────────────────
       --c-dropdown-bg              : Hintergrund des geschlossenen Dropdowns
       --c-dropdown-text            : Text im geschlossenen Dropdown
       --c-dropdown-border          : Rahmen des geschlossenen Dropdowns
       --c-dropdown-list-bg         : Hintergrund der aufgeklappten Optionsliste
       --c-dropdown-list-border     : Rahmen der aufgeklappten Optionsliste
       --c-dropdown-list-shadow     : Schatten der aufgeklappten Liste
       --c-dropdown-option-text     : Textfarbe einer einzelnen Option
       --c-dropdown-option-hover-bg : Hintergrund beim Hover über eine Option
       --c-dropdown-option-hover-text: Textfarbe beim Hover
       --c-dropdown-option-sel-bg   : Hintergrund der ausgewählten Option
    ──────────────────────────────────────────────────────────── */
    --c-dropdown-bg:                #F8F9FA;
    --c-dropdown-text:              #1E293B;
    --c-dropdown-border:            rgba(27, 58, 107, 0.20);
    --c-dropdown-list-bg:           #FFFFFF;
    --c-dropdown-list-border:       rgba(27, 58, 107, 0.15);
    --c-dropdown-list-shadow:       rgba(0, 0, 0, 0.12);
    --c-dropdown-option-text:       #1E293B;
    --c-dropdown-option-hover-bg:   rgba(27, 58, 107, 0.08);
    --c-dropdown-option-hover-text: #1B3A6B;
    --c-dropdown-option-sel-bg:     rgba(27, 58, 107, 0.10);

    /* ── SEGMENTED CONTROL ──────────────────────────────────────
       --c-seg-bg           : Hintergrund der gesamten Schalterleiste
       --c-seg-active-bg    : Hintergrund des aktiven/gewählten Segments
       --c-seg-active-text  : Textfarbe des aktiven Segments
       --c-seg-active-shadow: Schatten unter dem aktiven Segment
       --c-seg-inactive-text: Textfarbe der inaktiven Segmente
    ──────────────────────────────────────────────────────────── */
    --c-seg-bg:             rgba(27, 58, 107, 0.06);
    --c-seg-active-bg:      #1B3A6B;
    --c-seg-active-text:    #FFFFFF;
    --c-seg-active-shadow:  rgba(27, 58, 107, 0.25);
    --c-seg-inactive-text:  #4A5270;

    /* ── BUTTONS ────────────────────────────────────────────────
       --c-btn-primary-bg      : Hintergrund primärer Button (Speichern etc.)
       --c-btn-primary-text    : Textfarbe primärer Button
       --c-btn-primary-hover   : Hintergrund beim Hover
       --c-btn-primary-shadow  : Schatten beim Hover
       --c-btn-secondary-bg    : Hintergrund sekundärer Button (Abbrechen etc.)
       --c-btn-secondary-text  : Textfarbe sekundärer Button
       --c-btn-secondary-border: Rahmen sekundärer Button
    ──────────────────────────────────────────────────────────── */
    --c-btn-primary-bg:         #1B3A6B;
    --c-btn-primary-text:       #FFFFFF;
    --c-btn-primary-hover:      #142D54;
    --c-btn-primary-shadow:     rgba(27, 58, 107, 0.35);
    --c-btn-secondary-bg:       #F1F3F7;
    --c-btn-secondary-text:     #4A5270;
    --c-btn-secondary-border:   rgba(27, 58, 107, 0.15);

    /* ── MODAL / DIALOG ─────────────────────────────────────────
       --c-modal-bg       : Hintergrund des Dialog-Fensters
       --c-modal-text     : Textfarbe im Dialog
       --c-modal-border   : Rahmen des Dialog-Fensters
       --c-modal-shadow   : Schatten hinter dem Dialog
       --c-modal-backdrop : Abdunklungsfarbe hinter dem Dialog
    ──────────────────────────────────────────────────────────── */
    --c-modal-bg:       #FFFFFF;
    --c-modal-text:     #1E293B;
    --c-modal-border:   rgba(27, 58, 107, 0.12);
    --c-modal-shadow:   rgba(0, 0, 0, 0.18);
    --c-modal-backdrop: rgba(10, 20, 50, 0.55);

    /* ── LISTEN-ZEILEN (Banking-Style) ──────────────────────────
       --c-list-bg          : Hintergrund des gesamten Listen-Containers
       --c-list-border      : Außenrahmen des Listen-Containers
       --c-list-row-divider : Trennlinie zwischen einzelnen Zeilen
       --c-list-text-primary: Haupttext einer Zeile (Name, Zweck)
       --c-list-text-sub    : Unterzeile (Konto, Kategorie, Datum)
    ──────────────────────────────────────────────────────────── */
    --c-list-bg:            #F4F5F9;
    --c-list-border:        rgba(27, 58, 107, 0.11);
    --c-list-row-divider:   rgba(27, 58, 107, 0.08);
    --c-list-text-primary:  #1A1F2E;
    --c-list-text-sub:      #7A84A0;

    /* ── BADGES / PILLS ─────────────────────────────────────────
       --c-badge-turnus-bg    : Hintergrund Turnus-Badge (z.B. "Quartalsweise")
       --c-badge-turnus-text  : Textfarbe Turnus-Badge
       --c-badge-turnus-border: Rahmen Turnus-Badge
       --c-badge-konto-bg     : Hintergrund Kontotyp-Badge ("Bankkonto")
       --c-badge-konto-text   : Textfarbe Kontotyp-Badge
       --c-badge-konto-border : Rahmen Kontotyp-Badge
       --c-badge-count-bg     : Hintergrund Zähl-Badge bei Section-Labels
       --c-badge-count-text   : Textfarbe Zähl-Badge
    ──────────────────────────────────────────────────────────── */
    --c-badge-turnus-bg:        rgba(240, 120, 0, 0.12);
    --c-badge-turnus-text:      #F07800;
    --c-badge-turnus-border:    rgba(240, 120, 0, 0.25);
    --c-badge-konto-bg:         rgba(27, 58, 107, 0.10);
    --c-badge-konto-text:       #1B3A6B;
    --c-badge-konto-border:     rgba(27, 58, 107, 0.20);
    --c-badge-count-bg:         rgba(27, 58, 107, 0.10);
    --c-badge-count-text:       #1B3A6B;

    /* ── ALERT / INFO-BOXEN ─────────────────────────────────────
       --c-alert-info-bg    : Hintergrund blauer Info-Hinweis
       --c-alert-info-border: Linker Akzentstreifen Info-Hinweis
       --c-alert-info-text  : Textfarbe Info-Hinweis
       --c-alert-warn-bg    : Hintergrund gelbe Warnmeldung
       --c-alert-warn-border: Linker Akzentstreifen Warnmeldung
       --c-alert-err-bg     : Hintergrund rote Fehlermeldung
       --c-alert-err-border : Linker Akzentstreifen Fehlermeldung
    ──────────────────────────────────────────────────────────── */
    --c-alert-info-bg:      rgba(27, 58, 107, 0.07);
    --c-alert-info-border:  #1B3A6B;
    --c-alert-info-text:    #1A1F2E;
    --c-alert-warn-bg:      rgba(255, 152, 0, 0.08);
    --c-alert-warn-border:  #FF9800;
    --c-alert-err-bg:       rgba(244, 67, 54, 0.07);
    --c-alert-err-border:   #F44336;

    /* ── SEITEN-HEADER & SECTION-LABELS ─────────────────────────
       --c-page-header-border : Trennlinie unter dem Seitentitel
       --c-section-dot        : Farbpunkt vor Section-Überschriften
                                (wird in ui.py per Parameter übergeben,
                                 dieser Wert ist der globale Fallback)
    ──────────────────────────────────────────────────────────── */
    --c-page-header-border: rgba(27, 58, 107, 0.12);
    --c-section-dot:        #1B3A6B;

    /* ── LEERER ZUSTAND (Empty State) ───────────────────────────
       --c-empty-bg    : Hintergrund der "Keine Einträge"-Box
       --c-empty-border: Gestrichelter Rahmen der Empty-State-Box
       --c-empty-text  : Textfarbe der Meldung
    ──────────────────────────────────────────────────────────── */
    --c-empty-bg:       rgba(27, 58, 107, 0.04);
    --c-empty-border:   rgba(27, 58, 107, 0.18);
    --c-empty-text:     #4A5270;

    /* ── DIVIDER / TRENNLINIEN ──────────────────────────────────
       --c-divider : Farbe horizontaler Trennlinien (st.divider())
    ──────────────────────────────────────────────────────────── */
    --c-divider:        rgba(27, 58, 107, 0.10);

    /* ── TABELLEN (st.dataframe) ────────────────────────────────
       --c-table-header-bg  : Hintergrund der Kopfzeile
       --c-table-header-text: Textfarbe der Kopfzeile
       --c-table-row-even   : Hintergrund gerader Zeilen
       --c-table-row-odd    : Hintergrund ungerader Zeilen
       --c-table-row-hover  : Hintergrund beim Hover über eine Zeile
    ──────────────────────────────────────────────────────────── */
    --c-table-header-bg:    rgba(27, 58, 107, 0.06);
    --c-table-header-text:  #1B3A6B;
    --c-table-row-even:     #FFFFFF;
    --c-table-row-odd:      #F8F9FA;
    --c-table-row-hover:    rgba(27, 58, 107, 0.04);

    /* ── SELECTIONS-BALKEN ──────────────────────────────────────
       --c-selection-text   : "Ausgewählt"-Label rechts im Balken
       (Vorder- und Hintergrundfarbe des Balkens selbst werden
        dynamisch aus der jeweiligen Akzentfarbe berechnet)
    ──────────────────────────────────────────────────────────── */
    --c-selection-text:     #8892AA;

    /* ── WERT-PILLS (Dashboard inline) ─────────────────────────
       --c-pill-pos-bg    : Hintergrund positiver Wert-Pill
       --c-pill-pos-border: Rahmen positiver Wert-Pill
       --c-pill-neg-bg    : Hintergrund negativer Wert-Pill
       --c-pill-neg-border: Rahmen negativer Wert-Pill
    ──────────────────────────────────────────────────────────── */
    --c-pill-pos-bg:        rgba(28, 158, 58, 0.10);
    --c-pill-pos-border:    rgba(28, 158, 58, 0.25);
    --c-pill-neg-bg:        rgba(214, 59, 59, 0.10);
    --c-pill-neg-border:    rgba(214, 59, 59, 0.20);

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
