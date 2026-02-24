import sys
sys.path.append('.')
import pandas as pd
from datetime import datetime, timedelta
from db import get_emoji


def calculate_months(start_date, end_date):
    if not end_date:
        return 1
    start = datetime.fromisoformat(start_date).replace(day=1)
    end = datetime.fromisoformat(end_date).replace(day=1)
    months = (end.year - start.year) * 12 + (end.month - start.month) + 1
    return max(months, 1)


def get_forecast_detailed(conn, u_id, months):
    cur = conn.cursor()
    cur.execute(
        "SELECT e.*, k.name as konto_name FROM eintraege e JOIN konten k ON e.konto_id = k.id WHERE e.user_id=%s",
        (u_id,)
    )
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    df   = pd.DataFrame(rows, columns=cols)
    cur.close()
    chart_data, table_data = [], []
    turnus_faktor = {"Monatlich": 1, "Quartalsweise": 1/3, "Jährlich": 1/12}
    current_date = datetime.now().replace(day=1)
    m_ein, m_aus_ist, m_aus_ant, kat_dist = 0, 0, 0, {}

    for i in range(months):
        target = (current_date + timedelta(days=i * 31)).replace(day=1)
        m_label = target.strftime("%b %Y")
        ein_ist, aus_ist = 0, 0

        if not df.empty:
            for _, row in df.iterrows():
                if not row['start_datum']:
                    continue
                s = datetime.fromisoformat(row['start_datum']).replace(day=1)
                e = datetime.fromisoformat(row['end_datum']).replace(day=1) if row['end_datum'] else None

                if s <= target and (not e or target <= e):
                    is_due = (
                        row['intervall'] == "Monatlich" or
                        (row['intervall'] == "Quartalsweise" and (target.month - s.month) % 3 == 0) or
                        (row['intervall'] == "Jährlich" and target.month == s.month)
                    )

                    # Monatlichen Betrag berechnen
                    betrag_typ = row.get('betrag_typ', 'Monatliche Rate')
                    if betrag_typ == "Gesamtbetrag":
                        num_months = calculate_months(row['start_datum'], row['end_datum'])
                        monthly_amount = row['betrag'] / num_months if num_months > 0 else row['betrag']
                    else:
                        monthly_amount = row['betrag']

                    val_actual = monthly_amount if is_due else 0
                    val_anteilig = monthly_amount * turnus_faktor.get(row['intervall'], 1)

                    if row['typ'] == "Einnahme":
                        ein_ist += val_actual
                        if i == 0:
                            m_ein += val_actual
                    else:
                        aus_ist += val_actual
                        if i == 0:
                            m_aus_ist += val_actual
                            m_aus_ant += val_anteilig
                            kat = row['kategorie'] or 'Sonstige'
                            kat_dist[kat] = kat_dist.get(kat, 0) + val_anteilig

                    table_data.append({
                        "Monat": m_label,
                        " ": get_emoji(row['art'], row['typ']),
                        "Konto": row['konto_name'],
                        "Zweck": row['zweck'],
                        "Kategorie": row['kategorie'] or 'Sonstige',
                        "Betrag (fällig)": val_actual,
                        "Anteilig p.M.": val_anteilig,
                        "Turnus": row['intervall'],
                        "Typ_Internal": row['typ'],
                        "Ist_Fällig": is_due
                    })

        chart_data.append({
            "Monat": m_label,
            "Einnahmen": ein_ist,
            "Ausgaben": aus_ist,
            "Saldo": ein_ist - aus_ist
        })

    return (
        pd.DataFrame(chart_data),
        pd.DataFrame(table_data),
        m_ein, m_aus_ist, m_aus_ant, kat_dist
    )
