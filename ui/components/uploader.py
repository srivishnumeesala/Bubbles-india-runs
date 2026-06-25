# Technical Breakdown:
# - Renders the left sidebar control panel for user uploads and parameters.
# - Provides two input modes for job descriptions: direct copy-paste or text file uploads.
# - Facilitates bulk resume loading with multi-select drag-and-drop.
# - Sets threshold variables and model choices, returning them to the main application block.

import streamlit as st
from typing import List, Tuple

def render_sidebar():
    """Render the sidebar upload widgets and controls.

    Returns:
        Tuple[str, List, str, float, bool]:
            - final_jd (str): Job description text.
            - resume_files (List[UploadedFile]): List of uploaded resume files.
            - model_opt (str): Selected SBERT model name.
            - threshold (float): Target fit threshold.
            - run_btn (bool): Trigger state of the analysis button.
    """
    st.sidebar.markdown("# 🎯 Resume Ranker")
    st.sidebar.markdown("<span style='color: var(--text-muted); font-size:14px;'>Semantic talent matching platform</span>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # 1. Job Description Ingestion
    st.sidebar.subheader("📄 Job Description")
    jd_file = st.sidebar.file_uploader("Upload JD (.txt)", type=["txt"])
    jd_text = st.sidebar.text_area("Or paste JD text here:", height=150)

    # 2. Resumes Ingestion
    st.sidebar.subheader("👥 Candidate Resumes")
    resume_files = st.sidebar.file_uploader(
        "Upload PDF/DOCX resumes", 
        type=["pdf", "docx"], 
        accept_multiple_files=True,
        help="Select multiple resumes to rank them in batch."
    )

    # 3. Model Configuration
    st.sidebar.subheader("🤖 Model Selection")
    model_opt = st.sidebar.selectbox(
        "Model Name", 
        ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "all-distilroberta-v1"], 
        index=0
    )

    # 4. Fit Threshold Config
    st.sidebar.subheader("🎚 Similarity Threshold")
    threshold = st.sidebar.slider(
        "Minimum Fit Score", 
        min_value=0.0, 
        max_value=100.0, 
        value=60.0, 
        step=5.0,
        help="Scores below this are flagged as weak fit."
    )
    
    st.sidebar.markdown("---")
    run_btn = st.sidebar.button("🚀 Run Analysis", use_container_width=True, type="primary")

    # Ingestion check
    final_jd = ""
    if jd_file is not None:
        try:
            final_jd = jd_file.read().decode("utf-8", errors="ignore").strip()
        except Exception as e:
            st.sidebar.error(f"Failed to read JD file: {str(e)}")
    elif jd_text:
        final_jd = jd_text.strip()

    return final_jd, resume_files or [], model_opt, threshold, run_btn
