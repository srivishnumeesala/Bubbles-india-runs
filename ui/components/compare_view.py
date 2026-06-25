# Technical Breakdown:
# - Renders a side-by-side comparative table for up to 3 candidate profiles.
# - Prompts user selection using multiselect input widgets.
# - Renders column-based comparison lists containing match scores, present, inferred, and missing tags.
# - Evaluates all JD keywords to show checks/warns/crosses side-by-side.

import streamlit as st
from typing import Dict, List
from ranking import CandidateResult

def render_compare_view(candidates: List[CandidateResult], jd_keywords: Dict[str, List[str]]) -> None:
    """Render the side-by-side candidate comparison view.

    Args:
        candidates (List[CandidateResult]): Ranked list of candidates.
        jd_keywords (Dict[str, List[str]]): Extracted JD keywords by category.
    """
    if not candidates:
        st.info("No candidates processed yet.")
        return

    st.markdown("<h3 style='font-size:18px; font-weight:600;'>Candidate Comparator</h3>", unsafe_allow_html=True)
    st.markdown("<span style='color:var(--text-muted); font-size:12px;'>Select up to 3 candidates to compare skill coverage side-by-side.</span><br><br>", unsafe_allow_html=True)

    # 1. Selection dropdown
    names = [c.name for c in candidates]
    selected_names = st.multiselect("Select candidates to compare:", options=names, default=names[:min(3, len(names))])

    if not selected_names:
        st.warning("Please select at least one candidate to compare.")
        return

    if len(selected_names) > 3:
        st.error("You can select a maximum of 3 candidates for comparison.")
        selected_names = selected_names[:3]

    # Map names back to candidate objects
    selected_candidates = [c for c in candidates if c.name in selected_names]

    # Get all unique keywords extracted from JD
    all_keywords = set()
    for keywords in jd_keywords.values():
        all_keywords.update(keywords)
    sorted_keywords = sorted(list(all_keywords))

    # 2. Render side-by-side layout
    cols = st.columns(len(selected_candidates))

    for idx, cand in enumerate(selected_candidates):
        with cols[idx]:
            # Renders candidate metric card
            st.markdown(
                f"""
                <div class="metric-card-container">
                    <div style="font-size:18px; font-weight:700; color:#58A6FF; margin-bottom:5px;">{cand.name}</div>
                    <div class="metric-card-title">RANK #{cand.rank}</div>
                    <div style="font-size:32px; font-weight:700; margin:10px 0; font-family: 'JetBrains Mono';">
                        {cand.fit_score:.1f}%
                    </div>
                    <div style="font-size:12px; color:var(--text-muted);">Gap Score: {cand.gap_report.gap_score:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Renders skill items list
            st.markdown("<h4 style='font-size:13px; font-weight:600; margin-top:15px; border-bottom:1px solid var(--border); padding-bottom:5px;'>Skill Coverage</h4>", unsafe_allow_html=True)
            
            if not sorted_keywords:
                st.caption("No keywords extracted from JD.")
                continue

            for kw in sorted_keywords:
                if kw in cand.gap_report.present_skills:
                    st.markdown(f"**✅ present** &nbsp;&nbsp;&nbsp;&nbsp; {kw}", unsafe_allow_html=True)
                elif kw in cand.gap_report.inferred_skills:
                    st.markdown(f"<span style='color:#bc8cff;'>**⚠️ inferred**</span> &nbsp;&nbsp; {kw}", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:#ff7b72;'>**❌ missing**</span> &nbsp;&nbsp;&nbsp; {kw}", unsafe_allow_html=True)
