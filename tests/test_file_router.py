# Technical Breakdown:
# - Tests the FileRouter class.
# - Verifies correct routing based on file extensions.
# - Validates error handling for unsupported extensions and batch routing behavior.
# - Ensures failures do not block the entire batch and are logged appropriately.

import pytest
from pathlib import Path
from parsers.file_router import FileRouter
from config.settings import LOG_FILE

def test_file_router_success(sample_pdf: Path, sample_docx: Path):
    """Test router routes PDF and DOCX files successfully."""
    router = FileRouter()
    
    # PDF routing
    pdf_text = router.route(sample_pdf)
    assert "John Doe Resume" in pdf_text
    
    # DOCX routing
    docx_text = router.route(sample_docx)
    assert "Jane Smith Resume" in docx_text

def test_file_router_unsupported_extension(tmp_path: Path):
    """Test router raises ValueError and logs for unsupported file type."""
    router = FileRouter()
    txt_path = tmp_path / "resume.txt"
    with open(txt_path, "w") as f:
        f.write("Some text file contents")
        
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        
    with pytest.raises(ValueError) as excinfo:
        router.route(txt_path)
        
    assert "Unsupported extension" in str(excinfo.value)
    assert LOG_FILE.exists()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_content = f.read()
        assert "resume.txt" in log_content

def test_file_router_batch(sample_pdf: Path, sample_docx: Path, tmp_path: Path):
    """Test router handles batch operations, skipping invalid files and processing others."""
    router = FileRouter()
    
    # Make a bad path
    bad_path = tmp_path / "nonexistent.pdf"
    # Make an unsupported path
    unsupported_path = tmp_path / "image.png"
    with open(unsupported_path, "w") as f:
        f.write("PNG bytes mock")
        
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        
    paths = [sample_pdf, bad_path, sample_docx, unsupported_path]
    results = router.route_batch(paths)
    
    # Valid files must be in results
    assert sample_pdf.name in results
    assert sample_docx.name in results
    assert "John Doe" in results[sample_pdf.name]
    assert "Jane Smith" in results[sample_docx.name]
    
    # Invalid files must NOT be in results
    assert bad_path.name not in results
    assert unsupported_path.name not in results
    
    # Log file must record failures
    assert LOG_FILE.exists()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_content = f.read()
        assert "nonexistent.pdf" in log_content
        assert "image.png" in log_content
