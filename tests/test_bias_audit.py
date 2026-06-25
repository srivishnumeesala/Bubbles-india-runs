# Technical Breakdown:
# - Tests the bias auditing logic.
# - Seeds mock candidates with prestige university or age indicators.
# - Verifies that high score disparity deltas (> 10 points) result in flagged=True.
# - Verifies that minimal score differences result in flagged=False.

import pytest
from pathlib import Path
from ranking import CandidateResult, GapReport
from ranking.bias_audit import run_bias_audit

def test_run_bias_audit_flagged():
    """Verify that a large fit score difference between proxy groups triggers a flag."""
    candidates = [
        CandidateResult("Priya Sharma", Path("priya.pdf"), 95.0, 1, GapReport()),
        CandidateResult("Alex Johnson", Path("alex.pdf"), 90.0, 2, GapReport()),
        CandidateResult("James Lee", Path("james.pdf"), 75.0, 3, GapReport()),
        CandidateResult("Maria Garcia", Path("maria.pdf"), 70.0, 4, GapReport())
    ]
    
    # Priya and Alex have Harvard and Oxford (prestige institution proxy)
    # James and Maria have no proxy terms
    resume_texts = {
        "priya.pdf": "Attended Harvard University and got a degree in Computer Science.",
        "alex.pdf": "Studied at Oxford University. Senior engineer.",
        "james.pdf": "Developer at Tech Corp. 5 years experience.",
        "maria.pdf": "Software engineer. Python developer."
    }
    
    report = run_bias_audit(candidates, resume_texts)
    
    # Average of flagged (Priya, Alex) = (95 + 90)/2 = 92.5
    # Average of unflagged (James, Maria) = (75 + 70)/2 = 72.5
    # Delta = 20.0 (Threshold is 10.0) -> should be flagged
    assert report.flagged is True
    assert "institution_prestige:harvard" in report.proxy_keywords_found
    assert "institution_prestige:oxford" in report.proxy_keywords_found
    assert "Disparity Delta: 20.00" in report.correlation_summary

def test_run_bias_audit_normal():
    """Verify that small score variations do not trigger a flag."""
    candidates = [
        CandidateResult("Priya Sharma", Path("priya.pdf"), 85.0, 1, GapReport()),
        CandidateResult("Alex Johnson", Path("alex.pdf"), 80.0, 2, GapReport()),
        CandidateResult("James Lee", Path("james.pdf"), 83.0, 3, GapReport())
    ]
    
    # Priya graduated in 2012 (implied age proxy)
    # Alex and James do not have proxies
    resume_texts = {
        "priya.pdf": "Graduated in 2012. Python developer.",
        "alex.pdf": "Developer at Tech Corp.",
        "james.pdf": "CS graduate. Software engineer."
    }
    
    report = run_bias_audit(candidates, resume_texts)
    
    # Average of flagged (Priya) = 85.0
    # Average of unflagged (Alex, James) = (80 + 83)/2 = 81.5
    # Delta = 3.5 (Threshold is 10.0) -> should NOT be flagged
    assert report.flagged is False
    assert "graduation_year:2012" in report.proxy_keywords_found
    assert "Disparity Delta: 3.50" in report.correlation_summary
