"""Digital Guardrails — app.ml_engine compatibility facade.
Wraps the trained AI4Bharat IndicBERTv2 model and offline TF-IDF fallback
behind the stable AnalysisResult dataclass interface.
"""
import time
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from backend.ml.detector import (
    analyze_message as _backend_analyze_message,
    get_detector as _backend_get_detector
)

logger = logging.getLogger("digital_guardrails.ml_engine")

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRISIS = "crisis"

class PatternType(str, Enum):
    NEUTRAL = "neutral"
    BULLYING_HARASSMENT = "bullying_harassment"
    GROOMING_TRUST_BUILDING = "grooming_trust_building"
    GROOMING_ISOLATION_REQUEST = "grooming_isolation_request"
    GROOMING_COERCIVE_LANGUAGE = "grooming_coercive_language"

RISK_THRESHOLDS = {
    RiskLevel.LOW: 0.0,
    RiskLevel.MEDIUM: 0.45,
    RiskLevel.HIGH: 0.75,
}

EXPLANATION_TEMPLATES = {
    PatternType.NEUTRAL:
        "No concerning pattern was detected in this conversation.",
    PatternType.BULLYING_HARASSMENT:
        "This message shows signs of harassment or bullying language, such as insults, threats, or exclusion.",
    PatternType.GROOMING_TRUST_BUILDING:
        "This message shows a pattern of excessive flattery or attempts to build a private bond, which can be an early sign of grooming.",
    PatternType.GROOMING_ISOLATION_REQUEST:
        "This message asks to keep the conversation secret or move to a different platform, which is a common isolation tactic.",
    PatternType.GROOMING_COERCIVE_LANGUAGE:
        "This message uses guilt-tripping, pressure, or coercive language to push for compliance.",
}

# Internal pattern canonical mapper
_PATTERN_MAP = {
    "neutral": PatternType.NEUTRAL,
    "bullying-harassment": PatternType.BULLYING_HARASSMENT,
    "bullying_harassment": PatternType.BULLYING_HARASSMENT,
    "grooming-trust-building": PatternType.GROOMING_TRUST_BUILDING,
    "grooming_trust_building": PatternType.GROOMING_TRUST_BUILDING,
    "grooming-isolation-request": PatternType.GROOMING_ISOLATION_REQUEST,
    "grooming_isolation_request": PatternType.GROOMING_ISOLATION_REQUEST,
    "grooming-coercive-language": PatternType.GROOMING_COERCIVE_LANGUAGE,
    "grooming_coercive_language": PatternType.GROOMING_COERCIVE_LANGUAGE,
}

_LEVEL_MAP = {
    "Low": RiskLevel.LOW,
    "low": RiskLevel.LOW,
    "Medium": RiskLevel.MEDIUM,
    "medium": RiskLevel.MEDIUM,
    "High": RiskLevel.HIGH,
    "high": RiskLevel.HIGH,
    "Crisis": RiskLevel.CRISIS,
    "crisis": RiskLevel.CRISIS,
}

@dataclass
class AnalysisResult:
    risk_score: float          # 0.0 - 1.0 normalized score
    risk_level: RiskLevel      # derived RiskLevel enum
    pattern_type: PatternType  # classified PatternType enum
    explanation: str           # plain-language explanation
    language_detected: Optional[str] = None
    inference_ms: float = 0.0
    model_backend: str = "indicbert"

    # Support dictionary-like indexing res['risk_score'] for dual compatibility
    def __getitem__(self, item):
        if item == 'risk_score':
            return self.risk_score
        elif item == 'risk_level':
            return self.risk_level.value
        elif item == 'pattern_type':
            return self.pattern_type.value
        elif hasattr(self, item):
            val = getattr(self, item)
            return val.value if hasattr(val, 'value') else val
        raise KeyError(item)

    def to_dict(self):
        return {
            'risk_score': self.risk_score,
            'risk_level': self.risk_level.value,
            'pattern_type': self.pattern_type.value,
            'explanation': self.explanation,
            'language_detected': self.language_detected,
            'inference_ms': self.inference_ms,
            'model_backend': self.model_backend
        }

def load_model():
    """Warm up and load the trained IndicBERT model into memory once."""
    detector = _backend_get_detector()
    logger.info(f"Loaded Digital Guardrails model backend: {detector.name} ({detector.kind})")
    return detector

def analyze_message(text: str, language_hint: Optional[str] = None) -> AnalysisResult:
    """Analyze a single message or conversation window using the trained IndicBERT detector.
    
    Args:
        text: Raw message text or multi-turn window
        language_hint: Optional language code / hint
        
    Returns:
        AnalysisResult: Structured assessment with typed enums and score
    """
    start = time.perf_counter()
    if not text or not text.strip():
        return AnalysisResult(
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            pattern_type=PatternType.NEUTRAL,
            explanation=EXPLANATION_TEMPLATES[PatternType.NEUTRAL],
            language_detected=language_hint,
            inference_ms=0.0,
            model_backend="indicbert"
        )

    # Call the real trained IndicBERTv2 detector
    raw = _backend_analyze_message(text)
    elapsed_ms = (time.perf_counter() - start) * 1000

    pattern_type = _PATTERN_MAP.get(raw.get('pattern_type', 'neutral'), PatternType.NEUTRAL)
    risk_level = _LEVEL_MAP.get(raw.get('risk_level', 'Low'), RiskLevel.LOW)
    score_float = round(float(raw.get('risk_score', 0)) / 100.0, 4)

    explanation = raw.get('explanation') or EXPLANATION_TEMPLATES.get(pattern_type, "")

    return AnalysisResult(
        risk_score=score_float,
        risk_level=risk_level,
        pattern_type=pattern_type,
        explanation=explanation,
        language_detected=language_hint,
        inference_ms=round(elapsed_ms, 2),
        model_backend=raw.get('model_kind', 'indicbert')
    )

__all__ = [
    'RiskLevel',
    'PatternType',
    'AnalysisResult',
    'RISK_THRESHOLDS',
    'EXPLANATION_TEMPLATES',
    'load_model',
    'analyze_message'
]
