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
    """Zeilenstyle für Forecast-Tabelle."""
    if row['Typ_Internal'] == 'Einnahme':
        bg = 'background-color: rgba(79, 142, 247, 0.08)'
    else:
        bg = 'background-color: rgba(231, 76, 60, 0.08)'

    if not row['Ist_Fällig']:
        text = 'color: #555; font-style: italic'
    else:
        text = 'font-weight: 500'

    return [f'{bg}; {text}'] * len(row)


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
    kats_df = pd.read_sql_query("SELECT * FROM kategorien WHERE user_id=%s", conn, params=(u_id,))

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
            k_idx = 0
            if existing is not None:
                try:
                    current_k_name = konten_df[konten_df['id'] == int(existing['konto_id'])]['name'].iloc[0]
                    k_idx = k_list.index(current_k_name) if current_k_name in k_list else 0
                except (IndexError, KeyError):
                    k_idx = 0
            k_auswahl = st.selectbox("Konto", k_list, index=k_idx)

            kat_list = kats_df['name'].tolist()
            kat_idx = (
                kat_list.index(existing['kategorie'])
                if existing is not None and existing['kategorie'] in kat_list
                else 0
            )
            kategorie = st.selectbox("Kategorie", kat_list, index=kat_idx)

            zweck = st.text_input(
                "Zweck / Bezeichnung",
                value=existing['zweck'] if existing is not None else "",
                placeholder="z.B. Netflix, Miete, Autokredit..."
            )

        with c2:
            typ = st.selectbox(
                "Ein-/Ausgabe",
                ["Einnahme", "Ausgabe"],
                index=0 if (existing is None or existing['typ'] == "Einnahme") else 1
            )

            betrag_label = (
                "Betrag (€)" if art_val != "Finanzierung"
                else ("Gesamtbetrag (€)" if betrag_typ == "Gesamtbetrag" else "Monatliche Rate (€)")
            )
            betrag = st.number_input(
                betrag_label,
                min_value=0.0,
                step=0.01,
                value=float(existing['betrag']) if existing is not None else 0.0
            )

            if art_val != "Finanzierung":
                curr_int = existing['intervall'] if existing is not None else "Monatlich"
                int_idx = turnus_optionen.index(curr_int) if curr_int in turnus_optionen else 0
                intervall = st.selectbox("Turnus", turnus_optionen, index=int_idx)
            else:
                intervall = "Monatlich"

        st.divider()

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            s_date_val = (
                datetime.fromisoformat(existing['start_datum']).date()
                if existing is not None and existing['start_datum']
                else datetime.now().date()
            )
            start_d = st.date_input("Startdatum", value=s_date_val)

        with col_d2:
            e_date_val = (
                datetime.fromisoformat(existing['end_datum']).date()
                if existing is not None and existing['end_datum']
                else None
            )
            end_d = st.date_input("Enddatum (optional)", value=e_date_val)

        # Info-Box bei Finanzierung
        if art_val == "Finanzierung" and end_d and start_d:
            num_months = calculate_months(start_d.isoformat(), end_d.isoformat())
            if betrag > 0:
                if betrag_typ == "Gesamtbetrag":
                    monthly_rate = betrag / num_months if num_months > 0 else 0
                    st.info(f"📅 Laufzeit: **{num_months} Monate** · Monatliche Rate: **{format_euro(monthly_rate)}**")
                else:
                    total = betrag * num_months
                    st.info(f"📅 Laufzeit: **{num_months} Monate** · Gesamtbetrag: **{format_euro(total)}**")

        kuend = None
        if art_val == "Abo":
            kuend = st.number_input(
                "Kündigungsfrist (Tage)",
                min_value=0,
                value=int(existing['kuendigung_tage']) if existing is not None and existing['kuendigung_tage'] else 30,
                help="Wie viele Tage vor Verlängerung musst du kündigen?"
            )

        col_save, col_cancel = st.columns([3, 1])
        with col_save:
            save = st.form_submit_button("💾 Speichern", use_container_width=True, type="primary")
        with col_cancel:
            st.form_submit_button("Abbrechen", use_container_width=True)

        if save:
            if not zweck:
                st.error("Bitte einen Zweck eingeben.")
                return
            if betrag <= 0:
                st.error("Betrag muss größer als 0 sein.")
                return

            k_id = int(konten_df[konten_df['name'] == k_auswahl]['id'].iloc[0])
            final_start = start_d.isoformat()
            final_end = end_d.isoformat() if end_d else None

            c = conn.cursor()
            try:
                if existing is not None:
                    c.execute('''
                        UPDATE eintraege SET
                            art=%s, konto_id=%s, kategorie=%s, zweck=%s,
                            betrag=%s, betrag_typ=%s, typ=%s, intervall=%s,
                            start_datum=%s, end_datum=%s, kuendigung_tage=%s
                        WHERE id=%s AND user_id=%s
                    ''', (art_val, k_id, kategorie, zweck, betrag, betrag_typ, typ,
                          intervall, final_start, final_end, kuend, int(existing['id']), u_id))
                else:
                    c.execute('''
                        INSERT INTO eintraege (
                            user_id, art, konto_id, kategorie, zweck,
                            betrag, betrag_typ, typ, intervall,
                            start_datum, end_datum, kuendigung_tage
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ''', (u_id, art_val, k_id, kategorie, zweck, betrag, betrag_typ,
                          typ, intervall, final_start, final_end, kuend))
                conn.commit()
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Fehler beim Speichern: {e}")
            finally:
                c.close()


