# Knowledge Base Note — Semantic Resume Ranker

## Model Details & Config Location
- **Default Model**: `all-MiniLM-L6-v2` (384-dimensional dense vectors).
- **Configuration File**: [settings.py](file:///C:/Users/srivi/.gemini/antigravity/scratch/semantic_resume_ranker/config/settings.py) and [.env](file:///C:/Users/srivi/.gemini/antigravity/scratch/semantic_resume_ranker/.env).

## How to Add a New Parser for a New File Type
1. Create your parser module (e.g. `parsers/txt_parser.py`) containing your extraction logic:
   ```python
   def extract_txt(path: Path) -> str:
       # ... read and return raw text
   ```
2. Import and register the new extension and function in `parsers/file_router.py` inside `SUPPORTED_EXTENSIONS`:
   ```python
   from parsers.txt_parser import extract_txt
   
   SUPPORTED_EXTENSIONS = {
       ".pdf": extract_pdf,
       ".docx": extract_docx,
       ".txt": extract_txt,
   }
   ```
3. Update `requirements.txt` if any new parsing library is introduced.

## How to Swap the Embedding Model
1. Open the `.env` file in the root directory.
2. Edit the `MODEL_NAME` variable to point to any Hugging Face SBERT model name (e.g. `all-mpnet-base-v2` or `all-distilroberta-v1`):
   ```dotenv
   MODEL_NAME=all-mpnet-base-v2
   ```
3. Restart the Streamlit dashboard. The singleton cache will automatically clear and fetch the new model.

## How to Add a New Bias Proxy Category
1. Open [settings.py](file:///C:/Users/srivi/.gemini/antigravity/scratch/semantic_resume_ranker/config/settings.py).
2. Locate the `DEMOGRAPHIC_PROXY_TERMS` dictionary.
3. Add a new key for your category (e.g. `disability_markers` or `gender_proxies`) mapped to a list of terms or regex patterns:
   ```python
   DEMOGRAPHIC_PROXY_TERMS = {
       ...
       "new_category": ["proxy_term_1", r"\b(regex_pattern)\b"]
   }
   ```
4. Run the analysis. The bias auditing module will automatically scan for these new terms.

## How to Run the Full Test Suite
Execute the following command in the project root:
```bash
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```
All tests must pass and coverage should meet the >= 80% threshold.
