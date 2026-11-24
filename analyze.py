"""Educational SLA analysis using reproducible, synthetic tickets."""
import csv
import random
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def generate_tickets(seed=27, count=600):
    rng = random.Random(seed)
    result = []
    for ticket_id in range(1, count + 1):
        created = datetime(2024, 1, 1) + timedelta(hours=rng.randrange(24 * 90))
        priority = rng.choice(("high", "normal"))
        target = 60 if priority == "high" else 240
        delay = rng.randrange(10, 181) if priority == "high" else rng.randrange(20, 481)
        responded = created + timedelta(minutes=delay) if rng.random() >= 0.1 else None
        result.append((ticket_id, created.isoformat(sep=" "), priority, target,
                       responded.isoformat(sep=" ") if responded else None))
    return result


def summarize(rows, cutoff="2024-04-02 00:00:00"):
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE tickets (id INTEGER PRIMARY KEY, created TEXT NOT NULL, priority TEXT NOT NULL, target_minutes INTEGER NOT NULL, responded TEXT)")
        db.executemany("INSERT INTO tickets VALUES (?,?,?,?,?)", rows)
        query = (ROOT / "analysis.sql").read_text(encoding="utf-8")
        cursor = db.execute(query, {"cutoff": cutoff})
        return [x[0] for x in cursor.description], cursor.fetchall()


def main():
    rows = generate_tickets()
    columns, summary = summarize(rows)
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    with (out / "sla_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(summary)
    for row in summary:
        print(row)


if __name__ == "__main__":
    main()