@st.dialog("Konto bearbeiten / neu")
def konto_dialog(conn, u_id, edit_id=None):
    existing = None
    konten_df = pd.DataFrame()
    if edit_id:
        df = pd.read_sql_query(
            "SELECT * FROM konten WHERE id=%s AND user_id=%s",
            conn, params=(edit_id, u_id)
        )
        if not df.empty:
            existing = df.iloc[0]

    with st.form("konto_form"):
        typ = st.selectbox(
            "Kontotyp",
            ["Bankkonto", "Zahldienstleister"],
            index=0 if (existing is None or existing['typ'] == "Bankkonto") else 1
        )
        name = st.text_input("Name", value=existing['name'] if existing is not None else "",
                             placeholder="z.B. DKB Girokonto, PayPal...")
        iban = ""
        if typ == "Bankkonto":
            iban = st.text_input(
                "IBAN (optional)",
                value=existing['iban'] if existing is not None else "",
                placeholder="DE00 0000 0000 0000 0000 00"
            )

        parent = None
        if typ == "Zahldienstleister":
            konten_df = pd.read_sql_query(
                "SELECT * FROM konten WHERE user_id=%s AND typ='Bankkonto'",
                conn, params=(u_id,)
            )
            if not konten_df.empty:
                bankkonten = konten_df['name'].tolist()
                current_parent = None
                if existing is not None and existing['parent_id']:
                    match = konten_df[konten_df['id'] == existing['parent_id']]['name']
                    current_parent = match.iloc[0] if not match.empty else None
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
                    c.execute(
                        "UPDATE konten SET name=%s, iban=%s, typ=%s, parent_id=%s WHERE id=%s AND user_id=%s",
                        (name, iban, typ, parent_id, int(existing['id']), u_id)
                    )
                else:
                    c.execute(
                        "INSERT INTO konten (user_id, name, iban, typ, parent_id) VALUES (%s,%s,%s,%s,%s)",
                        (u_id, name, iban, typ, parent_id)
                    )
                conn.commit()
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Fehler: {e}")
            finally:
                c.close()


