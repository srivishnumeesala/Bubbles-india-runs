# Technical Breakdown:
# - Renders the main Rankings tab, which contains candidate metrics and search tables.
# - Displays a four-column key metric header row.
# - Formats table rows dynamically using styled st.expanders to represent interactive items.
# - Integrates a custom Plotly Gauge Chart for fit scores and connects Radar and Gap panels.
# - Displays the original parsed resume text in a collapsed sub-expander.

import streamlit as st
from typing import Dict, List
from ranking import CandidateResult
from ui.components.radar_chart import render_radar_chart
from ui.components.gap_panel import render_gap_grid

def score_colour(score: float) -> str:
    """Return hex color code representing the fit score band."""
    if score >= 70.0:
        return "#3FB950"  # green
    elif score >= 40.0:
        return "#D29922"  # amber
    else:
        return "#F85149"  # red

def get_progress_bar_text(score: float, width: int = 15) -> str:
    """Generate a text-based ASCII progress bar."""
    filled = int(round((score / 100.0) * width))
    empty = width - filled
    return "█" * filled + "░" * empty

def render_rankings_tab(
    candidates: List[CandidateResult],
    resume_texts: Dict[str, str],
    jd_keywords: Dict[str, List[str]],
    threshold: float
) -> None:
    import plotly.graph_objects as go
    """Renders the rankings metric row and candidate listing table.

    Args:
        candidates (List[CandidateResult]): Ranked list of candidates.
        resume_texts (Dict[str, str]): Raw/cleaned resume texts.
        jd_keywords (Dict[str, List[str]]): JD keywords by category.
        threshold (float): Minimum fit threshold.
    """
    if not candidates:
        st.info("No candidates processed yet.")
        return

    # 1. Metric Header Row
    total_cands = len(candidates)
    above_threshold = sum(1 for c in candidates if c.fit_score >= threshold)
    top_score = candidates[0].fit_score if candidates else 0.0
    avg_score = sum(c.fit_score for c in candidates) / total_cands if total_cands > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card-container">
                <div class="metric-card-title">👥 TOTAL CANDIDATES</div>
                <div class="metric-card-value">{total_cands}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card-container">
                <div class="metric-card-title">✅ ABOVE THRESHOLD</div>
                <div class="metric-card-value">{above_threshold}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card-container">
                <div class="metric-card-title">🏆 TOP FIT SCORE</div>
                <div class="metric-card-value">{top_score:.1f}%</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card-container">
                <div class="metric-card-title">📊 AVERAGE FIT</div>
                <div class="metric-card-value">{avg_score:.1f}%</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("<br><h3 style='font-size:18px; font-weight:600;'>Candidate Leaderboard</h3>", unsafe_allow_html=True)
    st.markdown("<span style='color:var(--text-muted); font-size:12px;'>Click on a candidate row to expand match intelligence details.</span><br><br>", unsafe_allow_html=True)

    # 2. Render Ranked Candidate Expanders (styled as table rows)
    for cand in candidates:
        # Determine badges
        badge = str(cand.rank)
        if cand.rank == 1:
            badge = "🥇"
        elif cand.rank == 2:
            badge = "🥈"
        elif cand.rank == 3:
            badge = "🥉"

        prog_bar = get_progress_bar_text(cand.fit_score, width=12)
        score_col = score_colour(cand.fit_score)
        
        # Expander Header
        header_text = (
            f"{badge} │ **{cand.name}** │ "
            f"<span style='color:{score_col}; font-family:JetBrains Mono;'>{cand.fit_score:.1f}%</span> "
            f"<span style='color:{score_col}; font-family:monospace;'>{prog_bar}</span> │ "
            f"Gap Score: {cand.gap_report.gap_score:.1f}%"
        )
        
        # Streamlit expander
        with st.expander(header_text, expanded=False):
            # Render Candidate detail panel
            col_detail_left, col_detail_right = st.columns([1, 1])
            
            with col_detail_left:
                st.markdown("<h4 style='font-size:14px; font-weight:600; text-align:center;'>Match Score Indicator</h4>", unsafe_allow_html=True)
                
                # Plotly Gauge Chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=cand.fit_score,
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#8B949E"},
                        "bar": {"color": "#58A6FF"},
                        "bgcolor": "#21262D",
                        "steps": [
                            {"range": [0, 40], "color": "#2D1B1B"},    # dark red
                            {"range": [40, 70], "color": "#2D2510"},   # dark amber
                            {"range": [70, 100], "color": "#162218"},  # dark green
                        ],
                        "threshold": {
                            "line": {"color": score_colour(cand.fit_score), "width": 3},
                            "value": cand.fit_score,
                        },
                    },
                    number={"font": {"color": "#E6EDF3", "family": "Inter"}},
                ))
                fig.update_layout(
                    paper_bgcolor="#161B22",
                    font={"color": "#E6EDF3"},
                    height=200,
                    margin=dict(t=20, b=10, l=20, r=20),
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            with col_detail_right:
                st.markdown("<h4 style='font-size:14px; font-weight:600; text-align:center;'>Skill Category Coverage</h4>", unsafe_allow_html=True)
                # Plotly Radar Chart
                radar_fig = render_radar_chart(cand.gap_report, jd_keywords)
                st.plotly_chart(radar_fig, use_container_width=True, config={'displayModeBar': False})

            # Skills Gap Grid
            st.markdown("<hr style='border-top:1px solid var(--border); margin:10px 0;'>", unsafe_allow_html=True)
            render_gap_grid(cand.gap_report)

            # Raw Extracted Text block
            st.markdown("<br>", unsafe_allow_html=True)
            filename = cand.file_path.name
            raw_text = resume_texts.get(filename, "No text extracted.")
            with st.expander("📄 View Parsed Resume Text", expanded=False):
                st.code(raw_text, language="text")
