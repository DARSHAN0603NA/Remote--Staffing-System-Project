# Remote Staffing AI System

This repository hosts the **Remote Staffing AI System**, a Streamlit experience that ranks open positions against an uploaded resume using embeddings, skill overlap, and seniority checks.

## Highlights
- Snowflake (Snowpark) connector for pulling `JOB_DATA_DEDUPE`.
- Robust preprocessing: HTML cleanup, skill extraction, seniority/experience parsing, and deterministic row identifiers (`RN`).
- Embeddings generated with `sentence-transformers/all-mpnet-base-v2`; NER powered by `dslim/bert-base-NER`.
- Resume pipeline: PDF parsing via `PyPDF2`, keyword+NER skill extraction, transformer embedding.
- Matching logic mixes cosine similarity, skill overlap ratio, and seniority alignment to score jobs, plus quick visualizations (bar chart, radar, CSV export).

## Repo Layout
- `app.py` – Streamlit application.
- `run_debug.py` – optional CLI helper to run the matcher with a sample resume (handy for smoke tests).
- `regen_embeddings.py` – regenerates job embeddings after the RN fix; use if job data changes.
- `requirements.txt` – dependency list.

## Local Setup
1. Create/activate a Python environment:
   ```pwsh
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Run Streamlit:
   ```pwsh
   streamlit run app.py
   ```

### Offline Helpers
- `python regen_embeddings.py` → rebuild job embeddings if the job CSV changes.
- `python run_debug.py` → compute top matches for the bundled sample resume (prints to console).

## Notes
- If Snowflake credentials (configured in `app.py`) fail, the app falls back to `/mnt/data/job_data_preprocessed.csv` and `/mnt/data/job_embeddings.pkl`.
- The first run downloads transformer weights, so expect a longer start-up.
- Plotly charts and the data table now display the job title coming from the job dataset even when duplicate RN values existed.

## Security
Credentials are hard-coded per user request. Rotate/remove before sharing outside your trusted environment.

## Future Ideas
- Async/background embedding refresh.
- Persist regenerated embeddings back to Snowflake (`JOB_EMBEDDINGS`).
- Expand the `TECH_SKILLS` lexicon with curated domain skills.

Enjoy matching! — Remote Staffing AI System
