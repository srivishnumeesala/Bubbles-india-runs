# Technical Breakdown:
# - Renders session parameters summary and file download triggers.
# - Formats analysis outputs into in-memory CSV and JSON strings.
# - Integrates Streamlit download buttons for instant web exports.
# - Coordinates naming parameters using standard timestamp formats.

import io
import csv
import json
import datetime
from typing import List
import streamlit as st
from ranking import CandidateResult

def render_export_bar(
    candidates: List[CandidateResult],
    model_name: str,
    threshold: float
) -> None:
    """Render the session parameters summary and download triggers.

    Args:
        candidates (List[CandidateResult]): Processed candidates results.
        model_name (str): SBERT model name used.
        threshold (float): Similarity threshold.
    """
    if not candidates:
        st.info("No candidates processed yet.")
        return

    # Generate current ISO timestamp for display and filenames
    timestamp = datetime.datetime.now().isoformat()
    safe_ts = timestamp.replace(":", "-")

    st.markdown("<h3 style='font-size:18px; font-weight:600;'>Export Results</h3>", unsafe_allow_html=True)
    
    # 1. Session Summary Box
    total_cands = len(candidates)
    above_threshold = sum(1 for c in candidates if c.fit_score >= threshold)
    
    st.markdown(
        f"""
        <div style="background-color: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 18px; margin-bottom: 20px;">
            <div style="font-size:14px; font-weight:600; color:#58A6FF; margin-bottom:10px;">Session Summary Metadata</div>
            <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <tr style="border-bottom:1px solid #21262D;">
                    <td style="padding:6px 0; color:var(--text-muted);">Run Timestamp</td>
                    <td style="padding:6px 0; font-family:JetBrains Mono; text-align:right;">{timestamp}</td>
                </tr>
                <tr style="border-bottom:1px solid #21262D;">
                    <td style="padding:6px 0; color:var(--text-muted);">Model Used</td>
                    <td style="padding:6px 0; font-family:JetBrains Mono; text-align:right;">{model_name}</td>
                </tr>
                <tr style="border-bottom:1px solid #21262D;">
                    <td style="padding:6px 0; color:var(--text-muted);">Similarity Threshold</td>
                    <td style="padding:6px 0; font-family:JetBrains Mono; text-align:right;">{threshold:.1f}</td>
                </tr>
                <tr>
                    <td style="padding:6px 0; color:var(--text-muted);">Candidates Counts</td>
                    <td style="padding:6px 0; text-align:right;">{total_cands} total, {above_threshold} above threshold</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. In-memory data preparation for downloads
    
    # (A) Prepare CSV
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow([
        "rank",
        "candidate_name",
        "fit_score",
        "gap_score",
        "missing_skills_count",
        "file_path"
    ])
    for cand in candidates:
        csv_writer.writerow([
            cand.rank,
            cand.name,
            cand.fit_score,
            cand.gap_report.gap_score,
            len(cand.gap_report.missing_skills),
            str(cand.file_path)
        ])
    csv_data = csv_buffer.getvalue()

    # (B) Prepare JSON
    report_data = {
        "metadata": {
            "run_timestamp": timestamp,
            "model_name": model_name,
            "threshold": threshold,
            "total_candidates": total_cands
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
    json_data = json.dumps(report_data, indent=4)

    # 3. Export Buttons Layout
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name=f"results_{safe_ts}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with btn_col2:
        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name=f"results_{safe_ts}.json",
            mime="application/json",
            use_container_width=True
        )
