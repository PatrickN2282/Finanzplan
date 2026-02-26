import sys
sys.path.append('.')
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from db import format_euro, get_conn
from forecast import calculate_months

# ══════════════════════════════════════════════════════════════════
# FARB-PALETTE – muss mit den CSS :root-Variablen in main.py übereinstimmen
# Diese Werte werden für Plotly-Charts und dynamische inline-HTML-Farben
# verwendet, da Plotly keine CSS-Variablen lesen kann.
# Wenn du eine Farbe in main.py änderst → hier ebenfalls anpassen!
# ══════════════════════════════════════════════════════════════════

# Hauptakzentfarbe (--c-primary)
_MARINE  = "#1B3A6B"

# CTA / Neon-Grün (--value-neon) – für Saldo-Linie im Chart
_NEON    = "#39D353"

# Akzent Orange (--value-warn) – für Abos, Turnus-Badges
_ORANGE  = "#F07800"

# Statusfarben (--value-neg / --value-pos)
_RED     = "#D63B3B"
_GREEN   = "#1C9E3A"

# Sekundäre Textfarbe für Chart-Achsen (--c-text-muted)
_CHART_TEXT = "#4A5270"

# Gitterlinien-Farbe in Charts
_CHART_GRID = "rgba(0,0,0,0.06)"

# ── Plotly-Layout-Basis ──────────────────────────────────────────
# paper_bgcolor / plot_bgcolor transparent → App-Hintergrund scheint durch
_PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Ubuntu, sans-serif', color=_CHART_TEXT, size=12),
    margin=dict(t=44, b=52, l=8, r=8),
    legend=dict(orientation="h", yanchor="bottom", y=-0.32,
                font=dict(size=11)),
    xaxis=dict(gridcolor=_CHART_GRID, tickfont=dict(size=11)),
    yaxis=dict(gridcolor=_CHART_GRID, tickfont=dict(size=11), tickformat=',.0f'),
)


def get_emoji(art, typ):
    if art == "Buchung":  return "💰" if typ == "Einnahme" else "💸"
    if art == "Abo":      return "🔄"
    if art == "Finanzierung": return "📉"
    return "❓"


def _row_style(row):
    """Zeilen-Hintergrundfarbe für st.dataframe:
       Einnahmen → dezentes Grün  (--value-pos mit Transparenz)
       Ausgaben  → dezentes Rot   (--value-neg mit Transparenz)
       Nicht fällig → ausgegraut  (--c-text-muted)
    """
    if row['Typ_Internal'] == 'Einnahme':
        bg = 'background-color:rgba(43,179,79,0.06)'   # --value-pos
    else:
        bg = 'background-color:rgba(244,67,54,0.05)'   # --value-neg
    txt = 'font-weight:500' if row['Ist_Fällig'] else 'color:#94A3B8;font-style:italic'
    return [f'{bg};{txt}'] * len(row)


def _page_header(title: str, subtitle: str = ""):
    """Einheitlicher Seitenkopf mit Titel und optionalem Untertitel.
       Farben: --c-heading, --c-subheading, --c-page-header-border
    """
    sub_html = (
        f'<p style="color:var(--c-subheading);margin:0.15rem 0 0;'
        f'font-size:var(--font-size-sm);font-weight:400;">{subtitle}</p>'
    ) if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:1.4rem;padding-bottom:1rem;
                border-bottom:1px solid var(--c-page-header-border);">
        <h1 style="font-family:var(--font);font-weight:800;font-size:1.75rem;
                   letter-spacing:-0.03em;margin:0;color:var(--c-heading);">{title}</h1>
        {sub_html}
    </div>""", unsafe_allow_html=True)


def _section_label(text: str, color: str = _MARINE, count: int = None):
    """Kleine Section-Überschrift mit Farbpunkt und optionalem Zähl-Badge.
       Farbpunkt-Farbe: wird per Parameter übergeben (Standard: --c-primary / _MARINE)
       Badge: --c-badge-count-bg / --c-badge-count-text
       Überschriften-Text: --c-heading
    """
    badge = ""
    if count is not None:
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        badge = (
            f'<span style="background:var(--c-badge-count-bg);'
            f'color:var(--c-badge-count-text);'
            f'border:1px solid rgba({r},{g},{b},0.25);border-radius:20px;'
            f'padding:1px 9px;font-size:var(--font-size-xs);font-weight:700;margin-left:0.5rem;">'
            f'{count}</span>'
        )
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.5rem;margin:1.1rem 0 0.55rem;">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                     background:{color};flex-shrink:0;"></span>
        <span style="font-family:var(--font);font-weight:700;font-size:var(--font-size-base);
                     color:var(--c-heading);letter-spacing:-0.005em;">{text}</span>
        {badge}
    </div>""", unsafe_allow_html=True)


