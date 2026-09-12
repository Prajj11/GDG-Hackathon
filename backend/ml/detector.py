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
BENIGN_EXPLANATIONS = {
    'safety-advice': 'The message appears to be protective advice about telling trusted adults or avoiding unsafe sharing.',
    'negation': 'The message explicitly negates threat or private-detail seeking language.',
    'reported-speech': 'The message appears to report or quote a concerning message rather than directly pressure the child.',
    'gaming-talk': 'The message appears to use ordinary gaming or match slang without targeted humiliation.',
}


def _plain(text):
    return re.sub(r'\s+', ' ', text.casefold()).strip()


def benign_context(text):
    normalized = _plain(text)
    trusted_adults = (
        'parent', 'parents', 'teacher', 'trusted adult', 'mum', 'mummy',
        'mumma', 'papa', 'guardian', 'coach',
    )
    protective_phrases = (
        'do not send', "don't send", 'never send', 'mat bhejna', 'batana',
        'tell a', 'tell your', 'ko batana', 'se baat karna',
    )
    private_terms = (
        'photo', 'photos', 'private detail', 'private details', 'details',
        'stranger', 'unknown', 'secret',
    )
    advice_markers = (
        'teacher ne bola', 'coach said', 'teacher said', 'if anyone', 'koi ',
        'someone asks', 'trusted adult', 'always talk', 'parents ko batana',
    )
    isolation_markers = (
        'our secret', 'humara secret', 'delete', 'private chat', 'chupke',
        'akele', 'alone', 'gharwalon se chhupao',
    )
    if (any(word in normalized for word in trusted_adults)
            and any(phrase in normalized for phrase in protective_phrases)
            and any(term in normalized for term in private_terms)
            and any(marker in normalized for marker in advice_markers)
            and not any(marker in normalized for marker in isolation_markers)):
        return 'safety-advice'

    negation_patterns = (
        (
            r"\b(not|never|no|don't|do not|nahi|nahin)\b.{0,80}"
            r"\b(threaten|threatening|dhamki|private detail|private details|photo|details)\b"
        ),
        (
            r"\b(do not|don't|not|nahi|nahin)\b.{0,40}"
            r"\b(want|chahiye)\b.{0,40}\b(private|details|photo)\b"
        ),
    )
    if any(re.search(pattern, normalized) for pattern in negation_patterns):
        return 'negation'

    reporting_phrases = (
        'my friend said', 'friend said', 'someone messaged', 'someone told',
        'a stranger told', 'told me', 'reported that',
    )
    coercive_terms = (
        'send your photo', 'report you', 'threaten', 'threatening', 'leak',
        'private picture', 'private photo',
    )
    if any(phrase in normalized for phrase in reporting_phrases) and any(term in normalized for term in coercive_terms):
        return 'reported-speech'

    gaming_terms = ('game', 'gaming', 'match', 'round', 'level')
    slang_terms = ('killer', 'destroyed me', 'crushed me', 'beat me', 'destroy kar diya')
    direct_insults = (
        'ugly', 'idiot', 'loser', 'worthless', 'stupid', 'freak', 'bekaar',
        'bewakoof',
    )
    if any(term in normalized for term in gaming_terms) and any(term in normalized for term in slang_terms) and not any(term in normalized for term in direct_insults):
        return 'gaming-talk'

    return None

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
        benign_reason = benign_context(text) if label != 'neutral' else None
        if benign_reason:
            label = 'neutral'
            score = BASE_SCORES[label]
            confidence = max(confidence, .55)
            explanation = f'{EXPLANATIONS[label]} {BENIGN_EXPLANATIONS[benign_reason]}'
        else:
            explanation = EXPLANATIONS[label]
        return {'risk_score': score, 'risk_level': risk_level(score), 'pattern_type': label,
                'confidence': round(confidence, 3), 'explanation': explanation,
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

