# Technical Breakdown:
# - Tests the CSV and JSON report writers.
# - Confirms that exported CSV contains all expected headers and data rows.
# - Asserts that the JSON export parses correctly and maps candidate metadata and gap analysis.
# - Validates that timestamps are correctly embedded and sanitized for file systems.

import csv
import json
import pytest
from pathlib import Path
from ranking import CandidateResult, GapReport
from ranking.report import write_results

def test_write_results(tmp_path: Path):
    """Test results are written to CSV and JSON formats with correct schema."""
    candidates = [
        CandidateResult(
            name="John Doe",
            file_path=Path("john_doe.pdf"),
            fit_score=94.20,
            rank=1,
            gap_report=GapReport(
                present_skills=["python", "sql"],
                missing_skills=["kubernetes"],
                inferred_skills=["pytorch"],
                gap_score=62.50
            )
        )
    ]

    timestamp = "2026-06-24T14:32:07"
    model_name = "all-MiniLM-L6-v2"
    threshold = 60.0

    csv_path, json_path = write_results(
        candidates, tmp_path, timestamp, model_name, threshold
    )

    # 1. Verify file paths and names
    assert csv_path.exists()
    assert json_path.exists()
    assert "2026-06-24T14-32-07" in csv_path.name
    assert "2026-06-24T14-32-07" in json_path.name

    # 2. Verify CSV contents
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Header row
        assert rows[0] == [
            "rank",
            "candidate_name",
            "fit_score",
            "gap_score",
            "missing_skills_count",
            "file_path"
        ]
        # Data row
        assert rows[1][0] == "1"
        assert rows[1][1] == "John Doe"
        assert rows[1][2] == "94.2"
        assert rows[1][3] == "62.5"
        assert rows[1][4] == "1"
        assert rows[1][5] == "john_doe.pdf"

    # 3. Verify JSON contents
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
        # Metadata
        assert data["metadata"]["run_timestamp"] == timestamp
        assert data["metadata"]["model_name"] == model_name
        assert data["metadata"]["threshold"] == threshold
        
        # Candidates list
        assert len(data["candidates"]) == 1
        cand = data["candidates"][0]
        assert cand["name"] == "John Doe"
        assert cand["fit_score"] == 94.2
        assert cand["gap_report"]["gap_score"] == 62.5
        assert cand["gap_report"]["present_skills"] == ["python", "sql"]
        assert cand["gap_report"]["inferred_skills"] == ["pytorch"]
        assert cand["gap_report"]["missing_skills"] == ["kubernetes"]
