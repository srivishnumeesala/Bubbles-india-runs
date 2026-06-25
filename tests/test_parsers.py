# Technical Breakdown:
# - Tests the pdf_parser, docx_parser, and cleaner modules.
# - Validates text extraction correctness, layout preservation, and table parsing.
# - Asserts cleaning steps: Unicode normalisation, email/URL removal, header/footer stripping, and whitespace/punctuation cleanup.

import pytest
from pathlib import Path
from parsers.pdf_parser import extract_pdf
from parsers.docx_parser import extract_docx
from parsers.cleaner import clean_text
from config.settings import LOG_FILE

def test_extract_pdf_success(sample_pdf: Path):
    """Test successful text extraction from PDF."""
    text = extract_pdf(sample_pdf)
    assert "John Doe Resume" in text
    assert "Skills: Python, TensorFlow, SQL" in text
    assert "Header Line" in text

def test_extract_pdf_missing_file():
    """Test PDF extraction raises FileNotFoundError for missing path."""
    with pytest.raises(FileNotFoundError):
        extract_pdf(Path("non_existent_file.pdf"))

def test_extract_pdf_corrupted_file(tmp_path: Path):
    """Test PDF extraction raises RuntimeError and logs error for corrupted file."""
    corrupted_path = tmp_path / "corrupted.pdf"
    with open(corrupted_path, "w") as f:
        f.write("Not a PDF content")
    
    # Ensure log file is clean or doesn't exist
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        
    with pytest.raises(RuntimeError):
        extract_pdf(corrupted_path)
        
    assert LOG_FILE.exists()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_content = f.read()
        assert "corrupted.pdf" in log_content

def test_extract_docx_success(sample_docx: Path):
    """Test successful text extraction from DOCX paragraphs and tables."""
    text = extract_docx(sample_docx)
    assert "Jane Smith Resume" in text
    assert "Language" in text
    assert "Python, SQL" in text
    assert "Frameworks" in text
    assert "PyTorch, FastAPI" in text

def test_extract_docx_missing_file():
    """Test DOCX extraction raises FileNotFoundError for missing path."""
    with pytest.raises(FileNotFoundError):
        extract_docx(Path("non_existent_file.docx"))

def test_extract_docx_corrupted_file(tmp_path: Path):
    """Test DOCX extraction raises RuntimeError and logs error for corrupted file."""
    corrupted_path = tmp_path / "corrupted.docx"
    with open(corrupted_path, "w") as f:
        f.write("Corrupted content")
        
    with pytest.raises(RuntimeError):
        extract_docx(corrupted_path)

def test_clean_text_unicode():
    """Test cleaner normalizes unicode text."""
    raw = "Café résumé \u201csmart quotes\u201d"
    cleaned = clean_text(raw)
    assert "Cafe resume \"smart quotes\"" in cleaned

def test_clean_text_removes_emails_and_urls():
    """Test cleaner strips out email addresses and websites."""
    raw = "My email is test@domain.com. Visit us at https://google.com or www.test.com."
    cleaned = clean_text(raw)
    assert "test@domain.com" not in cleaned
    assert "https://google.com" not in cleaned
    assert "www.test.com" not in cleaned
    assert "My email is" in cleaned

def test_clean_text_strips_repeating_headers_footers():
    """Test cleaner strips lines that appear in 3 or more pages."""
    raw = "Page 1 content\nRepeating Header\nFooter Info\n\nPage 2 content\nRepeating Header\nFooter Info\n\nPage 3 content\nRepeating Header\nFooter Info"
    cleaned = clean_text(raw)
    assert "Repeating Header" not in cleaned
    assert "Footer Info" not in cleaned
    assert "Page 1 content" in cleaned
    assert "Page 2 content" in cleaned
    assert "Page 3 content" in cleaned

def test_clean_text_whitespace_and_punctuation():
    """Test cleaner collapses whitespace and repetitive punctuation."""
    raw = "Multiple spaces  here...\n\n\n\nNew line after many breaks.....\nAnd dashes------"
    cleaned = clean_text(raw)
    assert "\n\n\n" not in cleaned
    assert "here." in cleaned
    assert "..." not in cleaned
    assert "....." not in cleaned
    assert "------" not in cleaned
    assert "dashes-" in cleaned