@st.dialog("Kategorie bearbeiten / neu")
def kategorie_dialog(conn, u_id, edit_id=None):
    existing = None
    if edit_id:
        df = pd.read_sql_query(
            "SELECT * FROM kategorien WHERE id=%s AND user_id=%s",
            conn, params=(edit_id, u_id)
        )
        if not df.empty:
            existing = df.iloc[0]

    with st.form("kategorie_form"):
        name = st.text_input(
            "Kategoriename",
            value=existing['name'] if existing is not None else "",
            placeholder="z.B. Sport, Streaming, Haushalt..."
        )
        if st.form_submit_button("💾 Speichern", use_container_width=True, type="primary"):
            if not name:
                st.error("Bitte einen Namen eingeben.")
                return
            c = conn.cursor()
            try:
                if existing is not None:
                    c.execute(
                        "UPDATE kategorien SET name=%s WHERE id=%s AND user_id=%s",
                        (name, int(existing['id']), u_id)
                    )
                else:
                    c.execute(
                        "INSERT INTO kategorien (user_id, name) VALUES (%s,%s)",
                        (u_id, name)
                    )
                conn.commit()
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Fehler: {e}")
            finally:
                c.close()


# ---------------------------------------------------------------------------
# SEITEN
# ---------------------------------------------------------------------------

