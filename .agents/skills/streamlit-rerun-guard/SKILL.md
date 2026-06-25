---
name: streamlit-rerun-guard
description: Guards against reload/rerun issues inside Streamlit applications.
---
# Streamlit Rerun Guard Skill

## Instructions
1. Never import or call code that performs expensive setup (like loading SBERT models) at module level without caching.
2. Use `st.cache_resource` for SBERT model loaders (singletons) to ensure they are loaded only once per session.
3. Use `st.cache_data` for data-heavy functions like text encoding, file reading, and parsing where inputs and outputs are serializable.
4. Wrap all Streamlit page configuration (`st.set_page_config()`) as the absolute first Streamlit command in the entry-point file.
5. All file I/O operations triggered inside Streamlit callbacks or blocks must be wrapped in robust `try...except` blocks with logging.
