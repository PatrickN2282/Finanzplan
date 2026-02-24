import sys
sys.path.append('.')
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from db import format_euro, get_conn
from forecast import calculate_months


def get_emoji(art, typ):
    if art == "Buchung":
        return "💰" if typ == "Einnahme" else "💸"
    elif art == "Abo":
        return "🔄"
    elif art == "Finanzierung":
        return "🏦"
    return "❓"


def _style_row(row):
    if row['Typ_Internal'] == 'Einnahme':
        bg = 'background-color: rgba(0,212,255,0.05)'
    else:
        bg = 'background-color: rgba(255,76,106,0.05)'
    text = 'font-weight:500' if row['Ist_Fällig'] else 'color:#475569; font-style:italic'
    return [f'{bg}; {text}'] * len(row)


def _card(html: str):
    """Hilfsfunktion: Glasskarte rendern."""
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.5rem;
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    ">
        <div style="position:absolute;top:0;left:0;right:0;height:1px;
                    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);">
        </div>
        {html}
    </div>""", unsafe_allow_html=True)


def _section_header(title: str, count: int = None, color: str = "#00D4FF"):
    badge = f'<span style="background:rgba({",".join(str(int(color.lstrip("#")[i:i+2],16)) for i in (0,2,4))},0.15);color:{color};border:1px solid rgba({",".join(str(int(color.lstrip("#")[i:i+2],16)) for i in (0,2,4))},0.3);border-radius:20px;padding:1px 10px;font-size:0.75rem;font-weight:600;margin-left:0.5rem;">{count}</span>' if count is not None else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;margin:1.2rem 0 0.6rem 0;">
        <div style="width:3px;height:1.1rem;background:{color};border-radius:2px;margin-right:0.6rem;opacity:0.8;"></div>
        <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:#CBD5E1;letter-spacing:-0.01em;">{title}</span>
        {badge}
    </div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# DIALOGE
# ---------------------------------------------------------------------------

@st.dialog("Eintrag bearbeiten / neu")
def eintrag_dialog(conn, u_id, edit_id=None):
    turnus_optionen = ["Monatlich", "Quartalsweise", "Jährlich"]
    existing = None

    if u_id is not None:
        u_id = int(u_id)
    if edit_id is not None:
        edit_id = int(edit_id)
        df = pd.read_sql_query(
            "SELECT * FROM eintraege WHERE id=%s AND user_id=%s",
            conn, params=(edit_id, u_id)
        )
        if not df.empty:
            existing = df.iloc[0]

    art_default = existing['art'] if existing is not None else "Buchung"
    art_val = st.segmented_control(
        "Art des Eintrags",
        ["Buchung", "Abo", "Finanzierung"],
        default=art_default
    )

    betrag_typ = "Monatliche Rate"
    if art_val == "Finanzierung":
        betrag_typ = st.selectbox(
            "Betrag-Typ",
            ["Gesamtbetrag", "Monatliche Rate"],
            index=0 if (existing is None or existing.get('betrag_typ') == "Gesamtbetrag") else 1,
            help="Gesamtbetrag wird gleichmäßig auf die Laufzeit verteilt."
        )

    konten_df = pd.read_sql_query("SELECT * FROM konten WHERE user_id=%s", conn, params=(u_id,))
    kats_df   = pd.read_sql_query("SELECT * FROM kategorien WHERE user_id=%s", conn, params=(u_id,))

    if konten_df.empty:
        st.warning("⚠️ Bitte lege erst ein Konto in der Verwaltung an!")
        return
    if kats_df.empty:
        st.warning("⚠️ Bitte lege erst eine Kategorie in der Verwaltung an!")
        return

    with st.form("eintrag_form"):
        c1, c2 = st.columns(2)
        with c1:
            k_list = konten_df['name'].tolist()
            k_idx  = 0
            if existing is not None:
                try:
                    cur_k = konten_df[konten_df['id'] == int(existing['konto_id'])]['name'].iloc[0]
                    k_idx = k_list.index(cur_k) if cur_k in k_list else 0
                except (IndexError, KeyError):
                    k_idx = 0
            k_auswahl = st.selectbox("Konto", k_list, index=k_idx)

            kat_list = kats_df['name'].tolist()
            kat_idx  = (kat_list.index(existing['kategorie'])
                        if existing is not None and existing['kategorie'] in kat_list else 0)
            kategorie = st.selectbox("Kategorie", kat_list, index=kat_idx)

            zweck = st.text_input("Zweck / Bezeichnung",
                value=existing['zweck'] if existing is not None else "",
                placeholder="z.B. Netflix, Miete, Autokredit…")

        with c2:
            typ = st.selectbox("Ein-/Ausgabe", ["Einnahme", "Ausgabe"],
                index=0 if (existing is None or existing['typ'] == "Einnahme") else 1)

            betrag_label = (
                "Betrag (€)" if art_val != "Finanzierung"
                else ("Gesamtbetrag (€)" if betrag_typ == "Gesamtbetrag" else "Monatliche Rate (€)")
            )
            betrag = st.number_input(betrag_label, min_value=0.0, step=0.01,
                value=float(existing['betrag']) if existing is not None else 0.0)

            if art_val != "Finanzierung":
                curr_int = existing['intervall'] if existing is not None else "Monatlich"
                int_idx  = turnus_optionen.index(curr_int) if curr_int in turnus_optionen else 0
                intervall = st.selectbox("Turnus", turnus_optionen, index=int_idx)
            else:
                intervall = "Monatlich"

        st.divider()

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            s_val = (datetime.fromisoformat(existing['start_datum']).date()
                     if existing is not None and existing['start_datum'] else datetime.now().date())
            start_d = st.date_input("Startdatum", value=s_val)
        with col_d2:
            e_val = (datetime.fromisoformat(existing['end_datum']).date()
                     if existing is not None and existing['end_datum'] else None)
            end_d = st.date_input("Enddatum (optional)", value=e_val)

        if art_val == "Finanzierung" and end_d and start_d and betrag > 0:
            num_months = calculate_months(start_d.isoformat(), end_d.isoformat())
            if betrag_typ == "Gesamtbetrag":
                monthly = betrag / num_months if num_months > 0 else 0
                st.info(f"📅 Laufzeit: **{num_months} Monate** · Rate: **{format_euro(monthly)}/Monat**")
            else:
                total = betrag * num_months
                st.info(f"📅 Laufzeit: **{num_months} Monate** · Gesamt: **{format_euro(total)}**")

        kuend = None
        if art_val == "Abo":
            kuend = st.number_input("Kündigungsfrist (Tage)", min_value=0,
                value=int(existing['kuendigung_tage']) if existing is not None and existing['kuendigung_tage'] else 30)

        col_s, col_c = st.columns([3, 1])
        with col_s:
            save = st.form_submit_button("💾 Speichern", use_container_width=True, type="primary")
        with col_c:
            st.form_submit_button("Abbrechen", use_container_width=True)

        if save:
            if not zweck:
                st.error("Bitte einen Zweck eingeben.")
                return
            if betrag <= 0:
                st.error("Betrag muss größer als 0 sein.")
                return
            k_id       = int(konten_df[konten_df['name'] == k_auswahl]['id'].iloc[0])
            final_end  = end_d.isoformat() if end_d else None
            c = conn.cursor()
            try:
                if existing is not None:
                    c.execute('''UPDATE eintraege SET art=%s,konto_id=%s,kategorie=%s,zweck=%s,
                                 betrag=%s,betrag_typ=%s,typ=%s,intervall=%s,
                                 start_datum=%s,end_datum=%s,kuendigung_tage=%s
                                 WHERE id=%s AND user_id=%s''',
                              (art_val,k_id,kategorie,zweck,betrag,betrag_typ,typ,
                               intervall,start_d.isoformat(),final_end,kuend,int(existing['id']),u_id))
                else:
                    c.execute('''INSERT INTO eintraege
                                 (user_id,art,konto_id,kategorie,zweck,betrag,betrag_typ,
                                  typ,intervall,start_datum,end_datum,kuendigung_tage)
                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                              (u_id,art_val,k_id,kategorie,zweck,betrag,betrag_typ,
                               typ,intervall,start_d.isoformat(),final_end,kuend))
                conn.commit()
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Fehler beim Speichern: {e}")
            finally:
                c.close()


@st.dialog("Konto bearbeiten / neu")
def konto_dialog(conn, u_id, edit_id=None):
    existing   = None
    konten_df  = pd.DataFrame()
    if edit_id:
        df = pd.read_sql_query("SELECT * FROM konten WHERE id=%s AND user_id=%s",
                               conn, params=(edit_id, u_id))
        if not df.empty:
            existing = df.iloc[0]

    with st.form("konto_form"):
        typ  = st.selectbox("Kontotyp", ["Bankkonto", "Zahldienstleister"],
                            index=0 if (existing is None or existing['typ'] == "Bankkonto") else 1)
        name = st.text_input("Name", value=existing['name'] if existing is not None else "",
                             placeholder="z.B. DKB Girokonto, PayPal…")
        iban = ""
        if typ == "Bankkonto":
            iban = st.text_input("IBAN (optional)",
                                 value=existing['iban'] if existing is not None else "",
                                 placeholder="DE00 0000 0000 0000 0000 00")
        parent = None
        if typ == "Zahldienstleister":
            konten_df = pd.read_sql_query("SELECT * FROM konten WHERE user_id=%s AND typ='Bankkonto'",
                                          conn, params=(u_id,))
            if not konten_df.empty:
                bankkonten    = konten_df['name'].tolist()
                current_parent = None
                if existing is not None and existing['parent_id']:
                    m = konten_df[konten_df['id'] == existing['parent_id']]['name']
                    current_parent = m.iloc[0] if not m.empty else None
                parent_idx = bankkonten.index(current_parent) if current_parent in bankkonten else 0
                parent = st.selectbox("Verbundenes Bankkonto", bankkonten, index=parent_idx)
            else:
                st.warning("Lege zuerst ein Bankkonto an.")

        if st.form_submit_button("💾 Speichern", use_container_width=True, type="primary"):
            if not name:
                st.error("Bitte einen Namen eingeben.")
                return
            parent_id = None
            if parent and not konten_df.empty:
                parent_id = int(konten_df[konten_df['name'] == parent]['id'].iloc[0])
            c = conn.cursor()
            try:
                if existing is not None:
                    c.execute("UPDATE konten SET name=%s,iban=%s,typ=%s,parent_id=%s WHERE id=%s AND user_id=%s",
                              (name,iban,typ,parent_id,int(existing['id']),u_id))
                else:
                    c.execute("INSERT INTO konten (user_id,name,iban,typ,parent_id) VALUES (%s,%s,%s,%s,%s)",
                              (u_id,name,iban,typ,parent_id))
                conn.commit()
                st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Fehler: {e}")
            finally:
                c.close()


@st.dialog("Kategorie bearbeiten / neu")
def kategorie_dialog(conn, u_id, edit_id=None):
    existing = None
    if edit_id:
        df = pd.read_sql_query("SELECT * FROM kategorien WHERE id=%s AND user_id=%s",
                               conn, params=(edit_id, u_id))
        if not df.empty:
            existing = df.iloc[0]

    with st.form("kategorie_form"):
        name = st.text_input("Kategoriename",
                             value=existing['name'] if existing is not None else "",
                             placeholder="z.B. Sport, Streaming, Haushalt…")
        if st.form_submit_button("💾 Speichern", use_container_width=True, type="primary"):
            if not name:
                st.error("Bitte einen Namen eingeben.")
                return
            c = conn.cursor()
            try:
                if existing is not None:
                    c.execute("UPDATE kategorien SET name=%s WHERE id=%s AND user_id=%s",
                              (name,int(existing['id']),u_id))
                else:
                    c.execute("INSERT INTO kategorien (user_id,name) VALUES (%s,%s)", (u_id,name))
                conn.commit()
                st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Fehler: {e}")
            finally:
                c.close()


# ---------------------------------------------------------------------------
# SEITEN
# ---------------------------------------------------------------------------

def dashboard_page(conn, u_id):
    from forecast import get_forecast_detailed

    # ── Seitenkopf ──
    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <h1 style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;
                   letter-spacing:-0.035em;margin:0;color:#E2E8F0;">
            Dashboard
        </h1>
        <p style="color:#475569;margin:0.2rem 0 0;font-size:0.87rem;">
            Deine Finanzübersicht auf einen Blick
        </p>
    </div>
    """, unsafe_allow_html=True)

    zeitraum = st.segmented_control(
        "Vorschau-Zeitraum", [3, 6, 12], default=3,
        format_func=lambda x: f"{x} Monate"
    )

    f_df, t_df, m_ein, m_aus_ist, m_aus_ant, kat_dist = get_forecast_detailed(conn, u_id, zeitraum)

    if f_df.empty or t_df.empty:
        st.markdown("""
        <div style="text-align:center;padding:3rem;background:rgba(255,255,255,0.02);
                    border:1px solid rgba(255,255,255,0.06);border-radius:16px;margin-top:1rem;">
            <div style="font-size:2.5rem;margin-bottom:0.8rem;">📭</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                        color:#CBD5E1;margin-bottom:0.4rem;">Noch keine Einträge</div>
            <div style="color:#475569;font-size:0.87rem;">
                Lege dein erstes Konto und deinen ersten Eintrag an.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        cols = st.columns([1, 2, 1])
        with cols[1]:
            if st.button("＋ Ersten Eintrag anlegen", use_container_width=True, type="primary"):
                eintrag_dialog(conn, u_id)
        return

    saldo = m_ein - m_aus_ist

    # ── KPI CARDS ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Einnahmen", format_euro(m_ein), help="Fällige Einnahmen diesen Monat")
    with col2:
        st.metric("💸 Ausgaben (fällig)", format_euro(m_aus_ist))
    with col3:
        st.metric("📊 Ausgaben (anteilig)", format_euro(m_aus_ant),
                  help="Inkl. quartals-/jährlicher Posten gleichmäßig verteilt")
    with col4:
        delta_val = saldo - (m_ein - m_aus_ant)
        st.metric(
            "✅ Verfügbar",
            format_euro(saldo),
            delta=f"{'+' if delta_val >= 0 else ''}{format_euro(abs(delta_val))} vs. anteilig" if delta_val != 0 else None
        )

    st.divider()

    # ── CHARTS ──
    with st.expander("📈 Grafiken & Statistiken", expanded=True):
        co1, co2 = st.columns(2)

        with co1:
            if kat_dist:
                # Custom Farben: Cyan-Palette
                colors = ['#00D4FF','#00A8CC','#007A99','#005066','#003344',
                          '#00FF87','#00CC6A','#33FFAA','#66FFB3','#99FFCC']
                fig_pie = go.Figure(go.Pie(
                    labels=list(kat_dist.keys()),
                    values=list(kat_dist.values()),
                    hole=0.55,
                    marker=dict(colors=colors[:len(kat_dist)],
                                line=dict(color='rgba(8,11,20,0.8)', width=2)),
                    textinfo='percent',
                    textfont=dict(size=11, color='#E2E8F0'),
                    hovertemplate='<b>%{label}</b><br>%{value:.2f} €<br>%{percent}<extra></extra>'
                ))
                fig_pie.update_layout(
                    title=dict(text="Ausgaben nach Kategorie", font=dict(family='Syne', size=14, color='#CBD5E1'), x=0.02),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.35,
                                font=dict(size=11, color='#64748B')),
                    margin=dict(t=40,b=70,l=0,r=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E2E8F0'),
                    annotations=[dict(text=f"<b>{format_euro(sum(kat_dist.values()))}</b>",
                                      x=0.5, y=0.5, font_size=13, showarrow=False,
                                      font=dict(color='#94A3B8', family='Syne'))]
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        with co2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Einnahmen', x=f_df['Monat'], y=f_df['Einnahmen'],
                marker=dict(color='rgba(0,212,255,0.7)',
                            line=dict(color='rgba(0,212,255,0.9)', width=1)),
                hovertemplate='<b>Einnahmen</b><br>%{x}: %{y:,.2f} €<extra></extra>'
            ))
            fig.add_trace(go.Bar(
                name='Ausgaben', x=f_df['Monat'], y=f_df['Ausgaben'],
                marker=dict(color='rgba(255,76,106,0.65)',
                            line=dict(color='rgba(255,76,106,0.9)', width=1)),
                hovertemplate='<b>Ausgaben</b><br>%{x}: %{y:,.2f} €<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                name='Saldo', x=f_df['Monat'], y=f_df['Saldo'],
                mode='lines+markers',
                line=dict(color='#00FF87', width=2, dash='dot'),
                marker=dict(size=7, color='#00FF87', line=dict(color='#080B14', width=2)),
                hovertemplate='<b>Saldo</b><br>%{x}: %{y:,.2f} €<extra></extra>'
            ))
            fig.update_layout(
                title=dict(text=f"Cashflow – {zeitraum} Monate",
                           font=dict(family='Syne', size=14, color='#CBD5E1'), x=0.02),
                barmode='group', bargap=0.25, bargroupgap=0.08,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E2E8F0', family='DM Sans'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.35,
                            font=dict(size=11, color='#64748B')),
                margin=dict(t=40, b=70, l=0, r=0),
                xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(size=11, color='#64748B')),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(size=11, color='#64748B'),
                           tickformat=',.0f')
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── MONATS-DETAIL ──
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;
                color:#CBD5E1;margin:0 0 0.7rem 0;letter-spacing:-0.01em;">
        📅 Detailübersicht
    </div>""", unsafe_allow_html=True)

    for i, monat in enumerate(t_df['Monat'].unique()):
        m_sub     = t_df[t_df['Monat'] == monat].sort_values(
                        by=["Ist_Fällig", "Typ_Internal"], ascending=[False, True])
        ein_sum   = m_sub[m_sub['Typ_Internal'] == 'Einnahme']['Betrag (fällig)'].sum()
        aus_sum   = m_sub[m_sub['Typ_Internal'] == 'Ausgabe']['Betrag (fällig)'].sum()
        saldo_m   = ein_sum - aus_sum
        s_color   = "#00FF87" if saldo_m >= 0 else "#FF4C6A"
        s_icon    = "▲" if saldo_m >= 0 else "▼"

        exp_label = (
            f"📅 **{monat}**"
            f"  ·  Saldo: {format_euro(saldo_m)}"
            f"  ·  💰 {format_euro(ein_sum)}"
            f"  ·  💸 {format_euro(aus_sum)}"
        )
        with st.expander(exp_label, expanded=(i == 0)):
            display_cols = [" ", "Konto", "Zweck", "Kategorie", "Betrag (fällig)", "Anteilig p.M.", "Turnus"]
            styled = (
                m_sub.style
                .apply(_style_row, axis=1)
                .format({"Betrag (fällig)": format_euro, "Anteilig p.M.": format_euro})
            )
            st.dataframe(styled, use_container_width=True, hide_index=True, column_order=display_cols)