def dashboard_page(conn, u_id):
    from forecast import get_forecast_detailed

    st.title("📊 Dashboard")

    zeitraum = st.segmented_control(
        "Vorschau-Zeitraum",
        [3, 6, 12],
        default=3,
        format_func=lambda x: f"{x} Monate"
    )

    f_df, t_df, m_ein, m_aus_ist, m_aus_ant, kat_dist = get_forecast_detailed(conn, u_id, zeitraum)

    if f_df.empty or t_df.empty:
        st.info("📭 Noch keine Einträge vorhanden. Lege zuerst ein Konto und Einträge an.")
        with st.columns([1, 2, 1])[1]:
            if st.button("➕ Ersten Eintrag anlegen", use_container_width=True, type="primary"):
                eintrag_dialog(conn, u_id)
        return

    saldo = m_ein - m_aus_ist
    saldo_color = "#4CAF50" if saldo >= 0 else "#F44336"

    # --- KPI METRIKEN ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Einnahmen (Monat)", format_euro(m_ein))
    with col2:
        st.metric("💸 Ausgaben (fällig)", format_euro(m_aus_ist))
    with col3:
        st.metric("📊 Ausgaben (anteilig)", format_euro(m_aus_ant),
                  help="Gleichmäßig verteilte monatliche Last inkl. quartals-/jährlicher Posten")
    with col4:
        delta_str = f"{'▲' if saldo >= 0 else '▼'} {format_euro(abs(saldo - m_aus_ant))}" if saldo != (m_ein - m_aus_ant) else None
        st.metric("✅ Verfügbar (Ist)", format_euro(saldo),
                  delta=f"{'+' if saldo >= 0 else ''}{format_euro(saldo)}" if saldo != 0 else None)

    st.divider()

    # --- CHARTS ---
    with st.expander("📈 Statistiken & Grafiken", expanded=True):
        co1, co2 = st.columns(2)

        with co1:
            if kat_dist:
                fig_pie = px.pie(
                    names=list(kat_dist.keys()),
                    values=list(kat_dist.values()),
                    hole=0.5,
                    title="Ausgaben nach Kategorie",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                    margin=dict(t=40, b=60, l=0, r=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E8EAF0')
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        with co2:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name='Einnahmen', x=f_df['Monat'], y=f_df['Einnahmen'],
                marker_color='#4F8EF7', marker_opacity=0.85
            ))
            fig_bar.add_trace(go.Bar(
                name='Ausgaben', x=f_df['Monat'], y=f_df['Ausgaben'],
                marker_color='#E74C3C', marker_opacity=0.85
            ))
            fig_bar.add_trace(go.Scatter(
                name='Saldo', x=f_df['Monat'], y=f_df['Saldo'],
                mode='lines+markers', line=dict(color='#2ECC71', width=2),
                marker=dict(size=6)
            ))
            fig_bar.update_layout(
                title=f"Cashflow – {zeitraum} Monate",
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E8EAF0'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                margin=dict(t=40, b=60, l=0, r=0),
                xaxis=dict(gridcolor='#2A2D3E'),
                yaxis=dict(gridcolor='#2A2D3E')
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- MONATS-TABELLEN ---
    st.subheader("📅 Detailübersicht")
    for monat in t_df['Monat'].unique():
        m_sub = t_df[t_df['Monat'] == monat].sort_values(by=["Ist_Fällig", "Typ_Internal"], ascending=[False, True])
        ein_sum = m_sub[m_sub['Typ_Internal'] == 'Einnahme']['Betrag (fällig)'].sum()
        aus_sum = m_sub[m_sub['Typ_Internal'] == 'Ausgabe']['Betrag (fällig)'].sum()
        saldo_m = ein_sum - aus_sum
        saldo_icon = "🟢" if saldo_m >= 0 else "🔴"

        with st.expander(f"📅 {monat}  ·  {saldo_icon} Saldo: {format_euro(saldo_m)}  ·  💰 {format_euro(ein_sum)}  💸 {format_euro(aus_sum)}", expanded=(monat == t_df['Monat'].iloc[0])):
            display_cols = [" ", "Konto", "Zweck", "Kategorie", "Betrag (fällig)", "Anteilig p.M.", "Turnus"]
            styled = (
                m_sub.style
                .apply(_style_row, axis=1)
                .format({"Betrag (fällig)": format_euro, "Anteilig p.M.": format_euro})
            )
            st.dataframe(styled, use_container_width=True, hide_index=True, column_order=display_cols)


def entries_page(conn, u_id):
    st.header("📝 Deine Einträge")

    df_entries = pd.read_sql_query(
        "SELECT e.*, k.name as konto_name FROM eintraege e JOIN konten k ON e.konto_id = k.id WHERE e.user_id=%s ORDER BY e.start_datum DESC",
        conn, params=(u_id,)
    )

    if df_entries.empty:
        st.info("📭 Noch keine Einträge vorhanden.")
        if st.button("➕ Ersten Eintrag anlegen", type="primary"):
            eintrag_dialog(conn, u_id)
        return

    def format_entries_display(subset):
        """Hilfsfunktion: DataFrame für Anzeige aufbereiten."""
        display = subset[['zweck', 'konto_name', 'kategorie', 'betrag', 'betrag_typ', 'typ', 'intervall', 'start_datum', 'end_datum']].copy()
        display['betrag'] = display['betrag'].apply(format_euro)
        display['start_datum'] = pd.to_datetime(display['start_datum']).dt.strftime('%d.%m.%Y')
        display['end_datum'] = display['end_datum'].apply(
            lambda x: pd.to_datetime(x).strftime('%d.%m.%Y') if pd.notna(x) and x else 'Offen'
        )
        return display.rename(columns={
            'zweck': 'Zweck', 'konto_name': 'Konto', 'kategorie': 'Kategorie',
            'betrag': 'Betrag', 'betrag_typ': 'Betrag-Typ', 'typ': 'Typ',
            'intervall': 'Turnus', 'start_datum': 'Start', 'end_datum': 'Ende'
        })

    gruppen_config = [
        ("Buchung",     "💸 Buchungen",     "booking"),
        ("Abo",         "🔄 Abos",          "abo"),
        ("Finanzierung","📉 Finanzierungen", "fin"),
    ]

    for art, label, key in gruppen_config:
        subset = df_entries[df_entries['art'] == art].copy()
        if subset.empty:
            continue

        aktiv = subset
        if art == "Finanzierung":
            aktiv = subset[
                subset['end_datum'].isna() |
                (pd.to_datetime(subset['end_datum'], errors='coerce') >= pd.Timestamp.now())
            ]
            abgeschlossen = subset[
                subset['end_datum'].notna() &
                (pd.to_datetime(subset['end_datum'], errors='coerce') < pd.Timestamp.now())
            ]

        st.subheader(f"{label} ({len(aktiv)})")
        display = format_entries_display(aktiv)
        se = st.dataframe(display, use_container_width=True, hide_index=True,
                          on_select="rerun", selection_mode="single-row",
                          key=f"tbl_{key}")

        if se.selection.rows:
            selected_row = aktiv.iloc[se.selection.rows[0]]
            st.markdown(f"**Ausgewählt:** {get_emoji(selected_row['art'], selected_row['typ'])} {selected_row['zweck']}")
            col1, col2, col3 = st.columns([2, 2, 6])
            with col1:
                if st.button("✏️ Bearbeiten", key=f"edit_{key}", use_container_width=True):
                    eintrag_dialog(conn, u_id, selected_row['id'])
            with col2:
                if st.button("🗑️ Löschen", key=f"del_{key}", use_container_width=True):
                    c = conn.cursor()
                    try:
                        c.execute("DELETE FROM eintraege WHERE id=%s AND user_id=%s",
                                  (int(selected_row['id']), u_id))
                        conn.commit()
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Fehler: {e}")
                    finally:
                        c.close()

        # Abgeschlossene Finanzierungen separat
        if art == "Finanzierung" and not abgeschlossen.empty:
            with st.expander(f"📦 Abgeschlossene Finanzierungen ({len(abgeschlossen)})"):
                st.dataframe(format_entries_display(abgeschlossen),
                             use_container_width=True, hide_index=True)

        st.divider()


def settings_page(conn, u_id):
    st.header("⚙️ Verwaltung")

    col_k, col_cat = st.columns(2)

    with col_k:
        st.subheader("🏦 Konten")
        kd = pd.read_sql_query("SELECT * FROM konten WHERE user_id=%s", conn, params=(u_id,))

        if not kd.empty:
            kd['verbundenes_konto'] = kd.apply(
                lambda row: kd[kd['id'] == row['parent_id']]['name'].iloc[0]
                if pd.notna(row['parent_id']) and not kd[kd['id'] == row['parent_id']].empty
                else '', axis=1
            )
            display_kd = kd[['name', 'iban', 'typ', 'verbundenes_konto']].rename(columns={
                'name': 'Name', 'iban': 'IBAN', 'typ': 'Typ', 'verbundenes_konto': 'Verknüpft mit'
            })
            sk = st.dataframe(display_kd, use_container_width=True, hide_index=True,
                              on_select="rerun", selection_mode="single-row")

            if sk.selection.rows:
                selected_konto = kd.iloc[sk.selection.rows[0]]
                st.markdown(f"**Ausgewählt:** 🏦 {selected_konto['name']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Bearbeiten", key="edit_konto", use_container_width=True):
                        konto_dialog(conn, u_id, selected_konto['id'])
                with col2:
                    if st.button("🗑️ Löschen", key="delete_konto", use_container_width=True):
                        c = conn.cursor()
                        try:
                            c.execute("DELETE FROM konten WHERE id=%s AND user_id=%s",
                                      (int(selected_konto['id']), u_id))
                            conn.commit()
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Fehler: {e}")
                        finally:
                            c.close()
        else:
            st.info("Noch keine Konten vorhanden.")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("➕ Konto hinzufügen", key="add_konto", use_container_width=True, type="primary"):
            konto_dialog(conn, u_id)

    with col_cat:
        st.subheader("📂 Kategorien")
        ctd = pd.read_sql_query("SELECT * FROM kategorien WHERE user_id=%s ORDER BY name", conn, params=(u_id,))

        if not ctd.empty:
            display_ctd = ctd[['name']].rename(columns={'name': 'Name'})
            sct = st.dataframe(display_ctd, use_container_width=True, hide_index=True,
                               on_select="rerun", selection_mode="single-row")

            if sct.selection.rows:
                selected_kat = ctd.iloc[sct.selection.rows[0]]
                st.markdown(f"**Ausgewählt:** 📂 {selected_kat['name']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Bearbeiten", key="edit_kat", use_container_width=True):
                        kategorie_dialog(conn, u_id, selected_kat['id'])
                with col2:
                    if st.button("🗑️ Löschen", key="delete_kat", use_container_width=True):
                        c = conn.cursor()
                        try:
                            c.execute("DELETE FROM kategorien WHERE id=%s AND user_id=%s",
                                      (int(selected_kat['id']), u_id))
                            conn.commit()
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Fehler: {e}")
                        finally:
                            c.close()
        else:
            st.info("Noch keine Kategorien vorhanden.")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("➕ Kategorie hinzufügen", key="add_kat", use_container_width=True, type="primary"):
            kategorie_dialog(conn, u_id)
