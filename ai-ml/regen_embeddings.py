import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from app import (
    PREPROCESSED_CSV,
    ensure_stable_rn,
    fill_missing_job_fields,
    generate_and_store_embeddings,
    EMBED_MODEL_NAME,
)

print('Reloading job data...')
jobs_df = pd.read_csv(PREPROCESSED_CSV)
if 'SKILLS_FINAL' in jobs_df.columns:
    jobs_df['SKILLS_FINAL'] = jobs_df['SKILLS_FINAL'].fillna('').apply(lambda s: [x.strip() for x in str(s).split(',') if x.strip()])

jobs_df = fill_missing_job_fields(jobs_df)
jobs_df = ensure_stable_rn(jobs_df)
print('Rows after RN fix:', len(jobs_df))

model = SentenceTransformer(EMBED_MODEL_NAME, token=os.environ.get('HF_TOKEN'))
generate_and_store_embeddings(jobs_df, model)
print('Embeddings regenerated with updated RN values.')
