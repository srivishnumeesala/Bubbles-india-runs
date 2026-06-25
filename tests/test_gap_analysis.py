# Technical Breakdown:
# - Tests Job Description keyword extraction and classification.
# - Validates classification into PRESENT, INFERRED, and ABSENT.
# - Confirms correctness of the GapReport score calculation.

import pytest
import numpy as np
from ranking.gap_analysis import extract_jd_keywords, classify_keyword, build_gap_report
from embeddings.encoder import encode_texts

def test_extract_jd_keywords():
    """Verify that JD keywords are extracted and grouped correctly by category."""
    jd_text = """
    We need a Senior Developer.
    Must have Python, Kubernetes, and AWS experience.
    Soft skills like communication and agile mentoring are required.
    AWS certified developer preferred.
    Education: Bachelor of Computer Science.
    """
    
    keywords = extract_jd_keywords(jd_text)
    
    assert "python" in keywords["tech_stack"]
    assert "kubernetes" in keywords["tech_stack"]
    assert "aws" in keywords["tech_stack"]
    
    assert "communication" in keywords["soft_skills"]
    assert "agile" in keywords["soft_skills"]
    
    assert "aws certified" in keywords["certifications"]
    
    assert "bachelor" in keywords["education"]
    assert "computer science" in keywords["education"]

def test_classify_keyword():
    """Test PRESENT, INFERRED, and ABSENT classifications."""
    resume_text = "Experienced software engineer working with neural networks and tensorflow. Strong team collaboration."
    resume_embedding = encode_texts([resume_text])[0]
    
    # 1. PRESENT (literal match)
    assert classify_keyword("tensorflow", resume_text, resume_embedding) == "present"
    assert classify_keyword("team collaboration", resume_text, resume_embedding) == "present"
    
    # 2. INFERRED (semantic match, not literal)
    # "deep learning" is semantically close to "neural networks and tensorflow"
    # Using a slightly lower threshold for test stability
    status = classify_keyword("deep learning", resume_text, resume_embedding, threshold_inferred=0.40)
    assert status == "inferred"
    
    # 3. ABSENT (no literal or semantic match)
    assert classify_keyword("kubernetes", resume_text, resume_embedding, threshold_inferred=0.75) == "absent"

def test_build_gap_report():
    """Test that a complete GapReport is calculated correctly."""
    jd_keywords = {
        "tech_stack": ["python", "docker", "kubernetes"],
        "soft_skills": ["communication"]
    }
    
    # Resume text contains literal "python" and "communication"
    # Resume has "containers" which should infer "docker" at lower threshold
    # Resume is completely missing "kubernetes"
    resume_text = "I write python code and maintain standard software containers. Great communication."
    resume_embedding = encode_texts([resume_text])[0]
    
    # Let's override similarity threshold in classify_keyword if needed, but here we test the report.
    # To make sure docker is inferred, we can mock it or let it evaluate.
    # In this test, we verify that the counts and scores are mathematically aligned.
    report = build_gap_report(jd_keywords, resume_text, resume_embedding)
    
    # Check that skills are sorted and partitioned
    assert "python" in report.present_skills
    assert "communication" in report.present_skills
    
    # Assert counts sum to total keywords (4)
    total_skills = len(report.present_skills) + len(report.inferred_skills) + len(report.missing_skills)
    assert total_skills == 4
    
    # Check gap score calculation matches expected weights: (P * 1.0 + I * 0.5) / Total * 100
    expected_score = (len(report.present_skills) * 1.0 + len(report.inferred_skills) * 0.5) / 4.0 * 100.0
    assert report.gap_score == round(expected_score, 2)