def _value_pill(label: str, value: float, positive_good: bool = True):
    """Inline Wert-Pill (z.B. auf dem Dashboard).
       Positiv → --c-pill-pos-bg / --value-pos
       Negativ → --c-pill-neg-bg / --value-neg
    """
    is_good = (value >= 0) if positive_good else (value <= 0)
    color  = _GREEN if is_good else _RED
    bg     = "var(--c-pill-pos-bg)"   if is_good else "var(--c-pill-neg-bg)"
    border = "var(--c-pill-pos-border)" if is_good else "var(--c-pill-neg-border)"
    sign   = "+" if value > 0 else ""
    st.markdown(f"""
    <div style="display:inline-flex;align-items:center;gap:0.4rem;
                background:{bg};border:1px solid {border};border-radius:20px;
                padding:0.3rem 0.75rem;font-size:var(--font-size-sm);
                font-weight:600;color:{color};font-family:var(--font);">
        {label}: {sign}{format_euro(value)}
    </div>""", unsafe_allow_html=True)


def _empty_state(msg="Noch keine Einträge vorhanden."):
    """Platzhalter-Box wenn keine Daten vorhanden.
       Farben: --c-empty-bg, --c-empty-border, --c-empty-text
    """
    st.markdown(f"""
    <div style="text-align:center;padding:2.5rem 1rem;
                background:var(--c-empty-bg);
                border:1px dashed var(--c-empty-border);
                border-radius:var(--r);margin:0.5rem 0 1rem;">
        <div style="font-size:2rem;margin-bottom:0.6rem;">📭</div>
        <div style="font-family:var(--font);font-weight:600;
                    font-size:var(--font-size-base);color:var(--c-empty-text);">{msg}</div>
    </div>""", unsafe_allow_html=True)


def _selection_bar(emoji: str, name: str, color: str = _MARINE):
    """Balken der anzeigt, welches Element aktuell ausgewählt ist.
       Hintergrund / Rahmen: dynamisch aus übergebenem color-Parameter berechnet
       "Ausgewählt"-Label: --c-selection-text
    """
    r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.6rem;
                background:rgba({r},{g},{b},0.06);
                border:1px solid rgba({r},{g},{b},0.18);
                border-radius:var(--r-s);padding:0.5rem 0.9rem;margin:0.35rem 0;
                font-size:var(--font-size-sm);color:rgba({r},{g},{b},0.8);">
        {emoji} <strong style="color:{color};">{name}</strong>
        <span style="margin-left:auto;font-size:var(--font-size-xs);
                     color:var(--c-selection-text);font-weight:500;">
            Ausgewählt
        </span>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# DIALOGE
# ─────────────────────────────────────────────────────────────────

