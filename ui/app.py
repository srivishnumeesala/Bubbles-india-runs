# Technical Breakdown:
# - Streamlit application entry point.
# - Renders custom styles, page configurations, and initializes sidebar upload grids.
# - Manages central pipeline state inside st.session_state (survives rerun widget changes).
# - Sets up model singletons cached via st.cache_resource and text encoders cached via st.cache_data.
# - Saves uploaded files to settings.RESUME_DIR/JD_DIR, routes parsing, generates embeddings, ranks matching,
#   calculates gaps, runs bias audits, and writes final reports to outputs folder.

import os
import datetime
from pathlib import Path
import streamlit as st
import numpy as np

# 1. Streamlit Page Configuration must be the FIRST call
st.set_page_config(
    page_title="Resume Ranker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load CSS Styles immediately after configuration
css_path = Path(__file__).resolve().parent / "styles.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Path insertion to resolve package imports when run via Streamlit
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Imports from project components
import config.settings as settings
from parsers.file_router import FileRouter
from embeddings.model_loader import get_model
from embeddings.encoder import encode_texts, encode_batch_with_cache
from ranking.similarity import compute_fit_scores
from ranking.gap_analysis import extract_jd_keywords, build_gap_report
from ranking.bias_audit import run_bias_audit
from ranking.report import write_results

from ui.components.uploader import render_sidebar
from ui.components.empty_state import render_empty_state
from ui.components.score_card import render_rankings_tab
from ui.components.compare_view import render_compare_view
from ui.components.export_bar import render_export_bar
from ui.components.bias_panel import render_bias_panel

# 2. Caching Wrappers for Streamlit
@st.cache_resource
def load_cached_model():
    """Cache SBERT model loader resource."""
    return get_model()

@st.cache_data
def cached_encode_texts(texts: list[str]) -> np.ndarray:
    """Cache text encoding outputs for exact match strings."""
    return encode_texts(texts)

# 3. Main Streamlit Logic
def main():
    # Render Sidebar Uploader components
    final_jd, resume_files, model_opt, threshold, run_btn = render_sidebar()

    # Override MODEL_NAME dynamically if user changed it in the sidebar
    if model_opt != settings.MODEL_NAME:
        settings.MODEL_NAME = model_opt
        # Clear lru_cache of get_model so it reloads the new selection
        get_model.cache_clear()

    # Initialize Session State variables
    if "analysis_run" not in st.session_state:
        st.session_state.analysis_run = False
        st.session_state.candidates = []
        st.session_state.raw_resumes = {}
        st.session_state.jd_keywords = {}
        st.session_state.bias_report = None

    # Handle Analysis Execution
    if run_btn:
        if not final_jd:
            st.error("Please provide a Job Description (paste text or upload a .txt file).")
            return
        if not resume_files:
            st.error("Please upload at least one candidate resume (PDF/DOCX).")
            return

        with st.spinner("Analysing candidate resumes..."):
            # Save JD & Resumes to local directories (audit logging)
            saved_paths = []
            for file in resume_files:
                file_path = settings.RESUME_DIR / file.name
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                saved_paths.append(file_path)
                
            jd_path = settings.JD_DIR / "job_description.txt"
            with open(jd_path, "w", encoding="utf-8") as f:
                f.write(final_jd)

            # A. Parsing Phase
            router = FileRouter()
            raw_resumes = router.route_batch(saved_paths)
            
            if not raw_resumes:
                st.error("No resumes were successfully parsed. Check failed_files.log for details.")
                return

            # B. Keyword Extraction Phase
            jd_keywords = extract_jd_keywords(final_jd)

            # C. Embedding Phase
            jd_embedding = cached_encode_texts([final_jd])[0]
            resume_embeddings = encode_batch_with_cache(raw_resumes, settings.CACHE_DIR)

            # D. Scoring & Ranking Phase
            candidates = compute_fit_scores(jd_embedding, resume_embeddings)

            # E. Gap Analysis per Candidate
            for cand in candidates:
                filename = cand.file_path.name
                cand_text = raw_resumes[filename]
                cand_emb = resume_embeddings[filename]
                
                gap_report = build_gap_report(jd_keywords, cand_text, cand_emb)
                cand.gap_report = gap_report

            # F. Bias Audit Correlation
            bias_report = run_bias_audit(candidates, raw_resumes)

            # G. Export Outputs to Disk
            run_ts = datetime.datetime.now().isoformat()
            write_results(candidates, settings.OUTPUT_DIR, run_ts, settings.MODEL_NAME, threshold)

            # Save results to session state
            st.session_state.candidates = candidates
            st.session_state.raw_resumes = raw_resumes
            st.session_state.jd_keywords = jd_keywords
            st.session_state.bias_report = bias_report
            st.session_state.analysis_run = True

            st.toast("Analysis Completed Successfully!", icon="🎯")

    # 4. View Page Rendering
    if st.session_state.analysis_run:
        # Title
        st.markdown("<h2 style='font-weight:700; margin-bottom: 25px;'>🎯 Candidate Match Intelligence</h2>", unsafe_allow_html=True)
        
        # Tabs structure
        tab_rank, tab_comp, tab_export = st.tabs([
            "🎯 Rankings", 
            "👥 Compare Candidates", 
            "💾 Export & Bias Audit"
        ])
        
        with tab_rank:
            render_rankings_tab(
                st.session_state.candidates,
                st.session_state.raw_resumes,
                st.session_state.jd_keywords,
                threshold
            )
            
        with tab_comp:
            render_compare_view(
                st.session_state.candidates,
                st.session_state.jd_keywords
            )
            
        with tab_export:
            render_export_bar(
                st.session_state.candidates,
                settings.MODEL_NAME,
                threshold
            )
            st.markdown("<br><hr style='border-top:1px solid var(--border);'><br>", unsafe_allow_html=True)
            render_bias_panel(st.session_state.bias_report)
    else:
        render_empty_state()

if __name__ == "__main__":
    main()
