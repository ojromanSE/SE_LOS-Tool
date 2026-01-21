import subprocess
import re
import os

def parse_taxes(pdf_path):
    text = subprocess.check_output(
        ["pdftotext", pdf_path, "-"],
        errors="ignore"
    ).decode()

    lines = text.split("\n")

    records = []
    current_well = None

    m = re.search(r"(20\d{2})[-\.](\d{2})", pdf_path)
    month = f"{m.group(1)}-{m.group(2)}" if m else None

    for i, l in enumerate(lines):
        if "State:" in l:
            current_well = l.split(",")[0].strip()

        if "TAX" in l.upper():
            for x in lines[i:i+5]:
                n = re.search(r"\(([\d,]+\.\d{2})\)", x)
                if n:
                    records.append({
                        "well": current_well,
                        "month": month,
                        "tax": float(n.group(1).replace(",", ""))
                    })

    return records
