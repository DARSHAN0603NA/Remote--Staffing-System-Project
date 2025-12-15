import os
import re
import io
import time
import base64
import pickle
from typing import List, Tuple, Dict, Any

import pandas as pd
import numpy as np
from tqdm.auto import tqdm

import streamlit as st
from PyPDF2 import PdfReader

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from transformers import pipeline

import plotly.express as px
import plotly.graph_objects as go

try:
    from snowflake.snowpark import Session
except Exception:
    Session = None

# Set HuggingFace API token (if you have one)
os.environ.setdefault("HF_TOKEN", "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")

# -----------------------------
# Configuration / Constants
# -----------------------------
CONN_PARAMS = {

    "ACCOUNT": "ELAGUFK-SC82128",
    "USER": "TANISHAKS03",
    "PASSWORD": "Tani@SNOW0306##",
    "ROLE": "ACCOUNTADMIN",
    "WAREHOUSE": "COMPUTE_WH",
    "DATABASE": "JOB_PORTAL_DB",
    "SCHEMA": "CLEAN"    
}


DATA_DIR = "/mnt/data"
os.makedirs(DATA_DIR, exist_ok=True)

PREPROCESSED_CSV = os.path.join(DATA_DIR, "job_data_preprocessed.csv")
EMBEDDINGS_PKL = os.path.join(DATA_DIR, "job_embeddings.pkl")
EMBEDDINGS_CSV = os.path.join(DATA_DIR, "job_embeddings.csv")

EMBED_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
NER_MODEL = "dslim/bert-base-NER"

TECH_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "nosql",
    "aws", "azure", "gcp", "docker", "kubernetes", "react", "angular", "vue",
    "node.js", "node", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "spark", "hadoop", "tableau", "powerbi", "excel", "git", "rest api", "graphql",
]

# -----------------------------
# Utility: Snowflake session
# -----------------------------
def create_snowflake_session(params: Dict[str, str]):
    if Session is None:
        return None
    try:
        cfg = {
            "account": params["ACCOUNT"],
            "user": params["USER"],
            "password": params["PASSWORD"],
            "role": params["ROLE"],
            "warehouse": params["WAREHOUSE"],
            "database": params["DATABASE"],
            "schema": params["SCHEMA"],
        }
        return Session.builder.configs(cfg).create()
    except Exception as e:
        print("Snowflake session creation failed:", e)
        return None


