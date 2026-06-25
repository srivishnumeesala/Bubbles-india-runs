# Technical Breakdown:
# - Uses PyMuPDF (fitz) over pdfplumber because:
#   (a) 3–5× faster on large PDFs.
#   (b) Preserves multi-column layout order via sort=True in get_text().
#   (c) Handles password-protected files with explicit error.
# - Extracts text page-by-page and joins with double newline to preserve section breaks.
# - Logs failures to data/logs/failed_files.log with a timestamp.

import datetime
from pathlib import Path
from config.settings import LOG_FILE

def extract_pdf(path: Path) -> str:
    import fitz  # PyMuPDF
    """Extract raw text from a PDF file page by page, preserving layout.

    Args:
        path (Path): Absolute or relative path to the PDF file.

    Returns:
        str: Extracted raw text, where pages are separated by double newlines.

    Raises:
        FileNotFoundError: If the file does not exist.
        RuntimeError: If the PDF is corrupted, password-protected, or fails to parse.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {path_obj}")

    try:
        doc = fitz.open(path_obj)
        if doc.is_encrypted:
            raise RuntimeError(f"PDF is encrypted: {path_obj}")

        pages_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # sort=True sorts layout columns top-to-bottom, left-to-right
            text = page.get_text("text", sort=True)
            pages_text.append(text)
        
        doc.close()
        return "\n\n".join(pages_text)

    except Exception as e:
        timestamp = datetime.datetime.now().isoformat()
        error_msg = f"[{timestamp}] [PDF Parser Error] {path_obj}: {str(e)}\n"
        try:
            # Ensure parent directories exist
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as log_f:
                log_f.write(error_msg)
        except Exception:
            pass  # Fail-safe if logging itself fails
        
        raise RuntimeError(f"Failed to parse PDF {path_obj}: {str(e)}") from e