@st.dialog("Eintrag bearbeiten / neu")
def eintrag_dialog(conn, u_id, edit_id=None):
    turnus_optionen = ["Monatlich", "Quartalsweise", "Jährlich"]
    existing = None
    if u_id is not None: u_id = int(u_id)
    if edit_id is not None:
        edit_id = int(edit_id)
        _c=conn.cursor();_c.execute("SELECT * FROM eintraege WHERE id=%s AND user_id=%s",(int(edit_id),int(u_id)));_r=_c.fetchall();df=pd.DataFrame(_r,columns=[d[0] for d in _c.description] if _c.description else []);_c.close()
        if not df.empty: existing = df.iloc[0]

    art_val = st.segmented_control(
        "Art", ["Buchung", "Abo", "Finanzierung"],
        default=existing['art'] if existing is not None else "Buchung"
    )
    betrag_typ = "Monatliche Rate"
    if art_val == "Finanzierung":
        betrag_typ = st.selectbox("Betrag-Typ", ["Gesamtbetrag", "Monatliche Rate"],
            index=0 if (existing is None or existing.get('betrag_typ') == "Gesamtbetrag") else 1)

    _c=conn.cursor();_c.execute("SELECT * FROM konten WHERE user_id=%s",(u_id,));_r=_c.fetchall();konten_df=pd.DataFrame(_r,columns=[d[0] for d in _c.description] if _c.description else []);_c.close()
    _c=conn.cursor();_c.execute("SELECT * FROM kategorien WHERE user_id=%s",(u_id,));_r=_c.fetchall();kats_df=pd.DataFrame(_r,columns=[d[0] for d in _c.description] if _c.description else []);_c.close()

    if konten_df.empty:
        st.warning("Bitte lege erst ein Konto in der Verwaltung an!")
        return
    if kats_df.empty:
        st.warning("Bitte lege erst eine Kategorie an!")
        return

    with st.form("eintrag_form"):
        c1, c2 = st.columns(2)
        with c1:
            k_list = konten_df['name'].tolist()
            k_idx  = 0
            if existing is not None:
                try:
                    ck = konten_df[konten_df['id'] == int(existing['konto_id'])]['name'].iloc[0]
                    k_idx = k_list.index(ck) if ck in k_list else 0
                except: pass
            k_auswahl = st.selectbox("Konto", k_list, index=k_idx)
            kat_list  = kats_df['name'].tolist()
            kat_idx   = (kat_list.index(existing['kategorie'])
                         if existing is not None and existing['kategorie'] in kat_list else 0)
            kategorie = st.selectbox("Kategorie", kat_list, index=kat_idx)
            zweck     = st.text_input("Zweck", value=existing['zweck'] if existing is not None else "",
                                      placeholder="z.B. Miete, Netflix, Autokredit…")
        with c2:
            typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"],
                index=0 if (existing is None or existing['typ'] == "Einnahme") else 1)
            bl = ("Betrag (€)" if art_val != "Finanzierung"
                  else ("Gesamtbetrag (€)" if betrag_typ == "Gesamtbetrag" else "Monatliche Rate (€)"))
            betrag = st.number_input(bl, min_value=0.0, step=0.01,
                value=float(existing['betrag']) if existing is not None else 0.0)
            if art_val != "Finanzierung":
                ci = existing['intervall'] if existing is not None else "Monatlich"
                intervall = st.selectbox("Turnus", turnus_optionen,
                    index=turnus_optionen.index(ci) if ci in turnus_optionen else 0)
            else:
                intervall = "Monatlich"

        st.divider()
        d1, d2 = st.columns(2)
        with d1:
            sv = (datetime.fromisoformat(existing['start_datum']).date()
                  if existing is not None and existing['start_datum'] else datetime.now().date())
            start_d = st.date_input("Startdatum", value=sv)
        with d2:
            ev = (datetime.fromisoformat(existing['end_datum']).date()
                  if existing is not None and existing['end_datum'] else None)
            end_d = st.date_input("Enddatum (optional)", value=ev)

        if art_val == "Finanzierung" and end_d and start_d and betrag > 0:
            nm = calculate_months(start_d.isoformat(), end_d.isoformat())
            if betrag_typ == "Gesamtbetrag":
                st.info(f"📅 {nm} Monate · Rate: **{format_euro(betrag/nm if nm else 0)}/Monat**")
            else:
                st.info(f"📅 {nm} Monate · Gesamt: **{format_euro(betrag*nm)}**")

        kuend = None
        if art_val == "Abo":
            kuend = st.number_input("Kündigungsfrist (Tage)", min_value=0,
                value=int(existing['kuendigung_tage']) if existing is not None and existing['kuendigung_tage'] else 30)

        cs, cc = st.columns([3, 1])
        with cs: save = st.form_submit_button("Speichern", width='stretch', type="primary")
        with cc: st.form_submit_button("Abbrechen", width='stretch')

        if save:
            if not zweck:   st.error("Bitte Zweck eingeben."); return
            if betrag <= 0: st.error("Betrag muss > 0 sein."); return
            k_id = int(konten_df[konten_df['name'] == k_auswahl]['id'].iloc[0])
            c = conn.cursor()
            try:
                if existing is not None:
                    c.execute('''UPDATE eintraege SET art=%s,konto_id=%s,kategorie=%s,zweck=%s,
                                 betrag=%s,betrag_typ=%s,typ=%s,intervall=%s,
                                 start_datum=%s,end_datum=%s,kuendigung_tage=%s
                                 WHERE id=%s AND user_id=%s''',
                              (art_val,k_id,kategorie,zweck,betrag,betrag_typ,typ,intervall,
                               start_d.isoformat(),end_d.isoformat() if end_d else None,
                               kuend,int(existing['id']),u_id))
                else:
                    c.execute('''INSERT INTO eintraege
                                 (user_id,art,konto_id,kategorie,zweck,betrag,betrag_typ,
                                  typ,intervall,start_datum,end_datum,kuendigung_tage)
                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                              (u_id,art_val,k_id,kategorie,zweck,betrag,betrag_typ,typ,
                               intervall,start_d.isoformat(),end_d.isoformat() if end_d else None,kuend))
                conn.commit(); st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Fehler: {e}")
            finally:
                c.close()


@st.dialog("Konto bearbeiten / neu")
def konto_dialog(conn, u_id, edit_id=None):
    existing  = None
    konten_df = pd.DataFrame()
    if edit_id:
        _c = conn.cursor()
        _c.execute("SELECT * FROM konten WHERE id=%s AND user_id=%s", (int(edit_id), int(u_id)))
        _r = _c.fetchall()
        df = pd.DataFrame(_r, columns=[d[0] for d in _c.description] if _c.description else [])
        _c.close()
        if not df.empty: existing = df.iloc[0]

    # typ-Auswahl AUSSERHALB des Formulars damit Wechsel sofort re-rendert
    typ_idx = 0 if (existing is None or existing['typ'] == "Bankkonto") else 1
    typ = st.selectbox("Kontotyp", ["Bankkonto", "Zahldienstleister"], index=typ_idx)

    # Bankkonten für Verknüpfung vorladen (nur relevant bei Zahldienstleister)
    if typ == "Zahldienstleister":
        _c = conn.cursor()
        _c.execute("SELECT * FROM konten WHERE user_id=%s AND typ='Bankkonto'", (u_id,))
        _r = _c.fetchall()
        konten_df = pd.DataFrame(_r, columns=[d[0] for d in _c.description] if _c.description else [])
        _c.close()
        if konten_df.empty:
            st.warning("Lege zuerst ein Bankkonto an.")

    with st.form("konto_form"):
        name = st.text_input("Name", value=existing['name'] if existing is not None else "",
                             placeholder="z.B. DKB Girokonto, PayPal…")
        iban = ""
        if typ == "Bankkonto":
            iban = st.text_input("IBAN (optional)",
                                 value=existing['iban'] if existing is not None else "")
        parent = None
        if typ == "Zahldienstleister" and not konten_df.empty:
            bl = konten_df['name'].tolist()
            cp = None
            if existing is not None and existing['parent_id']:
                m = konten_df[konten_df['id'] == existing['parent_id']]['name']
                cp = m.iloc[0] if not m.empty else None
            parent = st.selectbox("Verbundenes Konto", bl,
                                  index=bl.index(cp) if cp in bl else 0)

        if st.form_submit_button("Speichern", width='stretch', type="primary"):
            if not name: st.error("Name erforderlich."); return
            parent_id = None
            if parent and not konten_df.empty:
                parent_id = int(konten_df[konten_df['name'] == parent]['id'].iloc[0])
            c = conn.cursor()
            try:
                if existing is not None:
                    c.execute("UPDATE konten SET name=%s,iban=%s,typ=%s,parent_id=%s WHERE id=%s AND user_id=%s",
                              (name, iban, typ, parent_id, int(existing['id']), u_id))
                else:
                    c.execute("INSERT INTO konten (user_id,name,iban,typ,parent_id) VALUES (%s,%s,%s,%s,%s)",
                              (u_id, name, iban, typ, parent_id))
                conn.commit(); st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Fehler: {e}")
            finally:
                c.close()


@st.dialog("Kategorie bearbeiten / neu")
def kategorie_dialog(conn, u_id, edit_id=None):
    existing = None
    if edit_id:
        _c=conn.cursor();_c.execute("SELECT * FROM kategorien WHERE id=%s AND user_id=%s",(int(edit_id),int(u_id)));_r=_c.fetchall();df=pd.DataFrame(_r,columns=[d[0] for d in _c.description] if _c.description else []);_c.close()
        if not df.empty: existing = df.iloc[0]

    with st.form("kat_form"):
        name = st.text_input("Kategoriename",
                             value=existing['name'] if existing is not None else "",
                             placeholder="z.B. Sport, Streaming, Haushalt…")
        if st.form_submit_button("Speichern", width='stretch', type="primary"):
            if not name: st.error("Name erforderlich."); return
            c = conn.cursor()
            try:
                if existing is not None:
                    c.execute("UPDATE kategorien SET name=%s WHERE id=%s AND user_id=%s",
                              (name, int(existing['id']), u_id))
                else:
                    c.execute("INSERT INTO kategorien (user_id,name) VALUES (%s,%s)", (u_id, name))
                conn.commit(); st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Fehler: {e}")
            finally:
                c.close()


# ─────────────────────────────────────────────────────────────────
# SEITEN
# ─────────────────────────────────────────────────────────────────

def dashboard_page(conn, u_id):
    from forecast import get_forecast_detailed

    _page_header("Dashboard", "Deine Finanzübersicht auf einen Blick")

    zeitraum = st.segmented_control("Vorschau", [3, 6, 12], default=3,
                                    format_func=lambda x: f"{x} Monate")

    f_df, t_df, m_ein, m_aus_ist, m_aus_ant, kat_dist = get_forecast_detailed(conn, u_id, zeitraum)

    if f_df.empty or t_df.empty:
        _empty_state("Lege zuerst ein Konto und Einträge an.")
        cols = st.columns([1, 2, 1])
        with cols[1]:
            if st.button("＋ Ersten Eintrag anlegen", width='stretch', type="primary"):
                eintrag_dialog(conn, u_id)
        return

    saldo = m_ein - m_aus_ist

    # ── KPIs ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Einnahmen (Monat)", format_euro(m_ein))
    with col2:
        st.metric("Ausgaben (fällig)", format_euro(m_aus_ist))
    with col3:
        st.metric("Ausgaben (anteilig)", format_euro(m_aus_ant),
                  help="Gleichmäßig verteilte monatliche Last")
    with col4:
        delta = saldo - (m_ein - m_aus_ant)
        st.metric("Verfügbar (Ist)", format_euro(saldo),
                  delta=f"{'+' if delta >= 0 else ''}{format_euro(abs(delta))}" if delta != 0 else None)

    st.divider()

    # ── CHARTS ──
    with st.expander("Grafiken & Statistiken", expanded=True):
        co1, co2 = st.columns(2)

        with co1:
            if kat_dist:
                # Orange-Marine Palette für Kategorien
                kat_colors = [_MARINE,'#254E94','#2E60B0','#F07800','#FF9A30',
                              '#FFB860','#39D353','#2AB544','#1C9E3A','#17823A']
                fig = go.Figure(go.Pie(
                    labels=list(kat_dist.keys()),
                    values=list(kat_dist.values()),
                    hole=0.52,
                    marker=dict(colors=kat_colors[:len(kat_dist)],
                                line=dict(color='rgba(255,255,255,0.8)', width=2)),
                    textinfo='percent',
                    textfont=dict(size=11),
                    hovertemplate='<b>%{label}</b><br>%{value:.2f} €  |  %{percent}<extra></extra>'
                ))
                total_aus = sum(kat_dist.values())
                fig.update_layout(
                    **_PLOT_LAYOUT,
                    title=dict(text="Ausgaben nach Kategorie",
                               font=dict(family='Outfit', size=13, color=_CHART_TEXT), x=0.02),
                    annotations=[dict(text=f"<b>{format_euro(total_aus)}</b>",
                                      x=0.5, y=0.5, font_size=12, showarrow=False,
                                      font=dict(color=_CHART_TEXT, family='Outfit'))]
                )
                st.plotly_chart(fig, width='stretch')

        with co2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name='Einnahmen', x=f_df['Monat'], y=f_df['Einnahmen'],
                marker=dict(color=_MARINE, opacity=0.85,
                            line=dict(color=_MARINE, width=0)),
                hovertemplate='Einnahmen %{x}: <b>%{y:,.2f} €</b><extra></extra>'
            ))
            fig2.add_trace(go.Bar(
                name='Ausgaben', x=f_df['Monat'], y=f_df['Ausgaben'],
                marker=dict(color=_ORANGE, opacity=0.8,
                            line=dict(color=_ORANGE, width=0)),
                hovertemplate='Ausgaben %{x}: <b>%{y:,.2f} €</b><extra></extra>'
            ))
            # Saldo-Linie: grün wenn positiv, rot wenn negativ
            saldo_colors = [_GREEN if v >= 0 else _RED for v in f_df['Saldo']]
            fig2.add_trace(go.Scatter(
                name='Saldo', x=f_df['Monat'], y=f_df['Saldo'],
                mode='lines+markers',
                line=dict(color=_NEON, width=2.5),
                marker=dict(size=7, color=saldo_colors,
                            line=dict(color='white', width=1.5)),
                hovertemplate='Saldo %{x}: <b>%{y:,.2f} €</b><extra></extra>'
            ))
            fig2.update_layout(
                **_PLOT_LAYOUT,
                title=dict(text=f"Cashflow – {zeitraum} Monate",
                           font=dict(family='Outfit', size=13, color=_CHART_TEXT), x=0.02),
                barmode='group', bargap=0.22, bargroupgap=0.06,
            )
            st.plotly_chart(fig2, width='stretch')

    st.divider()

    # ── OPTION 3: TIMELINE-ANSICHT ────────────────────────────────
    _section_label("Cashflow-Timeline", color=_MARINE)

    for i, monat in enumerate(t_df['Monat'].unique()):
        m_sub   = t_df[t_df['Monat'] == monat].sort_values(
                      by=["Ist_Fällig","Typ_Internal"], ascending=[False,True])
        ein_s   = m_sub[m_sub['Typ_Internal']=='Einnahme']['Betrag (fällig)'].sum()
        aus_s   = m_sub[m_sub['Typ_Internal']=='Ausgabe']['Betrag (fällig)'].sum()
        saldo_m = ein_s - aus_s
        s_color = _GREEN if saldo_m >= 0 else _RED
        s_sign  = "+" if saldo_m > 0 else ""

        # Monatstrenner
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.8rem;margin:{'1.4rem' if i>0 else '0.4rem'} 0 0.6rem;">
            <div style="font-family:var(--font);font-weight:700;font-size:var(--font-size-base);
                        color:var(--c-heading);letter-spacing:-0.01em;white-space:nowrap;">
                📅 {monat}
            </div>
            <div style="flex:1;height:1px;background:var(--c-list-border);"></div>
            <div style="display:flex;gap:0.5rem;align-items:center;flex-shrink:0;">
                <span style="font-size:var(--font-size-sm);color:{_GREEN};font-weight:600;">
                    +{format_euro(ein_s)}
                </span>
                <span style="color:var(--c-list-text-sub);font-size:var(--font-size-xs);">·</span>
                <span style="font-size:var(--font-size-sm);color:{_RED};font-weight:600;">
                    -{format_euro(aus_s)}
                </span>
                <span style="color:var(--c-list-text-sub);font-size:var(--font-size-xs);">·</span>
                <span style="font-size:var(--font-size-sm);color:{s_color};font-weight:700;">
                    {s_sign}{format_euro(saldo_m)}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Einträge – einzelne st.markdown pro Zeile
        st.markdown(
            "<div style='background:var(--c-list-bg);"
            "border:1px solid var(--c-list-border);"
            "border-radius:var(--r);overflow:hidden;margin-bottom:0.3rem;'>",
            unsafe_allow_html=True)

        for _, row in m_sub.iterrows():
            is_ein   = row['Typ_Internal'] == 'Einnahme'
            faellig  = row['Ist_Fällig']
            betrag   = row['Betrag (fällig)']
            anteilig = row['Anteilig p.M.']
            color_b  = _GREEN if is_ein else _RED
            opacity  = "1" if faellig else "0.45"
            sign     = "+" if is_ein else chr(8722)
            icon     = str(row[' '])
            zweck    = str(row['Zweck']).replace('<','&lt;').replace('>','&gt;')
            konto    = str(row['Konto']).replace('<','&lt;').replace('>','&gt;')
            kat      = str(row['Kategorie']).replace('<','&lt;').replace('>','&gt;')

            t_badge = ""
            if row['Turnus'] != "Monatlich":
                t_badge = (
                    "<span style='background:var(--c-badge-turnus-bg);color:var(--c-badge-turnus-text);"
                    "border:1px solid var(--c-badge-turnus-border);border-radius:10px;"
                    "padding:1px 7px;font-size:var(--font-size-xs);font-weight:600;"
                    "margin-left:0.4rem;'>" + str(row['Turnus']) + "</span>"
                )
            not_due = "" if faellig else (
                "<span style='font-size:var(--font-size-xs);color:var(--c-list-text-sub);"
                "margin-left:0.4rem;font-style:italic;'>anteilig</span>"
            )

            row_html = (
                "<div style='display:flex;align-items:center;padding:0.5rem 0.9rem;"
                "border-bottom:1px solid var(--c-list-row-divider);"
                "opacity:" + opacity + ";'>"
                "<span style='font-size:1rem;width:1.6rem;flex-shrink:0;'>"
                + icon + "</span>"
                "<div style='flex:1;min-width:0;margin:0 0.6rem;'>"
                "<div style='font-weight:600;font-size:var(--font-size-base);"
                "color:var(--c-list-text-primary);"
                "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>"
                + zweck + t_badge + not_due + "</div>"
                "<div style='font-size:var(--font-size-xs);color:var(--c-list-text-sub);margin-top:1px;'>"
                + konto + " &middot; " + kat + "</div>"
                "</div>"
                "<div style='text-align:right;flex-shrink:0;'>"
                "<div style='font-weight:700;font-size:var(--font-size-base);color:" + color_b + ";'>"
                + sign + format_euro(betrag) + "</div>"
                "<div style='font-size:var(--font-size-xs);color:var(--c-list-text-sub);'>"
                + format_euro(anteilig) + "/M</div>"
                "</div></div>"
            )
            st.markdown(row_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

def _entry_row_list(conn, u_id, subset, key, color):
    """Banking-Style Zeilenliste für Einträge.
       Container: --c-list-bg, --c-list-border
       Zeilen-Trennlinie: --c-list-row-divider
       Primärtext: --c-list-text-primary
       Subtext: --c-list-text-sub
       Turnus-Badge: --c-badge-turnus-*
    """
    if subset.empty:
        st.markdown(
            "<p style='color:var(--c-list-text-sub);font-size:var(--font-size-sm);"
            "margin:0.2rem 0 0.7rem 1rem;'>Keine aktiven Einträge.</p>",
            unsafe_allow_html=True)
        return

    # Listen-Container
    st.markdown(
        "<div style='background:var(--c-list-bg);"
        "border:1px solid var(--c-list-border);"
        "border-radius:var(--r);overflow:hidden;margin-bottom:0.2rem;'>",
        unsafe_allow_html=True)

    for _, row in subset.iterrows():
        is_ein   = row['typ'] == 'Einnahme'
        col_b    = _GREEN if is_ein else _RED
        sign     = "+" if is_ein else chr(8722)
        art_icon = get_emoji(row['art'], row['typ'])

        t_badge = ""
        if row['intervall'] != "Monatlich":
            t_badge = (
                "<span style='background:var(--c-badge-turnus-bg);color:var(--c-badge-turnus-text);"
                "border:1px solid var(--c-badge-turnus-border);border-radius:var(--r-s);"
                "padding:1px 6px;font-size:var(--font-size-xs);font-weight:600;"
                "margin-left:0.35rem;'>" + row['intervall'] + "</span>"
            )

        try:
            d_str = pd.to_datetime(row['start_datum']).strftime('%d.%m.%Y')
        except Exception:
            d_str = str(row['start_datum']) if row['start_datum'] else ""

        end_str = ""
        if row['end_datum']:
            try:
                end_str = " – " + pd.to_datetime(row['end_datum']).strftime('%d.%m.%Y')
            except Exception:
                pass

        betrag_fmt = format_euro(row['betrag'])
        zweck_esc  = str(row['zweck']).replace('<', '&lt;').replace('>', '&gt;')
        konto_esc  = str(row['konto_name']).replace('<', '&lt;').replace('>', '&gt;')
        kat_esc    = str(row['kategorie']).replace('<', '&lt;').replace('>', '&gt;')
        intervall  = str(row['intervall'])

        html = (
            "<div style='display:flex;align-items:center;padding:0.65rem 1rem;"
            "border-bottom:1px solid var(--c-list-row-divider);'>"

            "<span style='font-size:1.1rem;width:1.8rem;flex-shrink:0;'>"
            + art_icon + "</span>"

            "<div style='flex:1;min-width:0;margin:0 0.75rem;'>"
            "<div style='font-weight:600;font-size:var(--font-size-base);"
            "color:var(--c-list-text-primary);"
            "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>"
            + zweck_esc + t_badge + "</div>"
            "<div style='font-size:var(--font-size-xs);color:var(--c-list-text-sub);margin-top:1px;'>"
            + konto_esc + " &middot; " + kat_esc + " &middot; " + d_str + end_str
            + "</div></div>"

            "<div style='text-align:right;flex-shrink:0;'>"
            "<div style='font-weight:700;font-size:var(--font-size-base);color:" + col_b + ";'>"
            + sign + " " + betrag_fmt + "</div>"
            "<div style='font-size:var(--font-size-xs);color:var(--c-list-text-sub);'>"
            + intervall + "</div></div></div>"
        )
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Auswahl per Selectbox
    names = [
        get_emoji(r['art'], r['typ']) + "  " + r['zweck'] + "  –  " + format_euro(r['betrag'])
        for _, r in subset.iterrows()
    ]
    chosen = st.selectbox(
        "Eintrag auswählen",
        ["— Eintrag auswählen —"] + names,
        index=0, key="pick_" + key, label_visibility="collapsed"
    )

    if chosen != "— Eintrag auswählen —":
        row = subset.iloc[names.index(chosen)]
        _selection_bar(get_emoji(row['art'], row['typ']), row['zweck'], color)
        c1, c2, c3 = st.columns([2, 2, 6])
        with c1:
            if st.button("✏️ Bearbeiten", key="ed_" + key, width='stretch'):
                eintrag_dialog(conn, u_id, row['id'])
        with c2:
            if st.button("🗑️ Löschen", key="dl_" + key, width='stretch'):
                cur = conn.cursor()
                try:
                    cur.execute("DELETE FROM eintraege WHERE id=%s AND user_id=%s",
                                (int(row['id']), u_id))
                    conn.commit()
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error("Fehler: " + str(e))
                finally:
                    cur.close()

def entries_page(conn, u_id):
    _page_header("Einträge", "Buchungen, Abos und Finanzierungen")

    _c=conn.cursor();_c.execute("SELECT e.*, k.name as konto_name FROM eintraege e JOIN konten k ON e.konto_id=k.id WHERE e.user_id=%s ORDER BY e.start_datum DESC",(u_id,));_r=_c.fetchall();df_all=pd.DataFrame(_r,columns=[d[0] for d in _c.description] if _c.description else []);_c.close()
    if df_all.empty:
        _empty_state()
        if st.button("＋ Ersten Eintrag anlegen", type="primary"):
            eintrag_dialog(conn, u_id)
        return

    gruppen = [
        ("Buchung",     "Buchungen",     "bk", _MARINE),
        ("Abo",         "Abos",          "ab", _ORANGE),
        ("Finanzierung","Finanzierungen","fn", "#7C4FD4"),
    ]

    for art, label, key, color in gruppen:
        subset = df_all[df_all['art'] == art].copy()
        if subset.empty: continue

        aktiv, abg = subset, pd.DataFrame()
        if art == "Finanzierung":
            mask = subset['end_datum'].notna() & \
                   (pd.to_datetime(subset['end_datum'], errors='coerce') < pd.Timestamp.now())
            aktiv, abg = subset[~mask], subset[mask]

        _section_label(label, color=color, count=len(aktiv))
        _entry_row_list(conn, u_id, aktiv.reset_index(drop=True), key, color)

        if not abg.empty:
            with st.expander(f"Abgeschlossene Finanzierungen ({len(abg)})"):
                abg_display = abg.copy()
                abg_display['betrag'] = abg_display['betrag'].apply(format_euro)
                abg_display['start_datum'] = pd.to_datetime(abg_display['start_datum']).dt.strftime('%d.%m.%Y')
                abg_display['end_datum'] = abg_display['end_datum'].apply(
                    lambda x: pd.to_datetime(x).strftime('%d.%m.%Y') if pd.notna(x) and x else '')
                st.dataframe(
                    abg_display[['zweck','konto_name','betrag','intervall','start_datum','end_datum']].rename(columns={
                        'zweck':'Zweck','konto_name':'Konto','betrag':'Betrag',
                        'intervall':'Turnus','start_datum':'Start','end_datum':'Ende'}),
                    width='stretch', hide_index=True
                )

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)


def _render_konto_list(kd):
    """Konten als Zeilenliste im Banking-Stil.
       Container: --c-list-bg, --c-list-border
       Zeilen-Trennlinie: --c-list-row-divider
       Primärtext: --c-list-text-primary   Subtext: --c-list-text-sub
       Konto-Badge: --c-badge-konto-*      Zahldienst-Badge: --c-badge-turnus-*
    """
    if kd.empty:
        return
    st.markdown(
        "<div style='background:var(--c-list-bg);"
        "border:1px solid var(--c-list-border);"
        "border-radius:var(--r);overflow:hidden;'>",
        unsafe_allow_html=True)

    for _, row in kd.iterrows():
        typ        = str(row['typ'])
        name       = str(row['name']).replace('<','&lt;').replace('>','&gt;')
        iban       = str(row['iban']) if row['iban'] else ""
        verknuepft = str(row['verbundenes_konto']) if row['verbundenes_konto'] else ""
        icon       = "🏦" if typ == "Bankkonto" else "💳"
        # Bankkonto → Marine-Badge, Zahldienstleister → Orange-Badge
        typ_bg     = "var(--c-badge-konto-bg)"     if typ == "Bankkonto" else "var(--c-badge-turnus-bg)"
        typ_color  = "var(--c-badge-konto-text)"   if typ == "Bankkonto" else "var(--c-badge-turnus-text)"
        typ_border = "var(--c-badge-konto-border)" if typ == "Bankkonto" else "var(--c-badge-turnus-border)"

        sub_parts = []
        if iban:
            sub_parts.append("IBAN: " + iban[:22] + ("…" if len(iban) > 22 else ""))
        if verknuepft:
            sub_parts.append("&#8594; " + verknuepft)
        sub_line = " &middot; ".join(sub_parts)

        typ_badge = (
            "<span style='background:" + typ_bg + ";color:" + typ_color + ";"
            "border:1px solid " + typ_border + ";border-radius:var(--r-s);"
            "padding:1px 7px;font-size:var(--font-size-xs);font-weight:600;margin-left:0.4rem;'>"
            + typ + "</span>"
        )
        sub_html = (
            "<div style='font-size:var(--font-size-xs);color:var(--c-list-text-sub);margin-top:1px;'>"
            + sub_line + "</div>"
        ) if sub_line else ""

        html = (
            "<div style='display:flex;align-items:center;padding:0.6rem 1rem;"
            "border-bottom:1px solid var(--c-list-row-divider);'>"
            "<span style='font-size:1.1rem;width:1.8rem;flex-shrink:0;'>" + icon + "</span>"
            "<div style='flex:1;min-width:0;margin:0 0.6rem;'>"
            "<div style='font-weight:600;font-size:var(--font-size-base);color:var(--c-list-text-primary);'>"
            + name + typ_badge + "</div>"
            + sub_html + "</div></div>"
        )
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_kategorie_list(ctd):
    """Kategorien als Zeilenliste.
       Container: --c-list-bg, --c-list-border
       Zeilen-Trennlinie: --c-list-row-divider
       Text: --c-list-text-primary
    """
    if ctd.empty:
        return
    st.markdown(
        "<div style='background:var(--c-list-bg);"
        "border:1px solid var(--c-list-border);"
        "border-radius:var(--r);overflow:hidden;'>",
        unsafe_allow_html=True)

    for _, row in ctd.iterrows():
        name = str(row['name']).replace('<','&lt;').replace('>','&gt;')
        html = (
            "<div style='display:flex;align-items:center;padding:0.6rem 1rem;"
            "border-bottom:1px solid var(--c-list-row-divider);'>"
            "<span style='font-size:1rem;width:1.8rem;flex-shrink:0;'>📂</span>"
            "<div style='font-weight:500;font-size:var(--font-size-base);color:var(--c-list-text-primary);'>"
            + name + "</div></div>"
        )
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def settings_page(conn, u_id):
    _page_header("Verwaltung", "Konten und Kategorien konfigurieren")

    col_k, col_cat = st.columns(2, gap="large")

    # ── KONTEN ──
    with col_k:
        _section_label("Konten", color=_MARINE)
        _c = conn.cursor()
        _c.execute("SELECT * FROM konten WHERE user_id=%s", (u_id,))
        _r = _c.fetchall()
        kd = pd.DataFrame(_r, columns=[d[0] for d in _c.description] if _c.description else [])
        _c.close()

        if not kd.empty:
            kd['verbundenes_konto'] = kd.apply(
                lambda r: kd[kd['id'] == r['parent_id']]['name'].iloc[0]
                          if pd.notna(r['parent_id']) and not kd[kd['id'] == r['parent_id']].empty
                          else '', axis=1
            )
            _render_konto_list(kd)

            names = [("🏦 " if r['typ'] == "Bankkonto" else "💳 ") + r['name']
                     for _, r in kd.iterrows()]
            chosen = st.selectbox("Konto auswählen", ["— Konto auswählen —"] + names,
                                  index=0, key="pick_k", label_visibility="collapsed")
            if chosen != "— Konto auswählen —":
                sel = kd.iloc[names.index(chosen)]
                _selection_bar("🏦", sel['name'], _MARINE)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✏️ Bearbeiten", key="ek", width='stretch'):
                        konto_dialog(conn, u_id, sel['id'])
                with c2:
                    if st.button("🗑️ Löschen", key="dk", width='stretch'):
                        cur = conn.cursor()
                        try:
                            cur.execute("DELETE FROM konten WHERE id=%s AND user_id=%s",
                                        (int(sel['id']), u_id))
                            conn.commit()
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error("Fehler: " + str(e))
                        finally:
                            cur.close()
        else:
            _empty_state("Noch keine Konten vorhanden.")

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.button("＋ Konto hinzufügen", key="ak", width='stretch', type="primary"):
            konto_dialog(conn, u_id)

    # ── KATEGORIEN ──
    with col_cat:
        _section_label("Kategorien", color=_ORANGE)
        _c = conn.cursor()
        _c.execute("SELECT * FROM kategorien WHERE user_id=%s ORDER BY name", (u_id,))
        _r = _c.fetchall()
        ctd = pd.DataFrame(_r, columns=[d[0] for d in _c.description] if _c.description else [])
        _c.close()

        if not ctd.empty:
            _render_kategorie_list(ctd)

            names_k = ["📂 " + r['name'] for _, r in ctd.iterrows()]
            chosen_k = st.selectbox("Kategorie auswählen", ["— Kategorie auswählen —"] + names_k,
                                    index=0, key="pick_kat", label_visibility="collapsed")
            if chosen_k != "— Kategorie auswählen —":
                sel_k = ctd.iloc[names_k.index(chosen_k)]
                _selection_bar("📂", sel_k['name'], _ORANGE)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✏️ Bearbeiten", key="ekat", width='stretch'):
                        kategorie_dialog(conn, u_id, sel_k['id'])
                with c2:
                    if st.button("🗑️ Löschen", key="dkat", width='stretch'):
                        cur = conn.cursor()
                        try:
                            cur.execute("DELETE FROM kategorien WHERE id=%s AND user_id=%s",
                                        (int(sel_k['id']), u_id))
                            conn.commit()
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error("Fehler: " + str(e))
                        finally:
                            cur.close()
        else:
            _empty_state("Noch keine Kategorien vorhanden.")

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.button("＋ Kategorie hinzufügen", key="akat", width='stretch', type="primary"):
            kategorie_dialog(conn, u_id)
