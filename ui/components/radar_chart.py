# Technical Breakdown:
# - Renders a skills category radar chart using Plotly Graphical Objects.
# - Categorizes axis labels dynamically from the Job Description keywords.
# - Calculates weighted scores per category (Present=100%, Inferred=50%, Absent=0%).
# - Styles charts using custom dark themes to align with ui/styles.css.

from typing import Dict, List
from ranking import GapReport

def render_radar_chart(gap_report: GapReport, jd_keywords: Dict[str, List[str]]) -> "go.Figure":
    import plotly.graph_objects as go
    """Generate a Plotly radar chart showing category coverage.

    Args:
        gap_report (GapReport): Candidate skill gap report.
        jd_keywords (Dict[str, List[str]]): Extracted JD keywords by category.

    Returns:
        go.Figure: Plotly Radar Chart figure.
    """
    categories = []
    scores = []

    # Map category names to aesthetic display titles
    category_mapping = {
        "tech_stack": "Tech Stack",
        "soft_skills": "Soft Skills",
        "certifications": "Certifications",
        "education": "Education"
    }

    # Calculate average coverage score for each category
    for key, display_name in category_mapping.items():
        kws = jd_keywords.get(key, [])
        if not kws:
            # Skip empty categories
            continue
        
        categories.append(display_name)
        score_sum = 0.0
        for kw in kws:
            if kw in gap_report.present_skills:
                score_sum += 1.0
            elif kw in gap_report.inferred_skills:
                score_sum += 0.5
        
        avg_score = (score_sum / len(kws)) * 100.0
        scores.append(round(avg_score, 1))

    # Radar chart expects closed loops, so duplicate the first point if categories are present
    if categories:
        categories.append(categories[0])
        scores.append(scores[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(88, 166, 255, 0.2)', # Semi-transparent accent blue
        line=dict(color='#58A6FF', width=2),
        marker=dict(color='#58A6FF', size=6),
        name='Candidate Fit'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color='#8B949E',
                gridcolor='#30363D',
                tickfont=dict(color='#8B949E', size=9)
            ),
            angularaxis=dict(
                gridcolor='#30363D',
                tickfont=dict(color='#E6EDF3', size=10, family='Inter')
            ),
            bgcolor='#161B22' # Card background color
        ),
        paper_bgcolor='#161B22',
        plot_bgcolor='#161B22',
        margin=dict(t=30, b=20, l=40, r=40),
        height=260,
        showlegend=False
    )

    return fig