# -----------------------------
# Data cleaning & preprocessing
# -----------------------------
def clean_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"<br\s*/?>", " \n", text, flags=re.I)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def ensure_stable_rn(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure there's a stable unique RN column for each row:
      1. If 'RN' exists, keep it as str.
      2. Else if common id columns exist (JOB_ID/ID/ROW_ID/UNIQUE_ID), use first one.
      3. Else generate a stable RN using index + hash of row (deterministic across runs).
    """
    df = df.copy()

    # If RN exists, cast to str and keep it -- but ensure uniqueness
    if "RN" in df.columns and not df["RN"].isnull().all():
        df["RN"] = df["RN"].astype(str)
        # Force uniqueness to avoid overwriting embeddings/matches
        duplicated = df["RN"].duplicated(keep=False)
        if duplicated.any():
            df.loc[duplicated, "RN"] = (
                df.loc[duplicated, "RN"]
                + "_"
                + df.loc[duplicated].index.astype(str)
            )
        return df

    # Preferred candidate id columns
    candidate_cols = ["JOB_ID", "ID", "JOBID", "ROW_ID", "ROWNUMBER", "ROW_NUMBER", "UNIQUE_ID", "_ID"]
    for c in candidate_cols:
        if c in df.columns:
            df["RN"] = df[c].astype(str)
            return df

    # No ID available — build deterministic RN using hash_pandas_object
    try:
        # Use pandas hashing of the full row to create a stable ID
        row_hash = pd.util.hash_pandas_object(df.apply(lambda r: r.astype(str), axis=1), index=True)
        df["RN"] = (df.index.astype(str) + "_" + row_hash.astype(str))
    except Exception:
        # fallback: index only (less ideal but deterministic in a single run)
        df["RN"] = df.index.astype(str)

    df["RN"] = df["RN"].astype(str)
    return df


def fill_missing_job_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    expected = [
        "COMPANY_NAME", "INDUSTRY", "HQ_LOCATION", "JOB_LOCATION", "COMPANY_SIZE",
        "POSTER_NAME", "POSTER_ROLE", "POSTER_EMAIL", "POSTER_PHONE", "JOB_TITLE",
        "ROLES_AND_RESPONSIBILITIES", "REQUIRED_QUALIFICATIONS", "SKILLS", "EXPERIENCE_REQUIRED",
        "EMPLOYMENT_TYPE", "SALARY_MIN", "SALARY_MAX", "SALARY_CURRENCY", "SALARY_RANGE",
        "HIRING_DEADLINE", "SOURCE", "LOAD_TIME", "RN"
    ]
    for c in expected:
        if c not in df.columns:
            df[c] = ""
    df["RN"] = df["RN"].astype(str)
    text_cols = [c for c in expected if c not in ("SALARY_MIN", "SALARY_MAX")]
    for c in text_cols:
        df[c] = df[c].fillna("").astype(str)
    for s in ("SALARY_MIN", "SALARY_MAX"):
        if s in df.columns:
            df[s] = pd.to_numeric(df[s], errors="coerce")
            median_val = df[s].median()
            if pd.notna(median_val):
                df[s] = df[s].fillna(median_val)
            else:
                df[s] = df[s].fillna(0)
    for s in ("SALARY_CURRENCY", "SALARY_RANGE"):
        if s in df.columns:
            df[s] = df[s].fillna("").astype(str)
            df[s] = df[s].replace("", np.nan).bfill().fillna("")
    # backfills using CLEAN_* if present
    if "CLEAN_JOB_TITLE" in df.columns:
        mask = df["JOB_TITLE"].fillna("").str.strip() == ""
        if mask.any():
            df.loc[mask, "JOB_TITLE"] = df.loc[mask, "CLEAN_JOB_TITLE"].fillna("")
    if "ROLES_AND_RESPONSIBILITIES" in df.columns:
        mask = df["ROLES_AND_RESPONSIBILITIES"].fillna("").str.strip() == ""
        if "CLEAN_RR" in df.columns and mask.any():
            df.loc[mask, "ROLES_AND_RESPONSIBILITIES"] = df.loc[mask, "CLEAN_RR"].fillna("")
            mask = df["ROLES_AND_RESPONSIBILITIES"].fillna("").str.strip() == ""
        if "RR" in df.columns and mask.any():
            df.loc[mask, "ROLES_AND_RESPONSIBILITIES"] = df.loc[mask, "RR"].fillna("")
    if "REQUIRED_QUALIFICATIONS" in df.columns:
        mask = df["REQUIRED_QUALIFICATIONS"].fillna("").str.strip() == ""
        if "CLEAN_QUAL" in df.columns and mask.any():
            df.loc[mask, "REQUIRED_QUALIFICATIONS"] = df.loc[mask, "CLEAN_QUAL"].fillna("")
            mask = df["REQUIRED_QUALIFICATIONS"].fillna("").str.strip() == ""
        if "QUAL" in df.columns and mask.any():
            df.loc[mask, "REQUIRED_QUALIFICATIONS"] = df.loc[mask, "QUAL"].fillna("")
    def _skills_to_str(x):
        if isinstance(x, (list, tuple)):
            return ", ".join([str(v) for v in x if str(v).strip()])
        return str(x) if x and str(x).strip() else ""
    if "SKILLS" in df.columns:
        mask = df["SKILLS"].fillna("").str.strip() == ""
        if mask.any() and "SKILLS_FINAL" in df.columns:
            df.loc[mask, "SKILLS"] = df.loc[mask, "SKILLS_FINAL"].apply(_skills_to_str)
            mask = df["SKILLS"].fillna("").str.strip() == ""
        if mask.any() and "SKILLS_RAW" in df.columns:
            df.loc[mask, "SKILLS"] = df.loc[mask, "SKILLS_RAW"].fillna("")
    if "EXPERIENCE_REQUIRED" in df.columns and "EXP_YEARS" in df.columns:
        mask = df["EXPERIENCE_REQUIRED"].fillna("").str.strip() == ""
        if mask.any():
            df.loc[mask, "EXPERIENCE_REQUIRED"] = df.loc[mask, "EXP_YEARS"].fillna("")
    if "JOB_LOCATION" in df.columns:
        mask = df["JOB_LOCATION"].fillna("").str.strip() == ""
        if mask.any() and "LOCATION" in df.columns:
            df.loc[mask, "JOB_LOCATION"] = df.loc[mask, "LOCATION"].fillna("")
            mask = df["JOB_LOCATION"].fillna("").str.strip() == ""
        if mask.any() and "HQ_LOCATION" in df.columns:
            df.loc[mask, "JOB_LOCATION"] = df.loc[mask, "HQ_LOCATION"].fillna("")
    if "LOAD_TIME" in df.columns:
        mask = df["LOAD_TIME"].fillna("").str.strip() == ""
        if mask.any():
            now = pd.Timestamp.now().isoformat()
            df.loc[mask, "LOAD_TIME"] = now
    return df


def extract_skills_from_text(text: str, skills_list: List[str] = TECH_SKILLS) -> List[str]:
    found = set()
    text_low = (text or "").lower()
    for skill in skills_list:
        if skill.lower() in text_low:
            found.add(skill.lower())
    tokens = re.findall(r"[A-Za-z+#+\.]{2,}", text)
    for t in tokens:
        tl = t.lower()
        if tl in text_low and len(tl) <= 20 and any(ch.isalpha() for ch in tl):
            if tl not in found and tl in skills_list:
                found.add(tl)
    return sorted(found)


def extract_seniority(text: str) -> str:
    if not isinstance(text, str):
        return "unknown"
    text = text.lower()
    if re.search(r"\bintern\b", text):
        return "intern"
    if re.search(r"\bjunior\b|\bjr\b", text):
        return "junior"
    if re.search(r"\bmid\b|\bmid[- ]level\b|\bassociate\b", text):
        return "mid"
    if re.search(r"\bsenior\b|\bsr\b", text):
        return "senior"
    if re.search(r"\bmanager\b|\blead\b|\bdirector\b", text):
        return "manager"
    return "unknown"


def extract_experience_years(text: str) -> str:
    if not isinstance(text, str):
        return ""
    m = re.search(r"(\d+(?:\.\d+)?\+?)\s*(?:years|yrs)", text.lower())
    return m.group(1) if m else ""


def preprocess_jobs(df: pd.DataFrame) -> pd.DataFrame:
    # Convert Snowpark DF to pandas if needed
    if not isinstance(df, pd.DataFrame):
        df = df.to_pandas() if hasattr(df, "to_pandas") else pd.DataFrame(df)
    df = df.copy()

    # Ensure stable RN
    df = ensure_stable_rn(df)

    # Create cleaned columns (defensive presence checks)
    if "JOB_TITLE" in df.columns:
        df["CLEAN_JOB_TITLE"] = df["JOB_TITLE"].fillna("").astype(str).apply(clean_html)
    else:
        df["CLEAN_JOB_TITLE"] = ""
    if "RR" in df.columns:
        df["CLEAN_RR"] = df["RR"].fillna("").astype(str).apply(clean_html)
    else:
        df["CLEAN_RR"] = ""
    if "QUAL" in df.columns:
        df["CLEAN_QUAL"] = df["QUAL"].fillna("").astype(str).apply(clean_html)
    else:
        df["CLEAN_QUAL"] = ""
    if "SKILLS" in df.columns:
        df["SKILLS_RAW"] = df["SKILLS"].fillna("").astype(str)
    else:
        df["SKILLS_RAW"] = ""

    # Extract skills
    df["SKILLS_LIST"] = df["SKILLS_RAW"].apply(lambda t: extract_skills_from_text(t))
    df["SKILLS_CLEAN_STR"] = df["SKILLS_LIST"].apply(lambda l: ", ".join(l))

    df["TEXT_FOR_SKILLS"] = (
        df["CLEAN_JOB_TITLE"] + " \n" + df["CLEAN_RR"] + " \n" + df["CLEAN_QUAL"] + " \n" + df["SKILLS_RAW"]
    )
    df["SKILLS_FROM_TEXT"] = df["TEXT_FOR_SKILLS"].apply(lambda t: extract_skills_from_text(t))
    df["SKILLS_FINAL"] = df.apply(lambda r: sorted(set(r["SKILLS_LIST"]) | set(r["SKILLS_FROM_TEXT"])), axis=1)

    # Seniority & experience
    df["SENIORITY"] = df["TEXT_FOR_SKILLS"].apply(extract_seniority)
    df["EXP_YEARS"] = df["TEXT_FOR_SKILLS"].apply(extract_experience_years)

    # Compose clean text used for embeddings
    df["CLEAN_TEXT"] = (
        df["CLEAN_JOB_TITLE"].fillna("") + " \n" +
        df["CLEAN_RR"].fillna("") + " \n" +
        df["CLEAN_QUAL"].fillna("") + " \nSkills: " +
        df["SKILLS_FINAL"].apply(lambda l: ", ".join(l))
    ).apply(lambda t: re.sub(r"\s+", " ", str(t)).strip())

    return df


# -----------------------------
# Embeddings: generate/save/load
# -----------------------------
def generate_and_store_embeddings(df: pd.DataFrame, model: SentenceTransformer):
    # df must already have stable RN and CLEAN_TEXT
    texts = df["CLEAN_TEXT"].fillna("").tolist()
    rns = df["RN"].astype(str).tolist()
    print(f"DEBUG: Generating embeddings for {len(texts)} jobs...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    print("DEBUG: embeddings generated")

    emb_df = pd.DataFrame({"RN": [str(x) for x in rns]})
    emb_df = emb_df.reset_index(drop=True)
    emb_df["embedding"] = [np.array(e, dtype=float) for e in embeddings]

    # Save pickle
    with open(EMBEDDINGS_PKL, "wb") as f:
        pickle.dump(emb_df, f)
    # Save CSV (embedding_str)
    emb_df_csv = emb_df.copy()
    emb_df_csv["embedding_str"] = emb_df_csv["embedding"].apply(lambda e: ",".join([str(x) for x in e.tolist()]))
    emb_df_csv.drop(columns=["embedding"], inplace=True)
    emb_df_csv.to_csv(EMBEDDINGS_CSV, index=False)

    print(f"DEBUG: Saved embeddings (count={len(emb_df)})")
    return emb_df


def load_embeddings():
    """
    Load embeddings from pickle first, else CSV. Normalize into DataFrame with
    columns ['RN', 'embedding' (ndarray)].
    """
    emb_df = None
    if os.path.exists(EMBEDDINGS_PKL):
        try:
            with open(EMBEDDINGS_PKL, "rb") as f:
                emb_df = pickle.load(f)
            # Ensure RN str and embedding ndarray
            emb_df = emb_df.copy()
            emb_df["RN"] = emb_df["RN"].astype(str)
            # If embedding is stored as list/object convert to ndarray
            def _to_arr(x):
                if x is None:
                    return None
                if isinstance(x, np.ndarray):
                    return x.astype(float)
                if isinstance(x, (list, tuple)):
                    return np.array(x, dtype=float)
                # fallback if pickled as string
                if isinstance(x, str):
                    return np.array([float(v) for v in x.split(",")], dtype=float)
                return np.array(x, dtype=float)
            emb_df["embedding"] = emb_df["embedding"].apply(_to_arr)
            print(f"DEBUG: Loaded embeddings from pickle ({len(emb_df)} rows)")
            return emb_df
        except Exception as e:
            print("DEBUG: Failed to load pickle embeddings:", e)
            emb_df = None

    if os.path.exists(EMBEDDINGS_CSV):
        try:
            emb_df = pd.read_csv(EMBEDDINGS_CSV)
            emb_df["RN"] = emb_df["RN"].astype(str)
            # reconstruct embedding array
            emb_df["embedding"] = emb_df["embedding_str"].apply(lambda s: np.array([float(x) for x in str(s).split(",")], dtype=float) if pd.notna(s) and s != "" else None)
            print(f"DEBUG: Loaded embeddings from CSV ({len(emb_df)} rows)")
            return emb_df
        except Exception as e:
            print("DEBUG: Failed to load CSV embeddings:", e)
            emb_df = None

    return None


# -----------------------------
# Matching functions
# -----------------------------
def skill_score(job_skills: List[str], resume_skills: List[str]) -> float:
    if not isinstance(job_skills, (list, tuple)) or not job_skills:
        return 0.0
    if not isinstance(resume_skills, (list, tuple)) or not resume_skills:
        return 0.0
    inter = set([s.lower() for s in job_skills]) & set([s.lower() for s in resume_skills])
    return len(inter) / max(1, len(set([s.lower() for s in job_skills])))


def seniority_match(job_sen: str, resume_sen: str) -> float:
    if not job_sen or not resume_sen:
        return 0.0
    job_sen = (job_sen or "").lower()
    resume_sen = (resume_sen or "").lower()
    if job_sen == "unknown" or resume_sen == "unknown":
        return 0.0
    if job_sen == resume_sen:
        return 1.0
    hierarchy = ["intern", "junior", "mid", "senior", "manager"]
    try:
        jidx = hierarchy.index(job_sen)
        ridx = hierarchy.index(resume_sen)
        dist = abs(jidx - ridx)
        return max(0.0, 1.0 - (dist / (len(hierarchy) - 1)))
    except ValueError:
        return 0.0


def match_score(cos_sim: float, skill_ov: float, senior: float) -> float:
    final = 0.75 * cos_sim + 0.20 * skill_ov + 0.05 * senior
    return float(final)


def extract_text_from_pdf(file_stream) -> str:
    try:
        reader = PdfReader(file_stream)
        texts = []
        for p in reader.pages:
            try:
                t = p.extract_text() or ""
            except Exception:
                t = ""
            texts.append(t)
        return "\n".join(texts)
    except Exception as e:
        print("PDF read error:", e)
        return ""


def extract_resume_skills_via_ner(text: str, ner_pipeline) -> List[str]:
    try:
        entities = ner_pipeline(text[:10000])
        found = set()
        for ent in entities:
            w = ent.get("word", "").lower()
            if len(w) > 1:
                found.add(w)
        return sorted(found)
    except Exception as e:
        print(f"NER extraction error: {e}")
        return []


def run_matching_pipeline(resume_embedding: np.ndarray, resume_skills: List[str], resume_sen: str,
                          jobs_df: pd.DataFrame, emb_df: pd.DataFrame) -> pd.DataFrame:
    # Build emb_map from emb_df (RN -> ndarray)
    emb_map = {}
    for _, row in emb_df.iterrows():
        rn = str(row["RN"])
        emb = row.get("embedding")
        if emb is None:
            continue
        if isinstance(emb, str):
            try:
                emb = np.array([float(x) for x in emb.split(",")], dtype=float)
            except Exception:
                continue
        else:
            emb = np.array(emb, dtype=float)
        emb_map[rn] = emb

    results = []
    missing_count = 0
    for _, job in jobs_df.iterrows():
        rn = str(job["RN"])
        job_emb = emb_map.get(rn)
        if job_emb is None:
            missing_count += 1
            continue
        try:
            cos = float(cosine_similarity([resume_embedding], [job_emb])[0][0])
        except Exception as e:
            print(f"DEBUG: Cosine sim error for RN {rn}: {e}")
            continue
        sk_score = skill_score(job.get("SKILLS_FINAL", []), resume_skills)
        sen = seniority_match(job.get("SENIORITY", "unknown"), resume_sen)
        final = match_score(cos, sk_score, sen)
        results.append({
            "RN": rn,
            "JOB_TITLE": job.get("JOB_TITLE", "") if "JOB_TITLE" in job else job.get("CLEAN_JOB_TITLE", ""),
            "COMPANY_NAME": job.get("COMPANY_NAME", "") if "COMPANY_NAME" in job else job.get("COMPANY", ""),
            "LOCATION": job.get("JOB_LOCATION", "") if "JOB_LOCATION" in job else job.get("LOCATION", ""),
            "cosine_sim": cos,
            "skill_overlap": sk_score,
            "seniority": sen,
            "MATCH_SCORE": final,
        })
    print(f"DEBUG: Missing embeddings for {missing_count} jobs (out of {len(jobs_df)})")
    res_df = pd.DataFrame(results)
    if len(res_df) > 0:
        res_df = res_df.sort_values("MATCH_SCORE", ascending=False).reset_index(drop=True)
    return res_df


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Job Matcher", layout="wide", initial_sidebar_state="expanded")

def gradient_header():
    st.markdown(
        """
        <div style="padding:20px;border-radius:12px;background:linear-gradient(90deg,#a7f3d0,#c7b8ff);">
            <h1 style="margin:0;padding:0;font-family:Inter, sans-serif;color:#0f172a">Remote Staffing AI System</h1>
            <p style="margin:0;color:#0f172a;opacity:0.9">Upload your resume and discover top job matches with embeddings + skill extraction.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def sidebar_instructions():
    st.sidebar.markdown("**Instructions**")
    st.sidebar.write("1. Upload a PDF resume.\n2. Wait while the app extracts skills and matches jobs.\n3. Explore charts and download results.")

def main():
    gradient_header()
    sidebar_instructions()

    col1, col2 = st.columns([2, 3])

    with col1:
        st.header("Resume")
        uploaded = st.file_uploader("Upload your resume (PDF)", type=["pdf"])    
        st.write("Or use the sample resume included in the repo (if available).")

    with col2:
        st.header("Data & Model")
        st.write("This app will attempt to connect to Snowflake to fetch `JOB_DATA_DEDUPE`. If that fails it will look for local preprocessed files.")

    # Connect to Snowflake (try)
    session = None
    try:
        with st.spinner("Connecting to Snowflake (Snowpark)..."):
            session = create_snowflake_session(CONN_PARAMS)
            time.sleep(0.2)
    except Exception:
        session = None

    jobs_df = None
    emb_df = None

    # Load jobs from Snowflake if session available
    if session is not None:
        try:
            with st.spinner("Loading JOB_DATA_DEDUPE from Snowflake..."):
                query = "SELECT * FROM JOB_PORTAL_DB.CLEAN.JOB_DATA_DEDUPE"
                df_sf = session.sql(query).to_pandas()
                st.write(f"**Fetched {len(df_sf)} rows** from Snowflake.")
                jobs_df = preprocess_jobs(df_sf)
                # Fill missing fields (non-fatal)
                try:
                    jobs_df = fill_missing_job_fields(jobs_df)
                except Exception:
                    pass
                jobs_df.to_csv(PREPROCESSED_CSV, index=False)
                st.success(f"Loaded and preprocessed job data ({len(jobs_df)} rows).")
        except Exception as e:
            st.warning(f"Snowflake load failed: {e}. Trying local files...")

    # If Snowflake failed or offline, try local preprocessed CSV
    if jobs_df is None and os.path.exists(PREPROCESSED_CSV):
        jobs_df = pd.read_csv(PREPROCESSED_CSV)
        # Reconstruct list columns
        if "SKILLS_FINAL" in jobs_df.columns:
            jobs_df["SKILLS_FINAL"] = jobs_df["SKILLS_FINAL"].fillna("").apply(lambda s: [x.strip() for x in str(s).split(",") if x.strip()])
        try:
            jobs_df = fill_missing_job_fields(jobs_df)
        except Exception:
            pass
        # Ensure stable RN
        jobs_df = ensure_stable_rn(jobs_df)
        st.info("Loaded preprocessed job data from local CSV.")

    # Load embeddings if present
    emb_df = load_embeddings()
    if emb_df is not None:
        st.info(f"Loaded {len(emb_df)} embeddings from disk.")

    # If jobs exist but embedding count or RN set mismatch, force regenerate
    if jobs_df is not None and emb_df is not None:
        # quick checks
        emb_rns = set(emb_df["RN"].astype(str).tolist())
        jobs_rns = set(jobs_df["RN"].astype(str).tolist())
        if len(emb_df) != len(jobs_df) or emb_rns != jobs_rns:
            st.warning("Embeddings appear out-of-sync with job data (count/IDs mismatch). They will be regenerated.")
            emb_df = None

    # If embeddings missing and jobs present, generate them
    model = None
    if emb_df is None and jobs_df is not None:
        with st.spinner("Loading embedding model and computing embeddings (this may take a while)…"):
            model = SentenceTransformer(EMBED_MODEL_NAME, token=os.environ.get("HF_TOKEN"))
            emb_df = generate_and_store_embeddings(jobs_df, model)
            st.success("Generated and saved embeddings.")
    else:
        # load model lazily if needed later
        pass

    # Initialize NER pipeline lazily when resume uploaded
    ner_pipe = None

    # Process uploaded resume
    if uploaded is not None:
        with st.spinner("Extracting resume text..."):
            raw_text = extract_text_from_pdf(uploaded)
            clean_resume_text = clean_html(raw_text).lower()
            st.success("Extracted resume text.")

        kw_skills = extract_skills_from_text(clean_resume_text)

        with st.spinner("Running NER on resume (may take a few seconds)..."):
            try:
                ner_pipe = pipeline("ner", model=NER_MODEL, grouped_entities=True, token=os.environ.get("HF_TOKEN"))
                ner_skills = extract_resume_skills_via_ner(clean_resume_text, ner_pipe)
            except Exception as e:
                st.warning(f"NER pipeline failed: {e}")
                ner_skills = []

        resume_skills = sorted(set(kw_skills + ner_skills))
        st.subheader("Extracted Skills")
        if resume_skills:
            st.write(", ".join(resume_skills))
        else:
            st.write("No skills detected via keyword/NER heuristics.")

        resume_sen = extract_seniority(clean_resume_text)
        resume_exp = extract_experience_years(clean_resume_text)
        st.write(f"**Seniority:** {resume_sen} — **Experience:** {resume_exp}")

        with st.spinner("Encoding resume..."):
            if model is None:
                model = SentenceTransformer(EMBED_MODEL_NAME, token=os.environ.get("HF_TOKEN"))
            resume_emb = model.encode([clean_resume_text], convert_to_numpy=True)[0]
            st.success("Resume encoded.")

        # -----------------------------
        # Run matching (robust & fixed)
        # -----------------------------
        if jobs_df is not None and emb_df is not None:
            with st.spinner("Computing matches..."):
                # Re-check emb_df/jobs_df alignment just before matching
                emb_rns = set(emb_df["RN"].astype(str).tolist())
                jobs_rns = set(jobs_df["RN"].astype(str).tolist())
                if len(emb_df) != len(jobs_df) or emb_rns != jobs_rns:
                    st.warning("Embeddings stale — rebuilding to match job data.")
                    # regenerate
                    model = SentenceTransformer(EMBED_MODEL_NAME, token=os.environ.get("HF_TOKEN"))
                    emb_df = generate_and_store_embeddings(jobs_df, model)
                    st.success("Embeddings rebuilt.")

                results_df = run_matching_pipeline(resume_emb, resume_skills, resume_sen, jobs_df, emb_df)

                if results_df is None or len(results_df) == 0:
                    st.error("No matching results found. (Check RN or embeddings mismatch.)")
                    # Debug prints
                    print(f"DEBUG: emb_df rows={len(emb_df) if emb_df is not None else 'None'}")
                    print(f"DEBUG: jobs_df rows={len(jobs_df) if jobs_df is not None else 'None'}")
                    st.stop()

                st.write(f"**Total matching results computed:** {len(results_df)}")
                if len(results_df) > 0:
                    st.write(f"**Top match score:** {results_df.iloc[0]['MATCH_SCORE']:.4f}")

                # Prepare topN (do NOT drop duplicates by RN — we want similar jobs to appear)
                topN = results_df.copy().head(10).reset_index(drop=True)

                # Add match strength category
                def cat_score(x):
                    if x >= 0.8:
                        return "Excellent"
                    if x >= 0.6:
                        return "Good"
                    if x >= 0.4:
                        return "Fair"
                    return "Low"

                topN["Match_Strength"] = topN["MATCH_SCORE"].apply(cat_score)

                st.success("Matching complete.")

                # Charts
                st.subheader("Match Score Distribution (Top 50)")
                sample = results_df.head(50)
                fig = px.bar(sample, x=sample.index, y="MATCH_SCORE", color="MATCH_SCORE", color_continuous_scale="Tealrose")
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Top 10 — Key Columns")
                topN["RN"] = topN["RN"].astype(str)
                jobs_df["RN"] = jobs_df["RN"].astype(str)
                full_topN = topN.merge(jobs_df, on="RN", how="left", suffixes=("_match", ""))
                selected_cols = [
                    "RN",
                    "JOB_TITLE",
                    "COMPANY_NAME",
                    "JOB_LOCATION",
                    "HQ_LOCATION",
                    "MATCH_SCORE",
                    "cosine_sim",
                    "skill_overlap",
                    "seniority",
                    "SALARY_MIN",
                    "SALARY_MAX",
                    "SALARY_CURRENCY",
                ]
                display_df = full_topN.reindex(columns=[c for c in selected_cols if c in full_topN.columns])
                st.dataframe(display_df, use_container_width=True, height=600)



                # Skill overlap chart
                st.subheader("Skill Overlap (Top 10)")
                topN_sk = topN.copy()
                topN_sk["skill_overlap_pct"] = topN_sk["skill_overlap"] * 100
                fig2 = px.bar(topN_sk, x="JOB_TITLE", y="skill_overlap_pct", color="skill_overlap_pct", color_continuous_scale="Mint")
                st.plotly_chart(fig2, use_container_width=True)

                # Radar for best match
                best = topN.iloc[0]
                radar_vals = [best["cosine_sim"], best["skill_overlap"], best["seniority"]]
                radar_labels = ["Cosine", "Skill", "Seniority"]
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(r=radar_vals + [radar_vals[0]], theta=radar_labels + [radar_labels[0]], fill='toself', name=best["JOB_TITLE"]))
                fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0, 1])), showlegend=False)
                st.subheader(f"Profile radar — Best Match: {best['JOB_TITLE']}")
                st.plotly_chart(fig_radar, use_container_width=True)

                # Download
                csv_bytes = results_df.head(100).to_csv(index=False).encode("utf-8")
                st.download_button("Download results (top 100) as CSV", data=csv_bytes, file_name="job_matches_top100.csv", mime="text/csv")

    else:
        st.info("Upload a PDF resume to find matching jobs.")

    st.markdown("---")
    st.caption("Built with ❤️ — SentenceTransformers, Snowpark, Streamlit, Plotly")


if __name__ == "__main__":
    main()