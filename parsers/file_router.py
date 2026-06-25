# Technical Breakdown:
# - Automatically detects file type by extension and routes to correct parsing function.
# - Integrates parsers/cleaner.py's clean_text to return fully prepared text strings.
# - Manages batch operations, skipping failures, logging them, and continuing with the remaining files.
# - Logs unsupported extension attempts and parsing errors to data/logs/failed_files.log.

import datetime
from pathlib import Path
from typing import Callable, Dict, List
from parsers.pdf_parser import extract_pdf
from parsers.docx_parser import extract_docx
from parsers.cleaner import clean_text
from config.settings import LOG_FILE

class FileRouter:
    """Router to detect file types by extension and dispatch to the correct parser."""
    
    SUPPORTED_EXTENSIONS: Dict[str, Callable[[Path], str]] = {
        ".pdf": extract_pdf,
        ".docx": extract_docx,
    }

    def route(self, path: Path) -> str:
        """Auto-detect file type by extension and dispatch to correct parser.

        Args:
            path (Path): Path to the file.

        Returns:
            str: Extracted and cleaned text.

        Raises:
            ValueError: If the file extension is not recognised/supported.
            FileNotFoundError: If the file does not exist.
            RuntimeError: If parsing fails.
        """
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")

        ext = path_obj.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            supported = ", ".join(self.SUPPORTED_EXTENSIONS.keys())
            error_msg = f"Unsupported extension: {ext}. Supported types: {supported}"
            
            # Log unsupported extension
            timestamp = datetime.datetime.now().isoformat()
            log_line = f"[{timestamp}] [Router Error] {path_obj}: {error_msg}\n"
            try:
                LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(LOG_FILE, "a", encoding="utf-8") as log_f:
                    log_f.write(log_line)
            except Exception:
                pass
                
            raise ValueError(error_msg)

        # Call the parser function
        parser_func = self.SUPPORTED_EXTENSIONS[ext]
        raw_text = parser_func(path_obj)
        
        # Clean and return text
        return clean_text(raw_text)

    def route_batch(self, paths: List[Path]) -> Dict[str, str]:
        """Route a batch of files; skip failures, log them, return successful extractions.

        Args:
            paths (List[Path]): List of paths to extract.

        Returns:
            Dict[str, str]: Mapping of filename (str) to cleaned text (str)
                            for successfully parsed files.
        """
        results: Dict[str, str] = {}
        for path in paths:
            path_obj = Path(path)
            try:
                cleaned_text = self.route(path_obj)
                results[path_obj.name] = cleaned_text
            except Exception as e:
                # Log batch routing failure
                timestamp = datetime.datetime.now().isoformat()
                log_line = f"[{timestamp}] [Router Batch Error] {path_obj.name}: {str(e)}\n"
                try:
                    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
                    with open(LOG_FILE, "a", encoding="utf-8") as log_f:
                        log_f.write(log_line)
                except Exception:
                    pass
        return results
