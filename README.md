# Semantic AI Resume Ranking System

## Project Overview
The Semantic AI Resume Ranking System is a talent intelligence application designed to match job descriptions against candidate resumes semantically. Leveraging Sentence-BERT representations, the system ranks resumes based on semantic fit, maps skill coverage (present, missing, and inferred), and audits the ranking process for demographic and institutional proxies to mitigate algorithmic bias.

## Architecture Decision Records (ADR)

### ADR-001: PyMuPDF over pdfplumber
- **Context**: Resume parsing requires fast, reliable text extraction from PDF files while maintaining layout order.
- **Decision**: Selected PyMuPDF (`fitz`) over `pdfplumber`.
- **Justification**: PyMuPDF is 3–5× faster, handles password-protected files, and preserves multi-column layout order via standard `get_text(sort=True)` parameters.

### ADR-002: MiniLM-L6-v2 over BERT-base
- **Context**: Selecting a dense vector representations model that fits standard consumer hardware and runs with low latency.
- **Decision**: Pinned SBERT model to `all-MiniLM-L6-v2`.
- **Justification**: Offers 6× faster inference on CPU (22ms vs 132ms per sentence), outputs lightweight 384-dimensional vectors that conserve RAM, and achieves 90%+ performance of BERT-base on SBERT benchmarks.

### ADR-003: Streamlit over Flask/FastAPI
- **Context**: Creating an interactive user dashboard for recruiters and administrators.
- **Decision**: Developed the web interface using Streamlit.
- **Justification**: Eliminates frontend/backend integration overhead for rapid prototyping, offering rich interactive controls and fast component rendering natively in Python.

### ADR-004: Cosine Similarity over BM25/Keyword Matching
- **Context**: Resumes and job descriptions often use different terms for identical concepts (e.g., "deep learning" vs. "neural networks").
- **Decision**: Employed Cosine Similarity on dense sentence vectors.
- **Justification**: Cosine similarity captures deep semantic associations rather than literal syntax. By L2-normalizing vectors, computation is optimized as a dot product, enabling fast matching of large resume cohorts.

### ADR-005: spaCy for Keyword Extraction over Regex
- **Context**: Extracting relevant professional skills, soft skills, and certifications from job description text.
- **Decision**: Used spaCy noun chunks combined with a structured wordlist.
- **Justification**: Rule-based regex matches fail on lexical variations and grammatical contexts. spaCy's dependency parser identifies noun chunks linguistically, yielding high precision.

---

## Quick-Start
```bash
pip install -r requirements.txt
cp .env.example .env
streamlit run ui/app.py
```

---

## Folder Structure
```
semantic_resume_ranker/
├── AGENTS.md                         # Multi-agent ownership contract
├── README.md                         # ADR, quickstart, citations
├── requirements.txt                  # All dependencies pinned
├── .env                              # Local environment variables
├── .env.example                      # Environment template
├── .agents/
│   ├── rules/
│   │   └── project-conventions.md   # Workspace rules
│   └── skills/
│       ├── phase-gate-checker/
│       │   └── SKILL.md             # Verification gate skill
│       ├── python-type-enforcer/
│       │   └── SKILL.md             # Typing enforcer skill
│       └── streamlit-rerun-guard/
│           └── SKILL.md             # Streamlit rerun guard skill
├── config/
│   └── settings.py                   # Central configuration
├── data/
│   ├── resumes/                      # PDF/DOCX resumes folder
│   ├── job_descriptions/             # Job description text files
│   ├── outputs/                      # Timestamped CSV/JSON rankings
│   ├── cache/                        # Hash-keyed .npy embedding cache
│   └── logs/
│       └── failed_files.log          # Corrupted file logs
├── parsers/
│   ├── __init__.py
│   ├── pdf_parser.py                 # PyMuPDF text extraction
│   ├── docx_parser.py                # python-docx parser
│   ├── cleaner.py                    # Unicode/regex cleaner
│   └── file_router.py                # Auto-routes extensions
├── embeddings/
│   ├── __init__.py
│   ├── model_loader.py               # Singleton SBERT model loader
│   └── encoder.py                    # Vectorizer with cache
├── ranking/
│   ├── __init__.py                   # Data models
│   ├── similarity.py                 # Cosine ranking scorer
│   ├── gap_analysis.py               # Skill gap Classifier
│   ├── bias_audit.py                 # Bias Audit correlation layer
│   └── report.py                     # Output report exporter
├── ui/
│   ├── app.py                        # Streamlit entry point
│   ├── styles.css                    # CSS theme rules
│   └── components/
│       ├── uploader.py               # Sidebar inputs
│       ├── score_card.py             # Rankings lists & details
│       ├── radar_chart.py            # Skill radar visualization
│       ├── gap_panel.py              # Skill classification grid
│       ├── export_bar.py             # Export components
│       ├── compare_view.py           # Side-by-side comparator
│       ├── bias_panel.py             # Bias reports rendering
│       └── empty_state.py            # Illustrated welcome state
└── tests/
    ├── conftest.py                   # Pytest shared fixtures
    ├── test_parsers.py
    ├── test_file_router.py
    ├── test_encoder.py
    ├── test_similarity.py
    ├── test_gap_analysis.py
    ├── test_bias_audit.py
    └── test_report.py
```

---

## Academic Citations
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *EMNLP 2019*. https://arxiv.org/abs/1908.10084
- Cosine similarity formula:
  $$\text{sim}(A,B) = \frac{A \cdot B}{\|A\| \|B\|}$$

---

## Bias Audit Methodology Note
To prevent the propagation of historical hiring inequalities, this system self-audits rankings for bias. It operates by scanning candidates' resumes for demographic and institutional proxies (such as graduation years indicating age, or prestige universities representing socioeconomic privilege). It computes the difference between the mean fit scores of the flagged group and the unflagged group. If this score disparity exceeds a configured threshold, the system flags the run as having a potential bias signal. It is important to note that this is a proxy detection mechanism and is intended as a screening tool to alert human reviewers, not an absolute evaluation of bias.
