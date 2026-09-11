"""Local classifiers: IndicBERT frozen encoder + trained classification head;
character TF-IDF logistic regression is the explicit offline fallback.
Risk is an illustrative policy score, never a probability of harm.
"""
import os
from pathlib import Path
from functools import lru_cache
import re
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from backend.ml.data import training_rows

MODEL_ID = 'ai4bharat/IndicBERTv2-MLM-only'
MODEL_REVISION = '8598f13fe52443bc3fc054fcd665944560145b5c'
MODEL_DIR = Path(os.getenv('MODEL_DIR', 'backend/artifacts/indicbert'))
EXPLANATIONS = {
    'neutral': 'No clear risk pattern was identified in this message. This does not establish that a conversation is safe.',
    'grooming-trust-building': 'The message resembles exclusive attention or gifts used to build dependency. Friendly language alone is not evidence of grooming.',
    'grooming-isolation-request': 'The message resembles a request for secrecy, private contact, or separation from trusted adults.',
    'grooming-coercive-language': 'The message resembles pressure to comply, backed by a threat to expose private information or cause harm.',
    'bullying-harassment': 'The message resembles targeted humiliation, exclusion, or repeated personal insults.',
}
BASE_SCORES = {'neutral': 12, 'grooming-trust-building': 43, 'grooming-isolation-request': 66, 'grooming-coercive-language': 85, 'bullying-harassment': 60}

class Detector:
    def __init__(self, mode=None):
        requested = mode or os.getenv('DETECTOR', 'auto')
        if requested not in ('auto', 'indicbert', 'baseline'):
            raise ValueError('DETECTOR must be auto, indicbert or baseline')
        self.reason = None
        if requested != 'baseline' and (MODEL_DIR / 'head.joblib').exists():
            try:
                import joblib
                import torch
                from transformers import AutoModel, AutoTokenizer
                torch.set_num_threads(min(4, os.cpu_count() or 1))
                # Transformers 4.57.6 misidentifies re-saved local BERT configs as Mistral.
                # Preserve the original IndicBERT tokenizer; do not apply a foreign tokenizer patch.
                self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True, fix_mistral_regex=False)
                self.encoder = AutoModel.from_pretrained(MODEL_DIR, local_files_only=True).eval()
                self.head = joblib.load(MODEL_DIR / 'head.joblib')
                self.name = 'IndicBERTv2 · trained head'
                self.kind = 'indicbert'
                return
            except Exception as exc:
                if requested == 'indicbert':
                    raise RuntimeError('IndicBERT artifacts could not be loaded') from exc
                self.reason = 'IndicBERT artifacts could not be loaded; baseline is active.'
        elif requested == 'indicbert':
            raise RuntimeError('Train IndicBERT first: python -m backend.ml.train')
        self.reason = self.reason or 'IndicBERT checkpoint is not installed; baseline is active.'
        rows = training_rows()
        self.head = make_pipeline(TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True), LogisticRegression(C=12, max_iter=1500, random_state=42))
        self.head.fit([r['text'] for r in rows], [r['label'] for r in rows])
        self.name = 'TF-IDF · fallback classifier'
        self.kind = 'baseline'

    def embeddings(self, texts):
        import torch
        batches = []
        for offset in range(0, len(texts), 8):
            tokens = self.tokenizer(texts[offset:offset+8], padding=True, truncation=True, max_length=192, return_tensors='pt')
            with torch.inference_mode():
                hidden = self.encoder(**tokens).last_hidden_state
                mask = tokens['attention_mask'].unsqueeze(-1)
                pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1)
            batches.append(pooled.cpu().numpy())
        return np.concatenate(batches)

    def classify(self, text):
        features = self.embeddings([text]) if self.kind == 'indicbert' else [text]
        probabilities = self.head.predict_proba(features)[0]
        index = int(np.argmax(probabilities))
        label = str(self.head.classes_[index])
        confidence = float(probabilities[index])
        score = BASE_SCORES[label]
        # Low-confidence predictions stay visible, but do not imply certainty.
        if confidence < .38 and label != 'neutral':
            score = min(score, 49)
        return {'risk_score': score, 'risk_level': risk_level(score), 'pattern_type': label,
                'confidence': round(confidence, 3), 'explanation': EXPLANATIONS[label],
                'model': self.name, 'model_kind': self.kind}

@lru_cache(maxsize=1)
def get_detector():
    return Detector()

def risk_level(score):
    return 'High' if score >= 75 else 'Medium' if score >= 40 else 'Low'

def analyze_message(text: str) -> dict:
    if not text.strip():
        raise ValueError('Message must not be blank')
    return get_detector().classify(text.strip())

def minimal_snippet(text: str, limit: int = 140) -> str:
    # Never store the whole multi-line window: choose only the last nonempty line.
    line = next((x.strip() for x in reversed(text.splitlines()) if x.strip()), '')
    line = re.sub(r'https?://\S+', '[link]', line)
    line = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[email]', line)
    line = re.sub(r'(?<!\w)\+?\d[\d\s()-]{7,}\d(?!\w)', '[phone]', line)
    return line[:limit] + ('…' if len(line) > limit else '')

