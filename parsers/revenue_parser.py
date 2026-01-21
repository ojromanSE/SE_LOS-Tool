import subprocess
import re
import os

def extract_month(filename):
    m = re.search(r"(20\d{2})[-\.](\d{2})", filename)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.search(r"(\d{2})\.(20\d{2})", filename)
    if m:
        return f"{m.group(2)}-{m.group(1)}"
    return None

def extract_numbers(block):
    nums = []
    for l in block:
        for n in re.findall(r"\(?-?\d[\d,]*\.\d{2}\)?", l):
            nums.append(
                float(n.replace(",", "").replace("(", "").replace(")", ""))
            )
    return nums

def parse_revenue(pdf_path):
    text = subprocess.check_output(
        ["pdftotext", pdf_path, "-"],
        errors="ignore"
    ).decode()

    lines = text.split("\n")
    month = extract_month(os.path.basename(pdf_path))

    records = []
    current_well = None

    for i, l in enumerate(lines):

        # detect well header
        if "State:" in l and "," in l:
            current_well = l.split(",")[0].strip()

        # detect totals by product
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
