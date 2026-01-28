import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import hashlib

# --- KONFIGURATION ---
APP_PASSWORD = "DeinSicheresPasswort123" # Ändere dies vor dem Deployment!

def check_password():
    """Gibt True zurück, wenn der Benutzer das korrekte Passwort eingegeben hat."""
    def password_entered():
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == hashlib.sha256(APP_PASSWORD.encode()).hexdigest():
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Passwort nicht im State lassen
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Erstmalige Anzeige der Login-Maske
        st.title("🔐 Finanz-Master Login")
        st.text_input("Bitte Passwort eingeben", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Passwort war falsch
        st.title("🔐 Finanz-Master Login")
        st.text_input("Bitte Passwort eingeben", type="password", on_change=password_entered, key="password")
        st.error("😕 Passwort falsch.")
        return False
    else:
        # Passwort korrekt
        return True

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
    conn.commit()
    return conn

# --- HAUPTPROGRAMM ---
st.set_page_config(page_title="Finanz-Master v1.3.8", layout="wide")

if check_password():
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
                    try: e_date_val = datetime.fromisoformat(existing['end_datum']).date()
                    except: e_date_val = None
                end_d = st.date_input("Enddatum (Optional)", value=e_date_val)

            kuend = None
            if art_val == "Abo":
                kuend = st.number_input("Kündigungsfrist (Tage)", value=int(existing['kuendigung_tage']) if edit_id and existing['kuendigung_tage'] else 30)

            if st.form_submit_button("Speichern"):
                k_id = int(konten_df[konten_df['name'] == k_auswahl]['id'].iloc[0])
                final_start, final_end = start_d.isoformat(), (end_d.isoformat() if end_d else None)
                if edit_id:
                    conn.execute('''UPDATE eintraege SET konto_id=?, kategorie=?, zweck=?, betrag=?, typ=?, intervall=?, 
                                    start_datum=?, end_datum=?, kuendigung_tage=? WHERE id=?''',
                                 (k_id, kategorie, zweck, betrag, typ, intervall, final_start, final_end, kuend, int(edit_id)))
                else:
                    conn.execute('''INSERT INTO eintraege (art, konto_id, kategorie, zweck, betrag, typ, intervall, start_datum, end_datum, kuendigung_tage) 
                                    VALUES (?,?,?,?,?,?,?,?,?,?)''', 
                                 (art_val, k_id, kategorie, zweck, betrag, typ, intervall, final_start, final_end, kuend))
                conn.commit(); st.rerun()

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
                        status_info = f"({((e.year - target.year) * 12 + e.month - target.month)}m | {format_euro(((e.year - target.year) * 12 + e.month - target.month) * row['betrag'])})" if row['art'] == "Finanzierung" and e else ""
                        if row['typ'] == "Einnahme":
                            ein_ist += val_actual
                            if i == 0: m_ein += val_actual
                        else:
                            aus_ist += val_actual
                            if i == 0:
                                m_aus_ist += val_actual; m_aus_ant += val_anteilig
                                kat_dist[row['kategorie']] = kat_dist.get(row['kategorie'], 0) + val_anteilig
                        table_data.append({"Monat": m_label, " ": get_emoji(row['art'], row['typ']), "Konto": row['konto_name'], "Zweck": f"{row['zweck']} {status_info}", "Kategorie": row['kategorie'], "Betrag (fällig)": val_actual, "Anteilig p.M.": val_anteilig, "Turnus": row['intervall'], "Typ_Internal": row['typ'], "Ist_Fällig": is_due})
            chart_data.append({"Monat": m_label, "Einnahmen": ein_ist, "Ausgaben": aus_ist, "Saldo": ein_ist - aus_ist})
        return pd.DataFrame(chart_data), pd.DataFrame(table_data), m_ein, m_aus_ist, m_aus_ant, kat_dist

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("🏦 Finanz-Master 1.3.8")
        page = st.radio("Navigation", ["📊 Dashboard", "📝 Einträge", "⚙️ Einstellungen"])
        if st.button("➕ Neuer Eintrag", use_container_width=True): eintrag_dialog()
        st.divider()
        if st.button("🚪 Abmelden"):
            del st.session_state["password_correct"]
            st.rerun()

    # --- PAGES ---
    if page == "📊 Dashboard":
        st.title("Dashboard")
        zeitraum = st.segmented_control("Vorschau Zeitraum", [3, 6, 12], default=3)
        f_df, t_df, m_ein, m_aus_ist, m_aus_ant, kat_dist = get_forecast_detailed(zeitraum)
        if not f_df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("1. Eingang", format_euro(m_ein)); c2.metric("2. Ausgaben (Ist)", f"-{format_euro(m_aus_ist)}"); c3.metric("3. Ausgaben (anteilig)", f"-{format_euro(m_aus_ant)}"); c4.metric("4. Verfügbar (Ist)", format_euro(m_ein - m_aus_ist))
            st.divider()
            with st.expander("Statistiken"):
                co1, co2 = st.columns(2)
                with co1: st.plotly_chart(px.pie(names=list(kat_dist.keys()), values=list(kat_dist.values()), hole=0.4, title="Kategorien"), use_container_width=True)
                with co2: st.plotly_chart(px.bar(f_df, x="Monat", y=["Einnahmen", "Ausgaben"], barmode="group", title="Trend"), use_container_width=True)
            st.divider()
            for monat in t_df['Monat'].unique():
                st.markdown(f"#### 📅 {monat}")
                m_sub = t_df[t_df['Monat'] == monat].sort_values(by="Ist_Fällig", ascending=False)
                def apply_style(row):
                    bg = 'rgba(46, 204, 113, 0.15)' if row['Typ_Internal'] == 'Einnahme' else 'rgba(231, 76, 60, 0.15)'
                    return [f'background-color: {bg}; {"font-weight: bold" if row["Ist_Fällig"] else "color: #888; font-style: italic"}'] * len(row)
                st.dataframe(m_sub.style.apply(apply_style, axis=1).format({"Betrag (fällig)": format_euro, "Anteilig p.M.": format_euro}), use_container_width=True, hide_index=True, column_order=(" ", "Konto", "Zweck", "Kategorie", "Betrag (fällig)", "Anteilig p.M.", "Turnus"))
            # Finanzierungs-Tracker
            df_fin = pd.read_sql_query("SELECT * FROM eintraege WHERE art='Finanzierung'", conn)
            if not df_fin.empty:
                st.divider(); st.subheader("📉 Finanzierungs-Status")
                for _, row in df_fin.iterrows():
                    start, end = datetime.fromisoformat(row['start_datum']).date(), (datetime.fromisoformat(row['end_datum']).date() if row['end_datum'] else None)
                    if end:
                        prog = min(max((datetime.now().date() - start).days / max((end - start).days, 1), 0.0), 1.0)
                        rm = max((end.year - datetime.now().year) * 12 + end.month - datetime.now().month, 0)
                        cf1, cf2 = st.columns([3, 1])
                        cf1.write(f"**{row['zweck']}**"); cf1.progress(prog)
                        cf2.write(f"**{format_euro(rm * row['betrag'])}**"); cf2.caption(f"{rm} Mo. übrig")

    elif page == "📝 Einträge":
        st.header("Alle Einträge verwalten")
        df_entries = pd.read_sql_query("SELECT e.*, k.name as konto_name FROM eintraege e JOIN konten k ON e.konto_id = k.id", conn)
        if not df_entries.empty:
            for gruppe in ["Buchung", "Abo", "Finanzierung"]:
                subset = df_entries[df_entries['art'] == gruppe].copy()
                if not subset.empty:
                    st.subheader(f"{gruppe}en")
                    res = st.dataframe(subset.style.format({"betrag": format_euro}), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row", column_order=["typ", "konto_name", "kategorie", "zweck", "betrag", "intervall", "start_datum", "end_datum"])
                    if res.selection.rows:
                        row_data = subset.iloc[res.selection.rows[0]]
                        with st.expander(f"⚙️ Optionen für: {row_data['zweck']}", expanded=True):
                            c1, c2, _ = st.columns([1, 1, 4])
                            if c1.button("Bearbeiten", key=f"ed_{row_data['id']}"): eintrag_dialog(row_data['id'])
                            if c2.button("Löschen", key=f"dl_{row_data['id']}"): conn.execute(f"DELETE FROM eintraege WHERE id={row_data['id']}"); conn.commit(); st.rerun()
                    st.divider()

    elif page == "⚙️ Einstellungen":
        st.header("Stammdaten verwalten")
        col_k, col_cat = st.columns(2)
        with col_k:
            st.subheader("Konten")
            kd = pd.read_sql_query("SELECT * FROM konten", conn)
            sk = st.dataframe(kd, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            if sk.selection.rows:
                kr = kd.iloc[sk.selection.rows[0]]
                with st.container(border=True):
                    nk_n = st.text_input("Name", value=kr['name'], key="ekn"); nk_i = st.text_input("IBAN", value=kr['iban'], key="eki")
                    if st.button("Speichern", key="sk"): conn.execute("UPDATE konten SET name=?, iban=? WHERE id=?", (nk_n, nk_i, int(kr['id']))); conn.commit(); st.rerun()
                    if st.button("Löschen", key="dk"): conn.execute("DELETE FROM konten WHERE id=?", (int(kr['id']),)); conn.commit(); st.rerun()
            with st.expander("➕ Neu"):
                with st.form("nk"):
                    n, i = st.text_input("Name"), st.text_input("IBAN")
                    if st.form_submit_button("OK"): conn.execute("INSERT INTO konten (name, iban) VALUES (?,?)", (n, i)); conn.commit(); st.rerun()
        with col_cat:
            st.subheader("Kategorien")
            ctd = pd.read_sql_query("SELECT * FROM kategorien", conn)
            scat = st.dataframe(ctd, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            if scat.selection.rows:
                cr = ctd.iloc[scat.selection.rows[0]]
                with st.container(border=True):
                    nc_n = st.text_input("Name", value=cr['name'], key="ecn")
                    if st.button("Speichern", key="sc"): conn.execute("UPDATE kategorien SET name=? WHERE id=?", (nc_n, int(cr['id']))); conn.commit(); st.rerun()
                    if st.button("Löschen", key="dc"): conn.execute("DELETE FROM kategorien WHERE id=?", (int(cr['id']),)); conn.commit(); st.rerun()
            with st.expander("➕ Neu"):
                with st.form("nc"):
                    n = st.text_input("Name")
                    if st.form_submit_button("OK"): conn.execute("INSERT INTO kategorien (name) VALUES (?)", (n,)); conn.commit(); st.rerun()