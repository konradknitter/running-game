#!/usr/bin/env python3
"""
update_manifest.py — Konrad Co-Trainer helper
Oblicza km tygodniowe z plików data/days/*.json
i aktualizuje data/manifest.json (chartWeeks + lastUpdated).

Uruchomienie:
    python3 scripts/update_manifest.py

Zasady:
- Liczy tylko aktywności type="run" z polem dist
- Tydzień = Pn–Nd (ISO: poniedziałek jako dzień 0)
- Aktualizuje tylko te wpisy chartWeeks, które mają pole "weekStart"
- Ustawia "partial": true dla tygodnia bieżącego (jeszcze trwającego)
- Ustawia lastUpdated na dzisiejszą datę
"""

import json
import os
from datetime import datetime, timedelta

# ── Ścieżki ──────────────────────────────────────────────────────────────────
REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAYS_DIR    = os.path.join(REPO_ROOT, 'data', 'days')
MANIFEST    = os.path.join(REPO_ROOT, 'data', 'manifest.json')

DAYS_PL = ['Pn', 'Wt', 'Śr', 'Czw', 'Pt', 'So', 'Nd']
MONTHS_PL = {
    1: 'sty', 2: 'lut', 3: 'mar', 4: 'kwi', 5: 'maj', 6: 'cze',
    7: 'lip', 8: 'sie', 9: 'wrz', 10: 'paź', 11: 'lis', 12: 'gru'
}

def pl_date(d: datetime) -> str:
    return f"{DAYS_PL[d.weekday()]} {d.day:02d}.{d.month:02d}.{d.year}"

def week_start(date_str: str) -> str:
    """Zwraca datę poniedziałku tygodnia zawierającego date_str."""
    d = datetime.strptime(date_str, '%Y-%m-%d')
    monday = d - timedelta(days=d.weekday())
    return monday.strftime('%Y-%m-%d')

def load_day_files() -> dict:
    """Wczytuje wszystkie pliki dni. Zwraca {date_str: data}."""
    days = {}
    if not os.path.isdir(DAYS_DIR):
        return days
    for fname in sorted(os.listdir(DAYS_DIR)):
        if fname.endswith('.json') and len(fname) == 15:  # YYYY-MM-DD.json
            date_str = fname[:-5]
            path = os.path.join(DAYS_DIR, fname)
            try:
                with open(path, encoding='utf-8') as f:
                    days[date_str] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"  WARN: nie można wczytać {fname}: {e}")
    return days

def compute_weekly_km(days: dict, today: datetime) -> dict:
    """
    Oblicza km biegowe per tydzień — tylko dla dni <= dziś (nie liczy planów).
    Zwraca {week_start_str: total_km}.
    """
    today_str = today.strftime('%Y-%m-%d')
    weekly = {}
    for date_str, data in days.items():
        if date_str > today_str:
            continue  # przyszłe dni / plany — pomijamy
        if data.get('type') == 'run' and data.get('dist'):
            ws = week_start(date_str)
            weekly[ws] = weekly.get(ws, 0.0) + float(data['dist'])
    return weekly

def is_week_complete(ws_str: str, today: datetime) -> bool:
    """Sprawdza czy tydzień (Pn–Nd) jest już zakończony."""
    ws = datetime.strptime(ws_str, '%Y-%m-%d')
    week_end = ws + timedelta(days=6)  # niedziela
    return week_end.date() < today.date()

def main():
    today = datetime.now()
    print(f"update_manifest.py — {pl_date(today)}")
    print(f"Repo: {REPO_ROOT}")

    # Wczytaj pliki dni
    days = load_day_files()
    print(f"Wczytano {len(days)} plików dni.")

    # Oblicz km per tydzień (tylko dni <= dziś)
    weekly_km = compute_weekly_km(days, today)
    if weekly_km:
        for ws, km in sorted(weekly_km.items()):
            print(f"  Tydzień {ws}: {km:.1f} km")
    else:
        print("  Brak danych biegowych w plikach dni.")

    # Wczytaj manifest
    with open(MANIFEST, encoding='utf-8') as f:
        manifest = json.load(f)

    # Aktualizuj chartWeeks (tylko te z weekStart)
    changed = False
    for entry in manifest.get('chartWeeks', []):
        ws = entry.get('weekStart')
        if not ws:
            continue  # historyczne wpisy bez weekStart — pomijamy

        if ws in weekly_km:
            new_km  = round(weekly_km[ws], 1)
            partial = not is_week_complete(ws, today)

            old_km  = entry.get('km')
            old_par = entry.get('partial', False)

            entry['km'] = new_km

            if partial:
                entry['partial'] = True
            elif 'partial' in entry:
                del entry['partial']  # usuń flagę po zakończeniu tygodnia

            if old_km != new_km or old_par != partial:
                print(f"  chartWeeks {ws}: {old_km} → {new_km} km"
                      + (" (partial)" if partial else ""))
                changed = True
        else:
            print(f"  WARN: brak danych dla tygodnia {ws} w plikach dni.")

    # Aktualizuj lastUpdated
    new_date = pl_date(today)
    if manifest.get('lastUpdated') != new_date:
        print(f"  lastUpdated: {manifest.get('lastUpdated')} → {new_date}")
        manifest['lastUpdated'] = new_date
        changed = True

    # Zapisz
    if changed:
        with open(MANIFEST, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print("manifest.json zaktualizowany.")
    else:
        print("Brak zmian w manifest.json.")

if __name__ == '__main__':
    main()
