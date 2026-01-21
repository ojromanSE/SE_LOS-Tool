import re
import os
from datetime import datetime
from utils.pdf_utils import extract_text


# =========================================================
# Helper functions
# =========================================================

def extract_month_from_filename(filename):
    """
    Extract YYYY-MM from common EnergyLink filename patterns
    """
    m = re.search(r"(20\d{2})[-\.](\d{2})", filename)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    m = re.search(r"(\d{2})\.(20\d{2})", filename)
    if m:
        return f"{m.group(2)}-{m.group(1)}"

    return None


def extract_numbers(lines):
    """
    Extract all numeric values from a block of lines
    """
    nums = []
    for l in lines:
        for n in re.findall(r"\(?-?\d[\d,]*\.\d{2}\)?", l):
            nums.append(
                float(
                    n.replace(",", "")
                     .replace("(", "")
                     .replace(")", "")
                )
            )
    return nums


# =========================================================
# JIB → LOE
# =========================================================

def parse_jib(pdf_path):
    """
    Parse EnergyLink JIB PDF and return LOE records
    """
    text = extract_text(pdf_path)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # -------------------------
    # Extract Op Accounting Month (ROBUST)
    # -------------------------
    month = None

    for i, l in enumerate(lines):
        if "Op Accounting Month" in l:
            # search forward up to 6 lines
            for j in range(i, min(i + 6, len(lines))):
                m = re.search(r"([A-Za-z]+)\s+(\d{4})", lines[j])
                if m:
                    month = datetime.strptime(
                        f"{m.group(1)} {m.group(2)}",
                        "%B %Y"
                    ).strftime("%Y-%m")
                    break
            break

    if month is None:
        raise ValueError(
            f"Could not determine Op Accounting Month in JIB: {os.path.basename(pdf_path)}"
        )

    # -------------------------
    # Extract LOE lines
    # -------------------------
    records = []
    current_well = None

    for l in lines:

        # crude but effective well header detection
        if (
            "STEUBEN" in l
            or " WA " in f" {l} "
            or " LS " in f" {l} "
        ):
            current_well = l.strip()

        # accepted amount at end of line
        amt = re.search(r"\(?([0-9,]+\.\d{2})\)?$", l)

        if current_well and amt:
            records.append({
                "well": current_well,
                "month": month,
                "loe": float(amt.group(1).replace(",", ""))
            })

    return records


# =========================================================
# Revenue → Volumes & Revenue
# =========================================================

def parse_revenue(pdf_path):
    """
    Parse EnergyLink Revenue PDF and return volumes + revenue
    """
    text = extract_text(pdf_path)
    lines = text.split("\n")

    month = extract_month_from_filename(os.path.basename(pdf_path))

    records = []
    current_well = None

    for i, l in enumerate(lines):

        # detect well/property header
        if "State:" in l and "," in l:
            current_well = l.split(",")[0].strip()

        # detect totals by product
        for product in ["OIL", "GAS", "NGL"]:
            if l.strip() == f"Total {product}":
                nums = extract_numbers(lines[i + 1:i + 10])
                if len(nums) >= 2:
                    records.append({
                        "well": current_well,
                        "month": month,
                        f"{product.lower()}_volume": min(nums),
                        f"{product.lower()}_revenue": max(nums)
                    })

    return records


# =========================================================
# Revenue → Taxes
# =========================================================

def parse_taxes(pdf_path):
    """
    Parse EnergyLink Revenue PDF for severance / regulatory taxes
    """
    text = extract_text(pdf_path)
    lines = text.split("\n")

    month = extract_month_from_filename(os.path.basename(pdf_path))

    records = []
    current_well = None

    for i, l in enumerate(lines):

        if "State:" in l:
            current_well = l.split(",")[0].strip()

        if "TAX" in l.upper():
            # look ahead for negative (parenthesized) values
            for x in lines[i:i + 5]:
                m = re.search(r"\(([\d,]+\.\d{2})\)", x)
                if m:
                    records.append({
                        "well": current_well,
                        "month": month,
                        "tax": float(m.group(1).replace(",", ""))
                    })

    return records