def entries_page(conn, u_id):
    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <h1 style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;
                   letter-spacing:-0.035em;margin:0;color:#E2E8F0;">Einträge</h1>
        <p style="color:#475569;margin:0.2rem 0 0;font-size:0.87rem;">
            Alle deine Buchungen, Abos und Finanzierungen
        </p>
    </div>""", unsafe_allow_html=True)

    df_entries = pd.read_sql_query(
        """SELECT e.*, k.name as konto_name
           FROM eintraege e JOIN konten k ON e.konto_id = k.id
           WHERE e.user_id=%s ORDER BY e.start_datum DESC""",
        conn, params=(u_id,)
    )

    if df_entries.empty:
        st.markdown("""
        <div style="text-align:center;padding:3rem;background:rgba(255,255,255,0.02);
                    border:1px solid rgba(255,255,255,0.06);border-radius:16px;">
            <div style="font-size:2.5rem;margin-bottom:0.8rem;">📭</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                        color:#CBD5E1;margin-bottom:0.4rem;">Noch keine Einträge</div>
        </div>""", unsafe_allow_html=True)
        if st.button("＋ Ersten Eintrag anlegen", type="primary"):
            eintrag_dialog(conn, u_id)
        return

    def format_display(subset):
        d = subset[['zweck','konto_name','kategorie','betrag','betrag_typ','typ','intervall','start_datum','end_datum']].copy()
        d['betrag']     = d['betrag'].apply(format_euro)
        d['start_datum'] = pd.to_datetime(d['start_datum']).dt.strftime('%d.%m.%Y')
        d['end_datum']  = d['end_datum'].apply(
            lambda x: pd.to_datetime(x).strftime('%d.%m.%Y') if pd.notna(x) and x else 'Offen'
        )
        return d.rename(columns={
            'zweck':'Zweck','konto_name':'Konto','kategorie':'Kategorie',
            'betrag':'Betrag','betrag_typ':'Betrag-Typ','typ':'Typ',
            'intervall':'Turnus','start_datum':'Start','end_datum':'Ende'
        })

    # Farbcodierung pro Gruppe
    gruppen = [
        ("Buchung",      "💸 Buchungen",       "booking", "#00D4FF"),
        ("Abo",          "🔄 Abos",             "abo",     "#00FF87"),
        ("Finanzierung", "📉 Finanzierungen",   "fin",     "#FFB800"),
    ]

    for art, label, key, color in gruppen:
        subset = df_entries[df_entries['art'] == art].copy()
        if subset.empty:
            continue

        aktiv = subset
        abgeschlossen = pd.DataFrame()
        if art == "Finanzierung":
            mask_abg = subset['end_datum'].notna() & \
                       (pd.to_datetime(subset['end_datum'], errors='coerce') < pd.Timestamp.now())
            aktiv       = subset[~mask_abg]
            abgeschlossen = subset[mask_abg]

        _section_header(label, count=len(aktiv), color=color)

        if aktiv.empty:
            st.markdown(f"<p style='color:#334155;font-size:0.85rem;margin:0.3rem 0 0.8rem 0.5rem;'>Keine aktiven Einträge.</p>", unsafe_allow_html=True)
        else:
            se = st.dataframe(format_display(aktiv), use_container_width=True,
                              hide_index=True, on_select="rerun",
                              selection_mode="single-row", key=f"tbl_{key}")

            if se.selection.rows:
                row = aktiv.iloc[se.selection.rows[0]]
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                            border-radius:10px;padding:0.6rem 1rem;margin:0.4rem 0;
                            display:flex;align-items:center;gap:0.5rem;font-size:0.88rem;color:#94A3B8;">
                    {get_emoji(row['art'],row['typ'])}
                    <strong style="color:#CBD5E1;">{row['zweck']}</strong>
                    <span style="margin-left:auto;color:#475569;">Ausgewählt</span>
                </div>""", unsafe_allow_html=True)

                col1, col2, col3 = st.columns([2, 2, 6])
                with col1:
                    if st.button("✏️ Bearbeiten", key=f"edit_{key}", use_container_width=True):
                        eintrag_dialog(conn, u_id, row['id'])
                with col2:
                    if st.button("🗑️ Löschen", key=f"del_{key}", use_container_width=True):
                        c = conn.cursor()
                        try:
                            c.execute("DELETE FROM eintraege WHERE id=%s AND user_id=%s",
                                      (int(row['id']), u_id))
                            conn.commit(); st.rerun()
                        except Exception as e:
                            conn.rollback(); st.error(f"Fehler: {e}")
                        finally:
                            c.close()

        if not abgeschlossen.empty:
            with st.expander(f"📦 Abgeschlossene Finanzierungen ({len(abgeschlossen)})"):
                st.dataframe(format_display(abgeschlossen),
                             use_container_width=True, hide_index=True)

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)


