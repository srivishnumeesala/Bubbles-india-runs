# Technical Breakdown:
# - Exports analysis reports in structured CSV and nested JSON formats.
# - Integrates metadata (run timestamp, model used, and score threshold) inside the export files.
# - Formats file names dynamically using timestamps to prevent accidental overrides.
# - Safely handles Path serialization during file output.

import csv
import json
from pathlib import Path
from typing import List, Tuple
from ranking import CandidateResult

def write_results(
    candidates: List[CandidateResult],
    output_dir: Path,
    run_timestamp: str,
    model_name: str,
    threshold: float,
) -> Tuple[Path, Path]:
    """Write results to CSV and JSON formats.

    Args:
        candidates (List[CandidateResult]): Candidate results.
        output_dir (Path): Output directory path.
        run_timestamp (str): ISO timestamp string.
        model_name (str): SBERT model name.
        threshold (float): Scoring threshold.

    Returns:
        Tuple[Path, Path]: (csv_path, json_path).
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Clean timestamp for filename use (replace colons to avoid filesystem errors on Windows)
    safe_ts = run_timestamp.replace(":", "-")
    csv_file = output_path / f"results_{safe_ts}.csv"
    json_file = output_path / f"results_{safe_ts}.json"

    # 1. Write CSV
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rank",
            "candidate_name",
            "fit_score",
            "gap_score",
            "missing_skills_count",
            "file_path"
        ])
        for cand in candidates:
            writer.writerow([
                cand.rank,
                cand.name,
                cand.fit_score,
                cand.gap_report.gap_score,
                len(cand.gap_report.missing_skills),
                str(cand.file_path)
            ])

    # 2. Write JSON
    report_data = {
        "metadata": {
            "run_timestamp": run_timestamp,
            "model_name": model_name,
            "threshold": threshold,
            "total_candidates": len(candidates)
        },
        "candidates": []
    }

    for cand in candidates:
        report_data["candidates"].append({
            "rank": cand.rank,
            "name": cand.name,
            "fit_score": cand.fit_score,
            "file_path": str(cand.file_path),
            "gap_report": {
                "present_skills": cand.gap_report.present_skills,
                "inferred_skills": cand.gap_report.inferred_skills,
                "missing_skills": cand.gap_report.missing_skills,
                "gap_score": cand.gap_report.gap_score
            }
        })

    with open(json_file, mode="w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)

    return csv_file, json_file
