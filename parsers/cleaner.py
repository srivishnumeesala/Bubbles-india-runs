# Technical Breakdown:
# - Standardizes and normalizes extracted text content.
# - Uses NFKD unicode decomposition to convert non-standard characters to ASCII approximations.
# - Removes noise (emails, URLs) that can skew semantic similarity vectors.
# - Detects repeating lines (e.g. headers/footers) by analyzing frequency across multi-page texts.
# - Collapses multiple blank lines and repeated punctuation (dots, hyphens, etc.) to keep clean tokens.

import re
import unicodedata
from collections import defaultdict

def clean_text(raw: str) -> str:
    """Clean and normalize raw extracted text for embedding generation.

    Performs:
      1. Decode unicode normalisation (NFKD -> ASCII approximation)
      2. Remove email addresses and URLs
      3. Strip page headers/footers (repeated lines in >=3 pages)
      4. Collapse 2 or more consecutive blank lines to exactly 1
      5. Strip leading/trailing whitespace per line
      6. Remove repeated punctuation (e.g. "......" -> ".")
      7. Return cleaned string

    Args:
        raw (str): The raw text extracted from the document.

    Returns:
        str: Cleaned and normalized text.
    """
    if not raw:
        return ""

    # 1. Replace smart quotes explicitly to standard ASCII quotes
    text_quotes = raw.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")

    # 2. Unicode normalization (NFKD) and ASCII conversion to remove combining accents
    normalized = unicodedata.normalize('NFKD', text_quotes)
    ascii_text = normalized.encode('ascii', 'ignore').decode('utf-8')

    # 3. Remove email addresses and URLs
    # Email regex pattern
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    # URL regex pattern
    url_pattern = r'https?://\S+|www\.\S+'
    
    text_no_urls = re.sub(url_pattern, '', ascii_text)
    text_no_emails = re.sub(email_pattern, '', text_no_urls)

    # 3. Detect and strip headers/footers (lines repeating in >= 3 pages)
    # Split text into pages by double newline
    pages = text_no_emails.split('\n\n')
    
    line_page_presence = defaultdict(set)
    for page_idx, page in enumerate(pages):
        for line in page.split('\n'):
            stripped_line = line.strip()
            if stripped_line:
                line_page_presence[stripped_line].add(page_idx)
                
    header_footers = {line for line, pages_seen in line_page_presence.items() if len(pages_seen) >= 3}

    cleaned_pages = []
    for page in pages:
        cleaned_lines = []
        for line in page.split('\n'):
            stripped_line = line.strip()
            if stripped_line in header_footers:
                continue
            cleaned_lines.append(stripped_line)
        cleaned_pages.append("\n".join(cleaned_lines))
        
    reconstructed = "\n\n".join(cleaned_pages)

    # 4. Collapse >= 2 consecutive blank lines to exactly 1 blank line
    # Multiple blank lines show up as 3 or more newlines
    collapsed = re.sub(r'\n{3,}', '\n\n', reconstructed)

    # 5. Strip leading/trailing whitespace per line and collapse repeated spaces
    # Let's split by line, strip, and rejoin.
    lines = [line.strip() for line in collapsed.split('\n')]
    
    # 6. Remove repeated punctuation (e.g. "......" -> ".")
    cleaned_text_block = "\n".join(lines)
    cleaned_text_block = re.sub(r'\.{2,}', '.', cleaned_text_block)
    cleaned_text_block = re.sub(r'-{2,}', '-', cleaned_text_block)
    cleaned_text_block = re.sub(r'={2,}', '=', cleaned_text_block)
    cleaned_text_block = re.sub(r'_{2,}', '_', cleaned_text_block)
    cleaned_text_block = re.sub(r'\*{2,}', '*', cleaned_text_block)

    # 7. Return cleaned string
    return cleaned_text_block.strip()
