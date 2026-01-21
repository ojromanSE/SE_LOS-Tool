import subprocess
import shutil
import pdfplumber

def extract_text(pdf_path):
    """
    Try pdftotext first (fast, accurate).
    Fall back to pdfplumber if not available.
    """

    if shutil.which("pdftotext"):
        try:
            return subprocess.check_output(
                ["pdftotext", pdf_path, "-"],
                errors="ignore"
            ).decode()
        except Exception:
            pass

    # Fallback: pdfplumber
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"

    return text
