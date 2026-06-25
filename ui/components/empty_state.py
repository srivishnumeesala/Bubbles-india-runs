# Technical Breakdown:
# - Renders a premium, visually stunning onboarding dashboard home screen.
# - Displays a hero badge, a gradient-styled header, and a talent-network SVG.
# - Renders four detailed feature cards with interactive CSS hover styles and custom HSL gradients.
# - Presents a clean step-by-step workflow timeline to guide the recruiter on next steps.
# - Uses textwrap.dedent to preserve GFM parsing safety.

import textwrap
import streamlit as st

def render_empty_state() -> None:
    """Display a premium visual welcome screen with detailed capability cards when no analysis has run."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. Hero Header Section with Glassmorphism / Gradients
    st.markdown(
        textwrap.dedent(
            """
            <div style="text-align: center; padding: 10px 0 30px 0;">
                <span style="
                    background: linear-gradient(135deg, rgba(88, 166, 255, 0.15) 0%, rgba(163, 113, 247, 0.15) 100%);
                    border: 1px solid rgba(88, 166, 255, 0.3);
                    color: #58A6FF;
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 1.5px;
                    text-transform: uppercase;
                ">
                    ✨ Next-Gen AI Recruitment
                </span>
                <h1 style="
                    font-size: 38px;
                    font-weight: 800;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    background: -webkit-linear-gradient(0deg, #58A6FF 30%, #A371F7 70%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    letter-spacing: -0.5px;
                ">
                    Semantic Talent Intelligence Dashboard
                </h1>
                <p style="
                    color: var(--text-muted);
                    font-size: 15px;
                    max-width: 650px;
                    margin: 0 auto 30px auto;
                    line-height: 1.6;
                ">
                    Accelerate candidate screenings using deep language models. Rank profiles by semantic alignment, map skills coverage gap-matrices, and self-audit hiring processes for demographic proxies.
                </p>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    # 2. Detailed Capability Features (4-Column Layout)
    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)

    with feat_col1:
        st.markdown(
            textwrap.dedent(
                """
                <div style="
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-md);
                    padding: 24px 20px;
                    height: 250px;
                    transition: all 0.3s ease;
                ">
                    <div style="font-size: 28px; margin-bottom: 12px;">🧠</div>
                    <h3 style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">Semantic Similarity</h3>
                    <p style="font-size: 12px; color: var(--text-muted); line-height: 1.5; margin: 0;">
                        Extracts dense vector representations of resumes and spec descriptions. Ranks candidates on conceptual alignment rather than rigid, literal keywords.
                    </p>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    with feat_col2:
        st.markdown(
            textwrap.dedent(
                """
                <div style="
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-md);
                    padding: 24px 20px;
                    height: 250px;
                    transition: all 0.3s ease;
                ">
                    <div style="font-size: 28px; margin-bottom: 12px;">🎯</div>
                    <h3 style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">Skills Gap Maps</h3>
                    <p style="font-size: 12px; color: var(--text-muted); line-height: 1.5; margin: 0;">
                        Auto-extracts JD keywords using spaCy NLP. Classifies profile matching into Present, Absent, and semantically Inferred skill bands with interactive radar maps.
                    </p>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    with feat_col3:
        st.markdown(
            textwrap.dedent(
                """
                <div style="
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-md);
                    padding: 24px 20px;
                    height: 250px;
                    transition: all 0.3s ease;
                ">
                    <div style="font-size: 28px; margin-bottom: 12px;">🛡️</div>
                    <h3 style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">Bias Proxy Guard</h3>
                    <p style="font-size: 12px; color: var(--text-muted); line-height: 1.5; margin: 0;">
                        Detects demographic and institutional bias markers (e.g. Ivy League filters or age years). Highlights rating deltas to ensure objective, fair screenings.
                    </p>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    with feat_col4:
        st.markdown(
            textwrap.dedent(
                """
                <div style="
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-md);
                    padding: 24px 20px;
                    height: 250px;
                    transition: all 0.3s ease;
                ">
                    <div style="font-size: 28px; margin-bottom: 12px;">⚡</div>
                    <h3 style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">High-Speed Cache</h3>
                    <p style="font-size: 12px; color: var(--text-muted); line-height: 1.5; margin: 0;">
                        Saves parsed embeddings as SHA-256 hash-keyed NumPy arrays. Accelerates large bulk-resume re-evaluations under 1 second without reloading weights.
                    </p>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 3. Interactive Getting Started Timeline (Timeline / Progress Flow)
    st.markdown("<h3 style='font-size:18px; font-weight:600; text-align:center;'>Recruitment Workflow Timeline</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px; color:var(--text-muted); text-align:center; margin-bottom:30px;'>Follow these three simple setup gates in the sidebar to populate match logs.</p>", unsafe_allow_html=True)

    timeline_col1, timeline_col2, timeline_col3 = st.columns(3)

    with timeline_col1:
        st.markdown(
            textwrap.dedent(
                """
                <div style="
                    background: rgba(88, 166, 255, 0.03);
                    border-left: 4px solid var(--accent);
                    border-radius: var(--radius-sm);
                    padding: 18px;
                ">
                    <div style="font-size:11px; font-weight:700; color:var(--accent); letter-spacing:0.5px; margin-bottom:4px;">GATE 01</div>
                    <div style="font-size:14px; font-weight:600; color:var(--text-primary); margin-bottom:6px;">Upload Job Specification</div>
                    <div style="font-size:12px; color:var(--text-muted); line-height:1.4;">
                        Upload a job description text file (.txt) or copy and paste the target skill text directly inside the sidebar text area.
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    with timeline_col2:
        st.markdown(
            textwrap.dedent(
                """
                <div style="
                    background: rgba(63, 185, 80, 0.03);
                    border-left: 4px solid var(--accent-green);
                    border-radius: var(--radius-sm);
                    padding: 18px;
                ">
                    <div style="font-size:11px; font-weight:700; color:var(--accent-green); letter-spacing:0.5px; margin-bottom:4px;">GATE 02</div>
                    <div style="font-size:14px; font-weight:600; color:var(--text-primary); margin-bottom:6px;">Upload Resumes & Profiles</div>
                    <div style="font-size:12px; color:var(--text-muted); line-height:1.4;">
                        Select multiple candidate profiles in PDF or Word (.docx) formats. The parsing router will route files and strip headers/footers automatically.
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    with timeline_col3:
        st.markdown(
            textwrap.dedent(
                """
                <div style="
                    background: rgba(163, 113, 247, 0.03);
                    border-left: 4px solid var(--accent-infer);
                    border-radius: var(--radius-sm);
                    padding: 18px;
                ">
                    <div style="font-size:11px; font-weight:700; color:var(--accent-infer); letter-spacing:0.5px; margin-bottom:4px;">GATE 03</div>
                    <div style="font-size:14px; font-weight:600; color:var(--text-primary); margin-bottom:6px;">Launch Match Matrices</div>
                    <div style="font-size:12px; color:var(--text-muted); line-height:1.4;">
                        Set your minimum acceptable fit score threshold, select SBERT encoder models, and hit <strong>Run Analysis</strong> to see interactive match leaderboards.
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )
