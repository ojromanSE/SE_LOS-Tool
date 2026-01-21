import re
import os
from datetime import datetime
from utils.pdf_utils import extract_text

# ---------------------------
# Helpers
# ---------------------------

def extract_month_from_filename(filename):
    m = re.search(r"(20\d{2})[-\.](\d{2})", filename)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.search(r"(\d{2})\.(20\d{2})", filename)
    if m:
        return f"{m.group(2)}-{m.group(1)}"
    return None

def extract_numbers(lines):
    nums = []
    for l in lines:
        for n in re.findall(r"\(?-?\d[\d,]*\.\d{2}\)?", l):
            nums.append(float(n.replace(",", "").replace("(", "").replace(")", "")))
    return nums

# ---------------------------
# JIB → LOE
# ---------------------------

def parse_jib(pdf_path):
    text = extract_text(pdf_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    month = None
    for i, l in enumerate(lines):
        if "Op Accounting Month" in l:
            m = re.search(r"([A-Za-z]+)\s+(\d{4})", lines[i+1])
            month = datetime.strptime(
                f"{m.group(1)} {m.group(2)}", "%B %Y"
            ).strftime("%Y-%m")
            break

    records = []
    current_well = None

    for l in lines:
        if "STEUBEN" in l or " WA " in l or " LS " in l:
            current_well = l.strip()

        amt = re.search(r"\(?([0-9,]+\.\d{2})\)?$", l)
        if current_well and amt:
            records.append({
                "well": current_well,
                "month": month,
                "loe": float(amt.group(1).replace(",", ""))
            })

    return records

# ---------------------------
# Revenue → volumes & revenue
# ---------------------------

def parse_revenue(pdf_path):
    text = extract_text(pdf_path)
    lines = text.split("\n")
    month = extract_month_from_filename(os.path.basename(pdf_path))

    records = []
    current_well = None

    for i, l in enumerate(lines):
        if "State:" in l and "," in l:
            current_well = l.split(",")[0].strip()

        for product in ["OIL", "GAS", "NGL"]:
            if l.strip() == f"Total {product}":
                nums = extract_numbers(lines[i+1:i+10])
                if len(nums) >= 2:
                    records.append({
                        "well": current_well,
                        "month": month,
                        f"{product.lower()}_volume": min(nums),
                        f"{product.lower()}_revenue": max(nums)
                    })

    return records

# ---------------------------
# Revenue → Taxes
# ---------------------------

def parse_taxes(pdf_path):
    text = extract_text(pdf_path)
    lines = text.split("\n")
    month = extract_month_from_filename(os.path.basename(pdf_path))

    records = []
    current_well = None

    for i, l in enumerate(lines):
        if "State:" in l:
            current_well = l.split(",")[0].strip()

        if "TAX" in l.upper():
            for x in lines[i:i+5]:
                m = re.search(r"\(([\d,]+\.\d{2})\)", x)
                if m:
                    records.append({
                        "well": current_well,
                        "month": month,
                        "tax": float(m.group(1).replace(",", ""))
                    })

    return records
