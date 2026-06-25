# Technical Breakdown:
# - Displays a three-column skill distribution grid for Present, Inferred, and Missing skills.
# - Renders colored HTML badges dynamically.
# - Integrates styling properties from ui/styles.css to match themes.
# - Handles empty skills lists with clean placeholders.

import streamlit as st
from ranking import GapReport

def render_gap_grid(gap_report: GapReport) -> None:
    """Render a 3-column pill grid for Present, Inferred, and Missing skills.

    Args:
        gap_report (GapReport): Candidate skill gap report.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h4 style='font-size:14px; font-weight:600; color: #58d667; margin-bottom:10px;'>✅ Present Skills</h4>", unsafe_allow_html=True)
        if gap_report.present_skills:
            badges_html = "".join([
                f"<span class='skill-badge skill-badge-present'>{sk}</span>"
                for sk in gap_report.present_skills
            ])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.caption("No matching skills literally found.")

    with col2:
        st.markdown("<h4 style='font-size:14px; font-weight:600; color: #bc8cff; margin-bottom:10px;'>⚠️ Inferred Skills</h4>", unsafe_allow_html=True)
        if gap_report.inferred_skills:
            badges_html = "".join([
                f"<span class='skill-badge skill-badge-inferred'>{sk}</span>"
                for sk in gap_report.inferred_skills
            ])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.caption("No semantic alignments inferred.")

    with col3:
        st.markdown("<h4 style='font-size:14px; font-weight:600; color: #ff7b72; margin-bottom:10px;'>❌ Missing Skills</h4>", unsafe_allow_html=True)
        if gap_report.missing_skills:
            badges_html = "".join([
                f"<span class='skill-badge skill-badge-missing'>{sk}</span>"
                for sk in gap_report.missing_skills
            ])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.caption("All keywords covered!")
