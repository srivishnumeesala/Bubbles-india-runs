# Technical Breakdown:
# - Renders the bias audit panel inside a collapsible Streamlit expander.
# - Renders warning signs/banners dynamically based on report status flags.
# - Displays lists of flagged proxies (e.g. Ivy League, graduation years) found.
# - Shows statistical breakdowns and human-in-the-loop audit disclaimers.

import streamlit as st
from ranking import BiasAuditReport

def render_bias_panel(report: BiasAuditReport) -> None:
    """Render the bias audit report inside an expander.

    Args:
        report (BiasAuditReport): Calculated bias audit report.
    """
    with st.expander("⚠️ Bias Audit Report", expanded=False):
        if report.flagged:
            # Render Warning Banner
            st.warning("⚠️ Potential Bias Signal Flagged")
            
            st.markdown(
                f"""
                <div style="background-color: rgba(210, 153, 34, 0.1); border: 1px solid var(--accent-amber); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 15px;">
                    <strong style="color:var(--accent-amber);">Audit Alarm:</strong> {report.recommendation}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Show statistical summary
            st.markdown("##### Score Disparity Summary")
            st.code(report.correlation_summary, language="text")

            # Show matching proxy keywords
            st.markdown("##### Flagged Proxy Keywords Found")
            if report.proxy_keywords_found:
                pills = "".join([
                    f"<span class='skill-badge skill-badge-missing'>{pk}</span>"
                    for pk in report.proxy_keywords_found
                ])
                st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
            else:
                st.caption("No specific keywords matched (general statistical skew).")
                
            st.markdown(
                """
                <p style="color:var(--text-muted); font-size:11px; margin-top:15px; font-style:italic;">
                    Disclaimer: This is an automated proxy check. Variance in candidate ratings may occur for other job-related factors. Human evaluation is required before taking any action.
                </p>
                """,
                unsafe_allow_html=True
            )
        else:
            # Clean audit representation
            st.success("✅ No bias signals detected in this run.")
            
            st.markdown("##### Score Disparity Summary")
            st.code(report.correlation_summary, language="text")
            
            st.markdown("##### What was checked (Transparency)")
            st.markdown(
                """
                The system scanned candidate text for institutional and demographic proxy terms:
                - **Prestige Institutions**: Ivy League, Oxbridge, IIT, etc.
                - **Graduation Years**: Dates that imply age brackets.
                - **Cultural name patterns** (transparency).
                
                The difference in average fit ratings between the flagged and unflagged group fell within acceptable parameters.
                """
            )
            
            if report.proxy_keywords_found:
                st.markdown("##### Identifiers Found")
                pills = "".join([
                    f"<span class='skill-badge skill-badge-inferred'>{pk}</span>"
                    for pk in report.proxy_keywords_found
                ])
                st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