def settings_page(conn, u_id):
    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <h1 style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;
                   letter-spacing:-0.035em;margin:0;color:#E2E8F0;">Verwaltung</h1>
        <p style="color:#475569;margin:0.2rem 0 0;font-size:0.87rem;">
            Konten und Kategorien verwalten
        </p>
    </div>""", unsafe_allow_html=True)

    col_k, col_cat = st.columns(2, gap="large")

    # ── KONTEN ──
    with col_k:
        _section_header("Konten", color="#00D4FF")
        kd = pd.read_sql_query("SELECT * FROM konten WHERE user_id=%s", conn, params=(u_id,))

        if not kd.empty:
            kd['verbundenes_konto'] = kd.apply(
                lambda r: kd[kd['id'] == r['parent_id']]['name'].iloc[0]
                          if pd.notna(r['parent_id']) and not kd[kd['id'] == r['parent_id']].empty else '',
                axis=1
            )
            display_kd = kd[['name','iban','typ','verbundenes_konto']].rename(columns={
                'name':'Name','iban':'IBAN','typ':'Typ','verbundenes_konto':'Verknüpft mit'
            })
            sk = st.dataframe(display_kd, use_container_width=True, hide_index=True,
                              on_select="rerun", selection_mode="single-row")

            if sk.selection.rows:
                sel = kd.iloc[sk.selection.rows[0]]
                st.markdown(f"""
                <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
                            border-radius:8px;padding:0.5rem 0.9rem;margin:0.3rem 0;
                            font-size:0.85rem;color:#64A8B8;">
                    🏦 Ausgewählt: <strong style="color:#00D4FF;">{sel['name']}</strong>
                </div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✏️ Bearbeiten", key="edit_konto", use_container_width=True):
                        konto_dialog(conn, u_id, sel['id'])
                with c2:
                    if st.button("🗑️ Löschen", key="del_konto", use_container_width=True):
                        c = conn.cursor()
                        try:
                            c.execute("DELETE FROM konten WHERE id=%s AND user_id=%s",
                                      (int(sel['id']), u_id))
                            conn.commit(); st.rerun()
                        except Exception as e:
                            conn.rollback(); st.error(f"Fehler: {e}")
                        finally:
                            c.close()
        else:
            st.markdown("<p style='color:#334155;font-size:0.85rem;'>Noch keine Konten.</p>",
                        unsafe_allow_html=True)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        if st.button("＋ Konto hinzufügen", key="add_konto",
                     use_container_width=True, type="primary"):
            konto_dialog(conn, u_id)

    # ── KATEGORIEN ──
    with col_cat:
        _section_header("Kategorien", color="#00FF87")
        ctd = pd.read_sql_query(
            "SELECT * FROM kategorien WHERE user_id=%s ORDER BY name",
            conn, params=(u_id,)
        )

        if not ctd.empty:
            display_ctd = ctd[['name']].rename(columns={'name': 'Name'})
            sct = st.dataframe(display_ctd, use_container_width=True, hide_index=True,
                               on_select="rerun", selection_mode="single-row")

            if sct.selection.rows:
                sel_k = ctd.iloc[sct.selection.rows[0]]
                st.markdown(f"""
                <div style="background:rgba(0,255,135,0.05);border:1px solid rgba(0,255,135,0.15);
                            border-radius:8px;padding:0.5rem 0.9rem;margin:0.3rem 0;
                            font-size:0.85rem;color:#4DB875;">
                    📂 Ausgewählt: <strong style="color:#00FF87;">{sel_k['name']}</strong>
                </div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✏️ Bearbeiten", key="edit_kat", use_container_width=True):
                        kategorie_dialog(conn, u_id, sel_k['id'])
                with c2:
                    if st.button("🗑️ Löschen", key="del_kat", use_container_width=True):
                        c = conn.cursor()
                        try:
                            c.execute("DELETE FROM kategorien WHERE id=%s AND user_id=%s",
                                      (int(sel_k['id']), u_id))
                            conn.commit(); st.rerun()
                        except Exception as e:
                            conn.rollback(); st.error(f"Fehler: {e}")
                        finally:
                            c.close()
        else:
            st.markdown("<p style='color:#334155;font-size:0.85rem;'>Noch keine Kategorien.</p>",
                        unsafe_allow_html=True)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        if st.button("＋ Kategorie hinzufügen", key="add_kat",
                     use_container_width=True, type="primary"):
            kategorie_dialog(conn, u_id)
