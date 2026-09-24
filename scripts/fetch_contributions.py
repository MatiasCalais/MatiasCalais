"""
fetch_contributions.py
Busca o calendário de contribuições público do GitHub (HTML, sem token,
sem GraphQL) em:
    https://github.com/users/<username>/contributions
Faz o parse dos dias com BeautifulSoup e salva data/contributions.json
com os dias brutos + estatísticas derivadas (streak atual, streak mais
longo, melhor dia, totais mensais).

Uso:
    python scripts/fetch_contributions.py
"""
import json
import datetime
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

USERNAME = "MatiasCalais"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_JSON = "data/contributions.json"


def fetch_days() -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # O GitHub marca cada dia como <td> com data-date e um nível de
    # contribuição (data-level ou classe contrib-level).
    cells = soup.select("td[data-date]") or soup.select("rect[data-date]")
    for cell in cells:
        date_str = cell.get("data-date")
        level_str = cell.get("data-level")
        if level_str is None:
            level_str = cell.get("data-count") or "0"
        try:
            level = int(level_str)
        except ValueError:
            level = 0
        # normaliza contagem quando o atributo é "count" em vez de "level"
        count_attr = cell.get("data-count")
        count = int(count_attr) if count_attr and count_attr.isdigit() else level
        days.append({"date": date_str, "level": min(level, 5), "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # streak atual e mais longo
    longest = current = 0
    running = 0
    today = datetime.date.today().isoformat()
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # streak atual = contando a partir do fim, enquanto count > 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = defaultdict(int)
    for d in days:
        month_key = d["date"][:7] if d["date"] else "unknown"
        monthly[month_key] += d["count"]

    return {
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
    }


def main():
    days = fetch_days()
    stats = compute_stats(days)
    payload = {"username": USERNAME, "days": days, "stats": stats}

    import os
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[fetch_contributions] {len(days)} dias salvos em {OUTPUT_JSON}")
    print(f"[fetch_contributions] total: {stats['total_last_year']}, "
          f"streak atual: {stats['current_streak']}, "
          f"streak mais longo: {stats['longest_streak']}")


if __name__ == "__main__":
    main()
