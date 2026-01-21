import subprocess
import re
from datetime import datetime

def parse_jib(pdf_path):
    text = subprocess.check_output(
        ["pdftotext", pdf_path, "-"],
        errors="ignore"
    ).decode()

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    month = None
    for i, l in enumerate(lines):
        if "Op Accounting Month" in l:
            m = re.search(r"([A-Za-z]+)\s+(\d{4})", lines[i+1])
            month = datetime.strptime(
                f"{m.group(1)} {m.group(2)}",
                "%B %Y"
            ).strftime("%Y-%m")
            break

    records = []
    current_well = None

    for l in lines:
        if "STEUBEN" in l or "WA" in l or "LS" in l:
            current_well = l.strip()

        amt = re.search(r"\(?([0-9,]+\.\d{2})\)?$", l)
        if current_well and amt:
            value = float(amt.group(1).replace(",", ""))
            records.append({
                "well": current_well,
                "month": month,
                "loe": value
            })

    return records
