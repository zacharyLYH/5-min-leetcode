import csv
import pathlib
import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def load_subscribers(csv_path: str | pathlib.Path) -> list[str]:
    p = pathlib.Path(csv_path)
    if not p.exists():
        return []
    emails: list[str] = []
    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            # empty or no header — treat whole file as list
            f.seek(0)
            for row in csv.reader(f):
                if row:
                    emails.append(row[0].strip())
        else:
            # support header `email` or first column fallback
            field = "email" if "email" in reader.fieldnames else reader.fieldnames[0]
            for row in reader:
                raw = (row.get(field) or "").strip()
                if raw:
                    emails.append(raw)

    # normalize: lower, dedupe, validate
    seen: set[str] = set()
    out: list[str] = []
    for e in emails:
        e = e.strip().lower()
        if not e or e.startswith("#"):
            continue
        if e not in seen and _EMAIL_RE.match(e):
            seen.add(e)
            out.append(e)
    return out
