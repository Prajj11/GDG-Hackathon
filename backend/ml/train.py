"""Train a classification head over real AI4Bharat IndicBERT embeddings with class-weighted loss.
Includes validation tracking, class balance weighting, and scikit-learn fallback baseline.
Run from repository root: python -m backend.ml.train
"""
import json
import os
import hashlib
import joblib
import torch
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score, f1_score
from transformers import AutoModel, AutoTokenizer
from backend.ml.data import training_rows, val_rows, get_splits, LABELS
from backend.ml.detector import Detector, MODEL_DIR, MODEL_ID, MODEL_REVISION

def main():
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    
    # 1. Load stratified splits
    train_data, val_data, test_data = get_splits()
    train_items = training_rows()
    val_items = val_rows()
    
    print(f"Dataset splits loaded: {len(train_data)} train convs ({len(train_items)} samples), "
          f"{len(val_data)} val convs, {len(test_data)} test convs.", flush=True)

    detector = object.__new__(Detector)
    print("Loading AI4Bharat IndicBERT...", flush=True)
    detector.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    detector.encoder = AutoModel.from_pretrained(MODEL_ID, revision=MODEL_REVISION).eval()

    print(f"Encoding {len(train_items)} training representations with IndicBERTv2...", flush=True)
    train_texts = [row['text'] for row in train_items]
    train_labels = [row['label'] for row in train_items]
    train_embeddings = detector.embeddings(train_texts)

    # 2. Train IndicBERT head with class-weighted loss
    print("Fitting supervised head with class-weighted loss (class_weight='balanced')...", flush=True)
    head = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=0.1, class_weight='balanced', max_iter=2500, random_state=42)
    )
    head.fit(train_embeddings, train_labels)

    # 3. Evaluate on Validation split
    print(f"Encoding {len(val_items)} validation representations...", flush=True)
    val_texts = [row['text'] for row in val_items]
    val_labels = [row['label'] for row in val_items]
    val_embeddings = detector.embeddings(val_texts)
    val_preds = head.predict(val_embeddings)
    
    val_acc = accuracy_score(val_labels, val_preds)
    val_macro_f1 = f1_score(val_labels, val_preds, average='macro', zero_division=0)
    print(f"\n--- Validation Set Performance ---")
    print(f"Accuracy: {val_acc:.4f} | Macro F1: {val_macro_f1:.4f}")
    val_report = classification_report(val_labels, val_preds, output_dict=True, zero_division=0)
    for lbl in LABELS:
        if lbl in val_report:
            print(f"  {lbl:<30} Precision: {val_report[lbl]['precision']:.2f} | "
                  f"Recall: {val_report[lbl]['recall']:.2f} | F1: {val_report[lbl]['f1-score']:.2f}")

    # 4. Train matching TF-IDF Baseline Fallback
    print("\nFitting offline TF-IDF baseline fallback on the same train split...", flush=True)
    baseline_head = make_pipeline(
        TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True),
        LogisticRegression(C=10.0, class_weight='balanced', max_iter=2000, random_state=42)
    )
    baseline_head.fit(train_texts, train_labels)
    baseline_val_preds = baseline_head.predict(val_texts)
    baseline_val_acc = accuracy_score(val_labels, baseline_val_preds)
    baseline_val_f1 = f1_score(val_labels, baseline_val_preds, average='macro', zero_division=0)
    print(f"Baseline Validation: Accuracy={baseline_val_acc:.4f}, Macro F1={baseline_val_f1:.4f}")

    # 5. Save Artifacts
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    detector.encoder.save_pretrained(MODEL_DIR, safe_serialization=True)
    detector.tokenizer.save_pretrained(MODEL_DIR)
    joblib.dump(head, MODEL_DIR / 'head.joblib')
    joblib.dump(baseline_head, MODEL_DIR / 'baseline_head.joblib')

    metadata = {
        'model': MODEL_ID,
        'revision': MODEL_REVISION,
        'method': 'Frozen IndicBERT mean-pooled embeddings + supervised class-weighted logistic regression head',
        'training_conversations': len(train_data),
        'training_examples_augmented': len(train_items),
        'validation_accuracy': round(val_acc, 4),
        'validation_macro_f1': round(val_macro_f1, 4),
        'baseline_validation_macro_f1': round(baseline_val_f1, 4),
        'dataset_sha256': hashlib.sha256(json.dumps(train_items, ensure_ascii=False).encode()).hexdigest(),
        'classes': LABELS,
        'limitations': 'Hybrid real (HASOC, BullyExplain, DravidianLangTech, COMI-LINGUA) + synthetic (grooming stages grounded in PAN12) dataset for child safety risk prioritization.'
    }
    (MODEL_DIR / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf8')
    print(f"\nArtifacts successfully saved to {MODEL_DIR}")
    print(json.dumps(metadata, indent=2), flush=True)

if __name__ == '__main__':
    main()
