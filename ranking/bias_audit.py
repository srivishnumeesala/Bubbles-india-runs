# Technical Breakdown:
# - Self-auditing layer to detect potential recruiting biases in rank outputs.
# - Scans resume text for proxy terms representing institutional prestige or age signals (graduation years).
# - Segregates candidates into a flagged (contains proxy) and unflagged (does not contain proxy) group.
# - Calculates the difference in average fit scores between groups: abs(mean_flagged - mean_unflagged).
# - Flags the audit (flagged=True) if this delta exceeds BIAS_DELTA_THRESHOLD (default: 10 points).
# - Provides structured summaries and human-in-the-loop recommendations.

import re
from typing import Dict, List
from ranking import CandidateResult, BiasAuditReport
from config.settings import DEMOGRAPHIC_PROXY_TERMS, BIAS_DELTA_THRESHOLD

def run_bias_audit(
    candidates: List[CandidateResult],
    resume_texts: Dict[str, str],
) -> BiasAuditReport:
    """Detect if demographic-proxy terms correlate with score distribution.

    Args:
        candidates (List[CandidateResult]): Sorted candidate results.
        resume_texts (Dict[str, str]): Mapping of candidate filename to cleaned resume text.

    Returns:
        BiasAuditReport: Calculated bias audit results.
    """
    if not candidates or not resume_texts:
        return BiasAuditReport(
            flagged=False,
            proxy_keywords_found=[],
            correlation_summary="No candidates available for bias audit.",
            recommendation="Please upload candidates to run the audit."
        )

    # Dictionary to hold proxy matches per candidate: {candidate_name: [list of proxies found]}
    candidate_proxies: Dict[str, List[str]] = {c.name: [] for c in candidates}
    all_proxies_found = set()
    
    # Check for proxies in each candidate's resume
    for candidate in candidates:
        filename = candidate.file_path.name
        text = resume_texts.get(filename, "").lower()
        if not text:
            continue

        for category, terms in DEMOGRAPHIC_PROXY_TERMS.items():
            for term in terms:
                # If term is a regex pattern (like graduation years), use re.search
                # Let's check if the term looks like a regex pattern (e.g. contains \b or \d)
                if '\\b' in term or '\\d' in term or '[' in term:
                    match = re.search(term, text)
                    if match:
                        matched_text = match.group(0)
                        candidate_proxies[candidate.name].append(f"{category}:{matched_text}")
                        all_proxies_found.add(f"{category}:{matched_text}")
                else:
                    # Direct substring check with word boundaries
                    pattern = r'\b' + re.escape(term.lower()) + r'\b'
                    if re.search(pattern, text):
                        candidate_proxies[candidate.name].append(f"{category}:{term}")
                        all_proxies_found.add(f"{category}:{term}")

    # Separate candidates into flagged and unflagged groups
    flagged_candidates = [c for c in candidates if len(candidate_proxies[c.name]) > 0]
    unflagged_candidates = [c for c in candidates if len(candidate_proxies[c.name]) == 0]

    flagged_count = len(flagged_candidates)
    unflagged_count = len(unflagged_candidates)

    if flagged_count == 0 or unflagged_count == 0:
        # Cannot calculate delta if one group is empty
        summary = (
            f"No correlation could be calculated. "
            f"Flagged candidates (contain proxy terms): {flagged_count}, "
            f"Unflagged candidates: {unflagged_count}."
        )
        recommendation = "Add a more diverse set of resumes to perform a proxy correlation audit."
        return BiasAuditReport(
            flagged=False,
            proxy_keywords_found=sorted(list(all_proxies_found)),
            correlation_summary=summary,
            recommendation=recommendation
        )

    # Compute mean fit scores
    mean_flagged = sum(c.fit_score for c in flagged_candidates) / flagged_count
    mean_unflagged = sum(c.fit_score for c in unflagged_candidates) / unflagged_count
    score_delta = abs(mean_flagged - mean_unflagged)

    is_flagged = score_delta > BIAS_DELTA_THRESHOLD

    summary = (
        f"Averaged Fit Score for candidates with demographic/institutional proxies: {mean_flagged:.2f} "
        f"(Count: {flagged_count}).\n"
        f"Averaged Fit Score for unflagged candidates: {mean_unflagged:.2f} "
        f"(Count: {unflagged_count}).\n"
        f"Calculated Score Disparity Delta: {score_delta:.2f} points "
        f"(Audit Threshold: {BIAS_DELTA_THRESHOLD:.1f})."
    )

    if is_flagged:
        recommendation = (
            "WARNING: A significant score disparity (> 10 points) has been detected between "
            "candidates with institutional/demographic proxies (e.g. Ivy League, graduation years) "
            "and other candidates. We highly recommend masking education names, institutional brands, "
            "and graduation dates from the resume text before parsing, followed by a human-in-the-loop audit."
        )
    else:
        recommendation = (
            "Audit Normal: The score variance between candidates possessing proxy keywords "
            "and those who do not falls within acceptable ranges. Continue monitoring."
        )

    return BiasAuditReport(
        flagged=is_flagged,
        proxy_keywords_found=sorted(list(all_proxies_found)),
        correlation_summary=summary,
        recommendation=recommendation
    )
