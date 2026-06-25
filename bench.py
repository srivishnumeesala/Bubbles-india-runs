# Technical Breakdown:
# - Performance benchmarking script.
# - Benchmarks cold model load time.
# - Benchmarks batch sentence encoding (50 sample texts).
# - Benchmarks similarity matching calculations (50 candidates).
# - Benchmarks full end-to-end pipeline ingestion to report writing (10 candidate resumes).
# - Outputs data in a clean Markdown table format.

import time
import shutil
import tempfile
from pathlib import Path
import numpy as np

def run_benchmarks():
    print("Starting Performance Benchmarks...")
    results = []

    # 1. Cold Model Load Time
    # Clean model cache first to ensure it's a cold load (uncached)
    from embeddings.model_loader import get_model
    get_model.cache_clear()
    
    start_time = time.time()
    model = get_model()
    cold_load_time = time.time() - start_time
    results.append({
        "operation": "Model Load Time (Cold)",
        "time_seconds": f"{cold_load_time:.4f}",
        "notes": f"Initial weight loading of SBERT model: {model.get_max_seq_length()} max seq length."
    })
    print(f"Cold model load: {cold_load_time:.4f}s")

    # 2. Batch Encoding (50 sample texts)
    from embeddings.encoder import encode_texts
    sample_texts = [
        f"Experienced engineer {i} working with Python, PyTorch, machine learning, and cloud infrastructure."
        for i in range(50)
    ]
    
    start_time = time.time()
    embeddings = encode_texts(sample_texts, batch_size=32)
    encode_time = time.time() - start_time
    results.append({
        "operation": "Batch Encoding (50 texts)",
        "time_seconds": f"{encode_time:.4f}",
        "notes": f"Batch size=32. Matrix size: {embeddings.shape}."
    })
    print(f"Batch encode 50 texts: {encode_time:.4f}s")

    # 3. Similarity Scorer (50 candidates)
    from ranking.similarity import compute_fit_scores
    jd_vector = encode_texts(["Senior Python Developer specializing in PyTorch"])[0]
    resume_embeddings = {f"candidate_{i}.pdf": vec for i, vec in enumerate(embeddings)}
    
    start_time = time.time()
    candidates = compute_fit_scores(jd_vector, resume_embeddings)
    similarity_time = time.time() - start_time
    results.append({
        "operation": "Similarity Matching (50 candidates)",
        "time_seconds": f"{similarity_time:.4f}",
        "notes": f"Matrix-based dot products and sorting."
    })
    print(f"Similarity match 50 candidates: {similarity_time:.4f}s")

    # 4. Full Pipeline Ingestion to Report (10 resumes)
    from config.settings import RESUME_DIR, OUTPUT_DIR, CACHE_DIR
    from parsers.file_router import FileRouter
    from ranking.gap_analysis import extract_jd_keywords, build_gap_report
    from ranking.bias_audit import run_bias_audit
    from ranking.report import write_results

    # Generate 10 temp resumes by copying our generated ones
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_resume = RESUME_DIR / "priya_sharma.docx"
        
        # If the file does not exist, check alex_johnson
        if not source_resume.exists():
            source_resume = RESUME_DIR / "alex_johnson.docx"

        temp_resumes = []
        for i in range(10):
            target = temp_path / f"benchmark_candidate_{i}.docx"
            shutil.copy(source_resume, target)
            temp_resumes.append(target)

        # Time the full pipeline
        start_time = time.time()
        
        # Ingest/Parse
        router = FileRouter()
        raw_resumes = router.route_batch(temp_resumes)
        
        # JD Keywords
        jd_text = "We need Python, SQL, PyTorch and Docker skills. AWS is a plus."
        jd_keywords = extract_jd_keywords(jd_text)
        
        # Embed
        jd_emb = encode_texts([jd_text])[0]
        # Skip cache to measure raw computation time
        resume_embs = {}
        for filename, text in raw_resumes.items():
            resume_embs[filename] = encode_texts([text])[0]
            
        # Rank
        candidates = compute_fit_scores(jd_emb, resume_embs)
        
        # Gap analysis
        for cand in candidates:
            filename = cand.file_path.name
            cand.gap_report = build_gap_report(jd_keywords, raw_resumes[filename], resume_embs[filename])
            
        # Bias audit
        bias_report = run_bias_audit(candidates, raw_resumes)
        
        # Exporter
        csv_p, json_p = write_results(candidates, OUTPUT_DIR, "benchmark_run", "all-MiniLM-L6-v2", 60.0)
        
        # Clean benchmark outputs
        if csv_p.exists(): csv_p.unlink()
        if json_p.exists(): json_p.unlink()

        pipeline_time = time.time() - start_time
        results.append({
            "operation": "E2E Pipeline Ingestion (10 Resumes)",
            "time_seconds": f"{pipeline_time:.4f}",
            "notes": f"Parse -> Embed -> Similarity -> Gaps -> Bias Audit -> Export."
        })
        print(f"E2E Pipeline 10 resumes: {pipeline_time:.4f}s")

    # Generate Markdown Output
    print("\nBenchmark results table:")
    print("| Operation | Time (Seconds) | Notes |")
    print("| --- | --- | --- |")
    for r in results:
        print(f"| {r['operation']} | {r['time_seconds']} | {r['notes']} |")

if __name__ == "__main__":
    run_benchmarks()
