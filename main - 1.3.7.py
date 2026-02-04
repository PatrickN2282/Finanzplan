import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px

# --- DATENBANK SETUP ---
def init_db():
    conn = sqlite3.connect("finanzen_pro_v1_3.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS konten (id INTEGER PRIMARY KEY, name TEXT, iban TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS kategorien (id INTEGER PRIMARY KEY, name TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS eintraege 
                 (id INTEGER PRIMARY KEY, art TEXT, konto_id INTEGER, kategorie TEXT, zweck TEXT, 
                  betrag REAL, typ TEXT, intervall TEXT, start_datum TEXT, end_datum TEXT,
                  kuendigung_tage INTEGER)''')
    
    c.execute("SELECT count(*) FROM konten")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO konten (name, iban) VALUES (?,?)", ("Hauptkonto", "DE00 0000 ..."))
    c.execute("SELECT count(*) FROM kategorien")
    if c.fetchone()[0] == 0:
        for kat in ["Gehalt", "Miete", "Lebensmittel", "Freizeit", "Auto", "Versicherung"]:
            c.execute("INSERT INTO kategorien (name) VALUES (?)", (kat,))
    conn.commit()
    return conn

st.set_page_config(page_title="Finanz-Master v1.3.7", layout="wide")
if 'conn' not in st.session_state:
    st.session_state.conn = init_db()
conn = st.session_state.conn

# --- HILFSFUNKTIONEN ---
def format_euro(val):
    if val is None: return "0,00 €"
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"

def get_emoji(art, typ):
    if typ == "Einnahme": return "💰"
    if art == "Abo": return "🔄"
    if art == "Finanzierung": return "📉"
    return "💸"

# --- DIALOGE ---
@st.dialog("Eintrag bearbeiten / neu")
def eintrag_dialog(edit_id=None):
    existing = None
    turnus_optionen = ["Monatlich", "Quartalsweise", "Jährlich"]
    
    if edit_id:
        existing = pd.read_sql_query(f"SELECT * FROM eintraege WHERE id={edit_id}", conn).iloc[0]
        art_val = existing['art']
    else:
        art_val = st.segmented_control("Typ", ["Buchung", "Abo", "Finanzierung"], default="Buchung")

    konten_df = pd.read_sql_query("SELECT * FROM konten", conn)
    kats_df = pd.read_sql_query("SELECT * FROM kategorien", conn)

    with st.form("eintrag_form"):
        c1, c2 = st.columns(2)
        with c1:
            k_list = konten_df['name'].tolist()
            k_idx = 0
            if edit_id:
                current_k_name = konten_df[konten_df['id'] == existing['konto_id']]['name'].iloc[0]
                k_idx = k_list.index(current_k_name) if current_k_name in k_list else 0
            k_auswahl = st.selectbox("Konto", k_list, index=k_idx)
            
            kat_list = kats_df['name'].tolist()
            kat_idx = kat_list.index(existing['kategorie']) if edit_id and existing['kategorie'] in kat_list else 0
            kategorie = st.selectbox("Kategorie", kat_list, index=kat_idx)
            zweck = st.text_input("Zweck", value=existing['zweck'] if edit_id else "")
        with c2:
            betrag = st.number_input("Betrag (€)", min_value=0.0, step=0.01, value=float(existing['betrag']) if edit_id else 0.0)
            typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"], index=0 if (not edit_id or existing['typ'] == "Einnahme") else 1)
            
            curr_int = existing['intervall'] if edit_id else "Monatlich"
            int_idx = turnus_optionen.index(curr_int) if curr_int in turnus_optionen else 0
            intervall = st.selectbox("Turnus", turnus_optionen, index=int_idx)

        st.divider()
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            s_date_val = datetime.fromisoformat(existing['start_datum']).date() if edit_id else datetime.now().date()
            start_d = st.date_input("Startdatum", value=s_date_val)
        with col_d2:
            e_date_val = None
            if edit_id and existing['end_datum']:
                try:
                    e_date_val = datetime.fromisoformat(existing['end_datum']).date()
                except: e_date_val = None
            end_d = st.date_input("Enddatum (Optional)", value=e_date_val)

        kuend = None
        if art_val == "Abo":
            kuend = st.number_input("Kündigungsfrist (Tage)", value=int(existing['kuendigung_tage']) if edit_id and existing['kuendigung_tage'] else 30)

        if st.form_submit_button("Speichern"):
            k_id = int(konten_df[konten_df['name'] == k_auswahl]['id'].iloc[0])
            final_start = start_d.isoformat()
            final_end = end_d.isoformat() if end_d else None
            
            if edit_id:
                conn.execute('''UPDATE eintraege 
                                SET konto_id=?, kategorie=?, zweck=?, betrag=?, typ=?, intervall=?, 
                                    start_datum=?, end_datum=?, kuendigung_tage=? 
                                WHERE id=?''',
                             (k_id, kategorie, zweck, betrag, typ, intervall, final_start, final_end, kuend, int(edit_id)))
            else:
                conn.execute('''INSERT INTO eintraege (art, konto_id, kategorie, zweck, betrag, typ, intervall, start_datum, end_datum, kuendigung_tage) 
                                VALUES (?,?,?,?,?,?,?,?,?,?)''', 
                             (art_val, k_id, kategorie, zweck, betrag, typ, intervall, final_start, final_end, kuend))
            conn.commit()
            st.rerun()

# --- FORECAST LOGIK ---
def get_forecast_detailed(months):
    df = pd.read_sql_query("SELECT e.*, k.name as konto_name FROM eintraege e JOIN konten k ON e.konto_id = k.id", conn)
    chart_data, table_data = [], []
    mapping = {"Monatlich": 1, "Quartalsweise": 1/3, "Jährlich": 1/12}
    current_date = datetime.now().replace(day=1)
    m_ein, m_aus_ist, m_aus_ant, kat_dist = 0, 0, 0, {}

    for i in range(months):
        target = (current_date + timedelta(days=i*31)).replace(day=1)
        m_label = target.strftime("%b %Y")
        ein_ist, aus_ist = 0, 0
        if not df.empty:
            for _, row in df.iterrows():
                s = datetime.fromisoformat(row['start_datum']).replace(day=1)
                e = datetime.fromisoformat(row['end_datum']).replace(day=1) if row['end_datum'] else None
                if s <= target and (not e or target <= e):
                    is_due = (row['intervall'] == "Monatlich") or \
                             (row['intervall'] == "Quartalsweise" and (target.month - s.month) % 3 == 0) or \
                             (row['intervall'] == "Jährlich" and target.month == s.month)
                    val_actual = row['betrag'] if is_due else 0
                    val_anteilig = row['betrag'] * mapping.get(row['intervall'], 1)
                    
                    status_info = ""
                    if row['art'] == "Finanzierung" and e:
                        r_months = (e.year - target.year) * 12 + e.month - target.month
                        r_sum = max(r_months * row['betrag'], 0)
                        status_info = f"({r_months}m | {format_euro(r_sum)})"

                    if row['typ'] == "Einnahme":
                        ein_ist += val_actual
                        if i == 0: m_ein += val_actual
                    else:
                        aus_ist += val_actual
                        if i == 0:
                            m_aus_ist += val_actual
                            m_aus_ant += val_anteilig
                            kat_dist[row['kategorie']] = kat_dist.get(row['kategorie'], 0) + val_anteilig
                    
                    table_data.append({
                        "Monat": m_label, " ": get_emoji(row['art'], row['typ']), "Konto": row['konto_name'],
                        "Zweck": f"{row['zweck']} {status_info}", "Kategorie": row['kategorie'], 
                        "Betrag (fällig)": val_actual, "Anteilig p.M.": val_anteilig, 
                        "Turnus": row['intervall'], "Typ_Internal": row['typ'], "Ist_Fällig": is_due
                    })
        chart_data.append({"Monat": m_label, "Einnahmen": ein_ist, "Ausgaben": aus_ist, "Saldo": ein_ist - aus_ist})
    return pd.DataFrame(chart_data), pd.DataFrame(table_data), m_ein, m_aus_ist, m_aus_ant, kat_dist

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏦 Finanz-Master 1.3.7")
    page = st.radio("Navigation", ["📊 Dashboard", "📝 Einträge", "⚙️ Einstellungen"])
    if st.button("➕ Neuer Eintrag", use_container_width=True): eintrag_dialog()

# --- DASHBOARD ---
if page == "📊 Dashboard":
    st.title("Dashboard")
    zeitraum = st.segmented_control("Vorschau Zeitraum", [3, 6, 12], default=3)
    f_df, t_df, m_ein, m_aus_ist, m_aus_ant, kat_dist = get_forecast_detailed(zeitraum)
    
    if not f_df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("1. Eingang", format_euro(m_ein))
        c2.metric("2. Ausgaben (Ist)", f"-{format_euro(m_aus_ist)}")
        c3.metric("3. Ausgaben (anteilig)", f"-{format_euro(m_aus_ant)}")
        c4.metric("4. Verfügbar (Ist)", format_euro(m_ein - m_aus_ist))
        
        st.divider()
        with st.expander("Statistiken (Kategorien & Trends)"):
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                if kat_dist:
                    fig_pie = px.pie(names=list(kat_dist.keys()), values=list(kat_dist.values()), hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_pie, use_container_width=True)
            with col_chart2:
                fig_bar = px.bar(f_df, x="Monat", y=["Einnahmen", "Ausgaben"], barmode="group", color_discrete_map={"Einnahmen": "#2ecc71", "Ausgaben": "#e74c3c"})
                st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()
        st.subheader("Detaillierte Vorschau")
        if not t_df.empty:
            for monat in t_df['Monat'].unique():
                st.markdown(f"#### 📅 {monat}")
                m_subset = t_df[t_df['Monat'] == monat].sort_values(by="Ist_Fällig", ascending=False).copy()
                
                def apply_style(row):
                    bg = 'rgba(46, 204, 113, 0.15)' if row['Typ_Internal'] == 'Einnahme' else 'rgba(231, 76, 60, 0.15)'
                    if row['Ist_Fällig']:
                        return [f'background-color: {bg}; font-weight: bold;'] * len(row)
                    return [f'background-color: {bg}; color: #888; font-style: italic; border-top: 1px dashed rgba(0,0,0,0.1);'] * len(row)

                st.dataframe(m_subset.style.apply(apply_style, axis=1).format({"Betrag (fällig)": format_euro, "Anteilig p.M.": format_euro}),
                             use_container_width=True, hide_index=True, column_order=(" ", "Konto", "Zweck", "Kategorie", "Betrag (fällig)", "Anteilig p.M.", "Turnus"))

        df_fin = pd.read_sql_query("SELECT * FROM eintraege WHERE art='Finanzierung'", conn)
        if not df_fin.empty:
            st.divider()
            st.subheader("📉 Finanzierungs-Status")
            for _, row in df_fin.iterrows():
                start = datetime.fromisoformat(row['start_datum']).date()
                end = datetime.fromisoformat(row['end_datum']).date() if row['end_datum'] else None
                if end:
                    total_days = max((end - start).days, 1)
                    passed_days = (datetime.now().date() - start).days
                    progress = min(max(passed_days / total_days, 0.0), 1.0)
                    rest_months = max((end.year - datetime.now().year) * 12 + end.month - datetime.now().month, 0)
                    cf1, cf2 = st.columns([3, 1])
                    with cf1:
                        st.write(f"**{row['zweck']}**")
                        st.progress(progress)
                    with cf2:
                        st.write(f"**{format_euro(rest_months * row['betrag'])}**")
                        st.caption(f"{rest_months} Mo. übrig")

# --- EINTRÄGE ---
elif page == "📝 Einträge":
    st.header("Alle Einträge verwalten")
    df_entries = pd.read_sql_query("SELECT e.*, k.name as konto_name FROM eintraege e JOIN konten k ON e.konto_id = k.id", conn)
    if not df_entries.empty:
        for gruppe in ["Buchung", "Abo", "Finanzierung"]:
            subset = df_entries[df_entries['art'] == gruppe].copy()
            if not subset.empty:
                st.subheader(f"{gruppe}en")
                cols = ["typ", "konto_name", "kategorie", "zweck", "betrag", "intervall", "start_datum", "end_datum"]
                res = st.dataframe(subset.style.format({"betrag": format_euro}), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row", column_order=cols)
                if res.selection.rows:
                    row_data = subset.iloc[res.selection.rows[0]]
                    with st.expander(f"⚙️ Optionen für: {row_data['zweck']}", expanded=True):
                        c1, c2, _ = st.columns([1, 1, 4])
                        if c1.button("Bearbeiten", key=f"ed_{row_data['id']}"): eintrag_dialog(row_data['id'])
                        if c2.button("Löschen", key=f"dl_{row_data['id']}"):
                            conn.execute(f"DELETE FROM eintraege WHERE id={row_data['id']}"); conn.commit(); st.rerun()
                st.divider()

# --- EINSTELLUNGEN ---
elif page == "⚙️ Einstellungen":
    st.header("Stammdaten verwalten")
    
    col_k, col_cat = st.columns(2)
    
    with col_k:
        st.subheader("Konten")
        konten_data = pd.read_sql_query("SELECT * FROM konten", conn)
        sel_k = st.dataframe(konten_data, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if sel_k.selection.rows:
            k_row = konten_data.iloc[sel_k.selection.rows[0]]
            with st.container(border=True):
                st.write(f"**Konto bearbeiten:** {k_row['name']}")
                new_k_name = st.text_input("Name", value=k_row['name'], key="edit_k_n")
                new_k_iban = st.text_input("IBAN", value=k_row['iban'], key="edit_k_i")
                ce1, ce2 = st.columns(2)
                if ce1.button("Änderungen speichern", key="save_k"):
                    conn.execute("UPDATE konten SET name=?, iban=? WHERE id=?", (new_k_name, new_k_iban, int(k_row['id'])))
                    conn.commit(); st.rerun()
                if ce2.button("Konto löschen", key="del_k", type="secondary"):
                    conn.execute("DELETE FROM konten WHERE id=?", (int(k_row['id']),))
                    conn.commit(); st.rerun()
        
        with st.expander("➕ Neues Konto hinzufügen"):
            with st.form("new_konto"):
                n_k, i_k = st.text_input("Name"), st.text_input("IBAN")
                if st.form_submit_button("Anlegen"):
                    conn.execute("INSERT INTO konten (name, iban) VALUES (?,?)", (n_k, i_k)); conn.commit(); st.rerun()

    with col_cat:
        st.subheader("Kategorien")
        kat_data = pd.read_sql_query("SELECT * FROM kategorien", conn)
        sel_cat = st.dataframe(kat_data, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if sel_cat.selection.rows:
            cat_row = kat_data.iloc[sel_cat.selection.rows[0]]
            with st.container(border=True):
                st.write(f"**Kategorie bearbeiten:** {cat_row['name']}")
                new_cat_name = st.text_input("Name", value=cat_row['name'], key="edit_cat_n")
                ce3, ce4 = st.columns(2)
                if ce3.button("Änderungen speichern", key="save_cat"):
                    conn.execute("UPDATE kategorien SET name=? WHERE id=?", (new_cat_name, int(cat_row['id'])))
                    conn.commit(); st.rerun()
                if ce4.button("Kategorie löschen", key="del_cat", type="secondary"):
                    conn.execute("DELETE FROM kategorien WHERE id=?", (int(cat_row['id']),))
                    conn.commit(); st.rerun()

        with st.expander("➕ Neue Kategorie hinzufügen"):
            with st.form("new_cat"):
                n_c = st.text_input("Kategorie Name")
                if st.form_submit_button("Anlegen"):
                    conn.execute("INSERT INTO kategorien (name) VALUES (?)", (n_c,)); conn.commit(); st.rerun()