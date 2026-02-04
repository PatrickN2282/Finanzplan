import sys
sys.path.append('.')
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from db import format_euro
from forecast import calculate_months

def get_emoji(art, typ):
    if art == "Buchung":
        return "💰" if typ == "Einnahme" else "💸"
    elif art == "Abo":
        return "🔄"
    elif art == "Finanzierung":
        return "🏦"
    return "❓"

# --- DIALOGE ---
@st.dialog("Eintrag bearbeiten / neu")
def eintrag_dialog(conn, u_id, edit_id=None):
    turnus_optionen = ["Monatlich", "Quartalsweise", "Jährlich"]
    existing = None
    if edit_id:
        df = pd.read_sql_query(f"SELECT * FROM eintraege WHERE id={edit_id} AND user_id={u_id}", conn)
        if not df.empty:
            existing = df.iloc[0]
    art_default = existing['art'] if existing is not None else "Buchung"
    art_val = st.segmented_control("Typ", ["Buchung", "Abo", "Finanzierung"], default=art_default)

    betrag_typ = "Monatlich"
    if art_val == "Finanzierung":
        betrag_typ = st.selectbox("Betrag Typ", ["Gesamtbetrag", "Monatliche Rate"], index=0 if (existing is None or existing['betrag_typ'] == "Gesamtbetrag") else 1)
    else:
        betrag_typ = "Monatlich"

    konten_df = pd.read_sql_query(f"SELECT * FROM konten WHERE user_id={u_id}", conn)
    kats_df = pd.read_sql_query(f"SELECT * FROM kategorien WHERE user_id={u_id}", conn)

    if konten_df.empty:
        st.warning("Bitte lege erst ein Konto in den Einstellungen an!"); return

    with st.form("eintrag_form"):
        c1, c2 = st.columns(2)
        with c1:
            k_list = konten_df['name'].tolist()
            k_idx = 0
            if existing is not None:
                current_k_name = konten_df[konten_df['id'] == existing['konto_id']]['name'].iloc[0]
                k_idx = k_list.index(current_k_name) if current_k_name in k_list else 0
            k_auswahl = st.selectbox("Konto", k_list, index=k_idx)
            kat_list = kats_df['name'].tolist()
            kat_idx = kat_list.index(existing['kategorie']) if existing is not None and existing['kategorie'] in kat_list else 0
            kategorie = st.selectbox("Kategorie", kat_list, index=kat_idx)
            zweck = st.text_input("Zweck", value=existing['zweck'] if existing is not None else "")
        with c2:
            betrag_label = "Betrag (€)" if art_val != "Finanzierung" else ("Gesamtbetrag (€)" if betrag_typ == "Gesamtbetrag" else "Monatliche Rate (€)")
            betrag = st.number_input(betrag_label, min_value=0.0, step=0.01, value=float(existing['betrag']) if existing is not None else 0.0)
            typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"], index=0 if (existing is None or existing['typ'] == "Einnahme") else 1)
            curr_int = existing['intervall'] if existing is not None else "Monatlich"
            int_idx = turnus_optionen.index(curr_int) if curr_int in turnus_optionen else 0
            intervall = st.selectbox("Turnus", turnus_optionen, index=int_idx)

        st.divider()
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            s_date_val = datetime.fromisoformat(existing['start_datum']).date() if existing is not None else datetime.now().date()
            start_d = st.date_input("Startdatum", value=s_date_val)
        with col_d2:
            e_date_val = datetime.fromisoformat(existing['end_datum']).date() if (existing is not None and existing['end_datum']) else None
            end_d = st.date_input("Enddatum (Optional)", value=e_date_val)

        if art_val == "Finanzierung" and end_d:
            num_months = calculate_months(start_d.isoformat(), end_d.isoformat())
            if betrag_typ == "Gesamtbetrag":
                monthly_rate = betrag / num_months if num_months > 0 else 0
                st.info(f"Monatliche Rate: {format_euro(monthly_rate)}")
            else:
                total = betrag * num_months
                st.info(f"Gesamtbetrag: {format_euro(total)}")

        kuend = None
        if art_val == "Abo":
            kuend = st.number_input("Kündigungsfrist (Tage)", value=int(existing['kuendigung_tage']) if existing is not None and existing['kuendigung_tage'] else 30)

        if st.form_submit_button("Speichern"):
            k_id = int(konten_df[konten_df['name'] == k_auswahl]['id'].iloc[0])
            final_start, final_end = start_d.isoformat(), (end_d.isoformat() if end_d else None)
            if existing is not None:
                conn.execute('''UPDATE eintraege SET art=%s, konto_id=%s, kategorie=%s, zweck=%s, betrag=%s, betrag_typ=%s, typ=%s, intervall=%s,
                                start_datum=%s, end_datum=%s, kuendigung_tage=%s WHERE id=%s AND user_id=%s''',
                             (art_val, k_id, kategorie, zweck, betrag, betrag_typ, typ, intervall, final_start, final_end, kuend, int(existing['id']), u_id))
            else:
                conn.execute('''INSERT INTO eintraege (user_id, art, konto_id, kategorie, zweck, betrag, betrag_typ, typ, intervall, start_datum, end_datum, kuendigung_tage)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                             (u_id, art_val, k_id, kategorie, zweck, betrag, betrag_typ, typ, intervall, final_start, final_end, kuend))
            conn.commit(); st.rerun()

@st.dialog("Konto bearbeiten / neu")
def konto_dialog(conn, u_id, edit_id=None):
    existing = None
    if edit_id:
        df = pd.read_sql_query(f"SELECT * FROM konten WHERE id={edit_id} AND user_id={u_id}", conn)
        if not df.empty:
            existing = df.iloc[0]
    
    with st.form("konto_form"):
        typ = st.selectbox("Typ", ["Bankkonto", "Zahldienstleister"], index=0 if (existing is None or existing['typ'] == "Bankkonto") else 1)
        name = st.text_input("Name", value=existing['name'] if existing is not None else "")
        iban = ""
        if typ == "Bankkonto":
            iban = st.text_input("IBAN", value=existing['iban'] if existing is not None else "")
        parent = None
        if typ == "Zahldienstleister":
            konten_df = pd.read_sql_query(f"SELECT * FROM konten WHERE user_id={u_id} AND typ='Bankkonto'", conn)
            if not konten_df.empty:
                bankkonten = konten_df['name'].tolist()
                current_parent = konten_df[konten_df['id'] == existing['parent_id']]['name'].iloc[0] if existing is not None and existing['parent_id'] else None
                parent_idx = bankkonten.index(current_parent) if current_parent in bankkonten else 0
                parent = st.selectbox("Verbundenes Konto", bankkonten, index=parent_idx)
            else:
                st.warning("Lege zuerst ein Bankkonto an.")
        
        if st.form_submit_button("Speichern"):
            parent_id = int(konten_df[konten_df['name'] == parent]['id'].iloc[0]) if parent else None
            if existing is not None:
                conn.execute("UPDATE konten SET name=%s, iban=%s, typ=%s, parent_id=%s WHERE id=%s AND user_id=%s", (name, iban, typ, parent_id, int(existing['id']), u_id))
            else:
                conn.execute("INSERT INTO konten (user_id, name, iban, typ, parent_id) VALUES (%s, %s, %s, %s, %s)", (u_id, name, iban, typ, parent_id))
            conn.commit(); st.rerun()

@st.dialog("Kategorie bearbeiten / neu")
def kategorie_dialog(conn, u_id, edit_id=None):
    existing = None
    if edit_id:
        df = pd.read_sql_query(f"SELECT * FROM kategorien WHERE id={edit_id} AND user_id={u_id}", conn)
        if not df.empty:
            existing = df.iloc[0]
    
    with st.form("kategorie_form"):
        name = st.text_input("Name", value=existing['name'] if existing is not None else "")
        if st.form_submit_button("Speichern"):
            if existing is not None:
                conn.execute("UPDATE kategorien SET name=%s WHERE id=%s AND user_id=%s", (name, int(existing['id']), u_id))
            else:
                conn.execute("INSERT INTO kategorien (user_id, name) VALUES (%s, %s)", (u_id, name))
            conn.commit(); st.rerun()

def dashboard_page(conn, u_id):
    from forecast import get_forecast_detailed
    st.title("📊 Dashboard")
    zeitraum = st.segmented_control("Vorschau Zeitraum", [3, 6, 12], default=3)
    f_df, t_df, m_ein, m_aus_ist, m_aus_ant, kat_dist = get_forecast_detailed(conn, u_id, zeitraum)
    if not f_df.empty:
        # Metriken
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Eingang", format_euro(m_ein))
        with col2:
            st.metric("💸 Ausgaben (Ist)", f"-{format_euro(m_aus_ist)}")
        with col3:
            st.metric("📈 Ausgaben (anteilig)", f"-{format_euro(m_aus_ant)}")
        with col4:
            st.metric("✅ Verfügbar (Ist)", format_euro(m_ein - m_aus_ist))
        
        st.divider()
        
        # Charts
        with st.expander("📊 Statistiken", expanded=True):
            co1, co2 = st.columns(2)
            with co1: 
                st.plotly_chart(px.pie(names=list(kat_dist.keys()), values=list(kat_dist.values()), hole=0.4, title="Kategorienverteilung"), width='stretch')
            with co2: 
                st.plotly_chart(px.bar(f_df, x="Monat", y=["Einnahmen", "Ausgaben"], barmode="group", title="Trend"), width='stretch')
        
        st.divider()
        
        # Tabellen
        if not t_df.empty:
            for monat in t_df['Monat'].unique():
                st.subheader(f"📅 {monat}")
                m_sub = t_df[t_df['Monat'] == monat].sort_values(by="Ist_Fällig", ascending=False)
                def apply_style(row):
                    bg = 'rgba(39, 174, 96, 0.1)' if row['Typ_Internal'] == 'Einnahme' else 'rgba(231, 76, 60, 0.1)'
                    return [f'background-color: {bg}; {"font-weight: bold" if row["Ist_Fällig"] else "color: #888; font-style: italic"}'] * len(row)
                st.dataframe(m_sub.style.apply(apply_style, axis=1).format({"Betrag (fällig)": format_euro, "Anteilig p.M.": format_euro}), width='stretch', hide_index=True, column_order=(" ", "Konto", "Zweck", "Kategorie", "Betrag (fällig)", "Anteilig p.M.", "Turnus"))
        else:
            st.info("Keine Einträge vorhanden. Lege zuerst ein Konto und Einträge an.")

def entries_page(conn, u_id):
    st.header("📝 Deine Einträge")
    df_entries = pd.read_sql_query(f"SELECT e.*, k.name as konto_name FROM eintraege e JOIN konten k ON e.konto_id = k.id WHERE e.user_id={u_id}", conn)
    if not df_entries.empty:
        for gruppe in ["Buchung", "Abo", "Finanzierung"]:
            subset = df_entries[df_entries['art'] == gruppe].copy()
            if not subset.empty:
                subheader_text = {"Abo": "Abos", "Finanzierung": "Finanzierungen", "Buchung": "Buchungen"}.get(gruppe, f"{gruppe}en")
                st.subheader(f"📂 {subheader_text}")
                
                display_subset = subset[['zweck', 'konto_name', 'kategorie', 'betrag', 'betrag_typ', 'typ', 'intervall', 'start_datum', 'end_datum']].copy()
                display_subset['betrag'] = display_subset['betrag'].apply(format_euro)
                display_subset['start_datum'] = pd.to_datetime(display_subset['start_datum']).dt.strftime('%d.%m.%Y')
                display_subset['end_datum'] = display_subset['end_datum'].apply(lambda x: pd.to_datetime(x).strftime('%d.%m.%Y') if pd.notna(x) else 'Offen')
                display_subset = display_subset.rename(columns={
                    'zweck': 'Zweck',
                    'konto_name': 'Konto',
                    'kategorie': 'Kategorie',
                    'betrag': 'Betrag',
                    'betrag_typ': 'Betrag Typ',
                    'typ': 'Typ',
                    'intervall': 'Intervall',
                    'start_datum': 'Start',
                    'end_datum': 'Ende'
                })
                
                se_key = f"se_{gruppe.lower()}"
                se = st.dataframe(display_subset, width='stretch', hide_index=True, on_select="rerun", selection_mode="single-row")
                
                if se.selection.rows:
                    selected_row = subset.iloc[se.selection.rows[0]]
                    st.subheader(f"Ausgewählter Eintrag: {get_emoji(selected_row['art'], selected_row['typ'])} {selected_row['zweck']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ Bearbeiten", key=f"edit_{gruppe.lower()}"):
                            eintrag_dialog(conn, u_id, selected_row['id'])
                    with col2:
                        if st.button("🗑️ Löschen", key=f"delete_{gruppe.lower()}"):
                            conn.execute("DELETE FROM eintraege WHERE id=%s AND user_id=%s", (selected_row['id'], u_id))
                            conn.commit()
                            st.rerun()
        
        # Abgeschlossene Finanzierungen
        abgeschlossene = df_entries[(df_entries['art'] == 'Finanzierung') & (df_entries['end_datum'].notna()) & (pd.to_datetime(df_entries['end_datum']) < pd.Timestamp.now())]
        if not abgeschlossene.empty:
            st.subheader("📂 Abgeschlossene Finanzierungen")
            display_abgeschlossene = abgeschlossene[['zweck', 'konto_name', 'kategorie', 'betrag', 'betrag_typ', 'typ', 'intervall', 'start_datum', 'end_datum']].copy()
            display_abgeschlossene['betrag'] = display_abgeschlossene['betrag'].apply(format_euro)
            display_abgeschlossene['start_datum'] = pd.to_datetime(display_abgeschlossene['start_datum']).dt.strftime('%d.%m.%Y')
            display_abgeschlossene['end_datum'] = display_abgeschlossene['end_datum'].apply(lambda x: pd.to_datetime(x).strftime('%d.%m.%Y') if pd.notna(x) else 'Offen')
            display_abgeschlossene = display_abgeschlossene.rename(columns={
                'zweck': 'Zweck',
                'konto_name': 'Konto',
                'kategorie': 'Kategorie',
                'betrag': 'Betrag',
                'betrag_typ': 'Betrag Typ',
                'typ': 'Typ',
                'intervall': 'Intervall',
                'start_datum': 'Start',
                'end_datum': 'Ende'
            })
            st.dataframe(display_abgeschlossene, width='stretch', hide_index=True)

def settings_page(conn, u_id):
    st.header("⚙️ Verwaltung")
    col_k, col_cat = st.columns(2)
    with col_k:
        st.subheader("🏦 Deine Konten")
        kd = pd.read_sql_query(f"SELECT * FROM konten WHERE user_id={u_id}", conn)
        kd['verbundenes_konto'] = kd.apply(lambda row: kd[kd['id'] == row['parent_id']]['name'].iloc[0] if pd.notna(row['parent_id']) else '', axis=1)
        display_kd = kd[['name', 'iban', 'typ', 'verbundenes_konto']].copy()
        display_kd = display_kd.rename(columns={'name': 'Name', 'iban': 'IBAN', 'typ': 'Typ', 'verbundenes_konto': 'Verbundenes Konto'})
        sk = st.dataframe(display_kd, width='stretch', hide_index=True, on_select="rerun", selection_mode="single-row")
        if sk.selection.rows:
            selected_konto = kd.iloc[sk.selection.rows[0]]
            st.subheader(f"Ausgewähltes Konto: 🏦 {selected_konto['name']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Bearbeiten", key="edit_konto"):
                    konto_dialog(conn, u_id, selected_konto['id'])
            with col2:
                if st.button("🗑️ Löschen", key="delete_konto"):
                    conn.execute("DELETE FROM konten WHERE id=%s AND user_id=%s", (int(selected_konto['id']), u_id))
                    conn.commit()
                    st.rerun()
        
        with st.expander("➕ Neues Konto"):
            if st.button("Neues Konto hinzufügen"):
                konto_dialog(conn, u_id)
    
    with col_cat:
        st.subheader("📂 Deine Kategorien")
        ctd = pd.read_sql_query(f"SELECT * FROM kategorien WHERE user_id={u_id}", conn)
        display_ctd = ctd[['name']].copy()
        display_ctd = display_ctd.rename(columns={'name': 'Name'})
        sct = st.dataframe(display_ctd, width='stretch', hide_index=True, on_select="rerun", selection_mode="single-row")
        if sct.selection.rows:
            selected_kat = ctd.iloc[sct.selection.rows[0]]
            st.subheader(f"Ausgewählte Kategorie: 📂 {selected_kat['name']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Bearbeiten", key="edit_kategorie"):
                    kategorie_dialog(conn, u_id, selected_kat['id'])
            with col2:
                if st.button("🗑️ Löschen", key="delete_kategorie"):
                    conn.execute("DELETE FROM kategorien WHERE id=%s AND user_id=%s", (int(selected_kat['id']), u_id))
                    conn.commit()
                    st.rerun()
        
        with st.expander("➕ Neue Kategorie"):
            if st.button("Neue Kategorie hinzufügen"):
                kategorie_dialog(conn, u_id)