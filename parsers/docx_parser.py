# Technical Breakdown:
# - Uses python-docx to parse Word document files.
# - Preserves structural document order by iterating through the body XML elements (w:p and w:tbl).
# - Extracts table cell content (often used for resume layouts) and paragraphs sequentially.
# - Combines table rows by tab-separating cell text and newlines.
# - Logs failures to data/logs/failed_files.log with a timestamp.

import datetime
from pathlib import Path
from config.settings import LOG_FILE

def extract_docx(path: Path) -> str:
    from docx import Document
    from docx.text.paragraph import Paragraph
    from docx.table import Table
    """Extract raw text from a DOCX file, including paragraph and table contents in order.

    Args:
        path (Path): Path to the DOCX file.

    Returns:
        str: Extracted raw text.

    Raises:
        FileNotFoundError: If the file does not exist.
        RuntimeError: If the DOCX is corrupted or fails to parse.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"DOCX file not found: {path_obj}")

    try:
        doc = Document(path_obj)
        text_parts = []

        # doc.element.body contains all paragraph (p) and table (tbl) XML elements in document order
        for element in doc.element.body:
            if element.tag.endswith('p'):
                p = Paragraph(element, doc)
                if p.text:
                    text_parts.append(p.text)
            elif element.tag.endswith('tbl'):
                t = Table(element, doc)
                table_text = []
                for row in t.rows:
                    # Collect text for each cell in the row
                    cells_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if cells_text:
                        table_text.append("\t".join(cells_text))
                if table_text:
                    text_parts.append("\n".join(table_text))

        return "\n\n".join(text_parts)

    except Exception as e:
        timestamp = datetime.datetime.now().isoformat()
        error_msg = f"[{timestamp}] [DOCX Parser Error] {path_obj}: {str(e)}\n"
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as log_f:
                log_f.write(error_msg)
        except Exception:
            pass
        
        raise RuntimeError(f"Failed to parse DOCX {path_obj}: {str(e)}") from e
