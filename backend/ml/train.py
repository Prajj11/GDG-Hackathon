"""Train a classification head over real AI4Bharat IndicBERT embeddings.
No random/untrained transformer classification head is used for inference.
Run from repository root: python -m backend.ml.train
"""
import json
import os
import hashlib
import joblib
import torch
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from transformers import AutoModel, AutoTokenizer
from backend.ml.data import training_rows
from backend.ml.detector import Detector, MODEL_DIR, MODEL_ID, MODEL_REVISION

def main():
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    rows = training_rows()
    detector = object.__new__(Detector)
    print('Loading AI4Bharat IndicBERT...', flush=True)
    detector.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    detector.encoder = AutoModel.from_pretrained(MODEL_ID, revision=MODEL_REVISION).eval()
    print(f'Encoding {len(rows)} synthetic examples...', flush=True)
    embeddings = detector.embeddings([row['text'] for row in rows])
    head = make_pipeline(StandardScaler(), LogisticRegression(C=.08, max_iter=2000, random_state=42))
    head.fit(embeddings, [row['label'] for row in rows])
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    detector.encoder.save_pretrained(MODEL_DIR, safe_serialization=True)
    detector.tokenizer.save_pretrained(MODEL_DIR)
    joblib.dump(head, MODEL_DIR / 'head.joblib')
    metadata = {'model': MODEL_ID, 'revision': MODEL_REVISION, 'method': 'Frozen IndicBERT mean-pooled embeddings + supervised logistic regression head', 'training_examples': len(rows), 'dataset_sha256': hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode()).hexdigest(), 'limitations': 'Small synthetic dataset; not validated for real-world child safeguarding or calibrated harm probabilities.'}
    (MODEL_DIR / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf8')
    print(json.dumps(metadata, indent=2), flush=True)

if __name__ == '__main__':
    main()
