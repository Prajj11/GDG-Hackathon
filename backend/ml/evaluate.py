"""Comprehensive model evaluation on held-out test split (15% unseen data).
Computes per-class precision/recall/F1, False Positive Rate on neutral data,
cross-language breakdowns (English, Hindi, Hinglish, Malayalam, Manglish),
and qualitative error analysis.
"""
import argparse
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import numpy as np
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from backend.ml.detector import Detector
from backend.ml.data import test_rows, training_rows, LABELS

def evaluate_model(mode='indicbert', output_path=None):
    detector = Detector(mode)
    test_items = test_rows()

    y_true = [item['label'] for item in test_items]
    texts = [item['text'] for item in test_items]
    languages = [item['language'] for item in test_items]

    # Run predictions
    results = [detector.classify(text) for text in texts]
    y_pred = [r['pattern_type'] for r in results]

    # 1. Overall & Per-Class Metrics
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    class_rep = classification_report(y_true, y_pred, labels=LABELS, output_dict=True, zero_division=0)

    # 2. False Positive Rate on Neutral/Benign Class
    # False Positive on neutral = A truly neutral message flagged as harmful (non-neutral)
    neutral_indices = [i for i, label in enumerate(y_true) if label == 'neutral']
    neutral_total = len(neutral_indices)
    neutral_false_positives = sum(y_pred[i] != 'neutral' for i in neutral_indices)
    neutral_fpr = (neutral_false_positives / neutral_total) if neutral_total > 0 else 0.0

    # 3. False Negative Rate on Harmful Classes
    harmful_indices = [i for i, label in enumerate(y_true) if label != 'neutral']
    harmful_total = len(harmful_indices)
    harmful_missed = sum(y_pred[i] == 'neutral' for i in harmful_indices)
    harmful_fnr = (harmful_missed / harmful_total) if harmful_total > 0 else 0.0

    # 4. Cross-Language Breakdown
    unique_langs = sorted(list(set(languages)))
    per_language = {}
    for lang in unique_langs:
        lang_indices = [i for i, l in enumerate(languages) if l == lang]
        lang_true = [y_true[i] for i in lang_indices]
        lang_pred = [y_pred[i] for i in lang_indices]
        lang_acc = accuracy_score(lang_true, lang_pred)
        lang_f1 = f1_score(lang_true, lang_pred, average='macro', zero_division=0)
        lang_neutral_total = sum(1 for y in lang_true if y == 'neutral')
        lang_neutral_fp = sum(1 for yt, yp in zip(lang_true, lang_pred) if yt == 'neutral' and yp != 'neutral')
        per_language[lang] = {
            'samples': len(lang_indices),
            'accuracy': round(lang_acc, 4),
            'macro_f1': round(lang_f1, 4),
            'neutral_samples': lang_neutral_total,
            'neutral_false_positives': lang_neutral_fp,
            'neutral_fpr': round((lang_neutral_fp / lang_neutral_total) if lang_neutral_total > 0 else 0.0, 4)
        }

    # 5. Real vs Synthetic Origin Breakdown
    origins = [item.get('origin', 'synthetic') for item in test_items]
    unique_origins = sorted(list(set(origins)))
    per_origin = {}
    for orig in unique_origins:
        orig_indices = [i for i, o in enumerate(origins) if o == orig]
        orig_true = [y_true[i] for i in orig_indices]
        orig_pred = [y_pred[i] for i in orig_indices]
        orig_acc = accuracy_score(orig_true, orig_pred)
        orig_f1 = f1_score(orig_true, orig_pred, average='macro', zero_division=0)
        orig_neutral_total = sum(1 for y in orig_true if y == 'neutral')
        orig_neutral_fp = sum(1 for yt, yp in zip(orig_true, orig_pred) if yt == 'neutral' and yp != 'neutral')
        orig_harmful_total = sum(1 for y in orig_true if y != 'neutral')
        orig_harmful_fn = sum(1 for yt, yp in zip(orig_true, orig_pred) if yt != 'neutral' and yp == 'neutral')
        orig_class_rep = classification_report(orig_true, orig_pred, labels=LABELS, output_dict=True, zero_division=0)
        
        per_origin[orig] = {
            'samples': len(orig_indices),
            'accuracy': round(orig_acc, 4),
            'macro_f1': round(orig_f1, 4),
            'neutral_samples': orig_neutral_total,
            'neutral_false_positives': orig_neutral_fp,
            'neutral_fpr': round((orig_neutral_fp / orig_neutral_total) if orig_neutral_total > 0 else 0.0, 4),
            'harmful_samples': orig_harmful_total,
            'harmful_false_negatives': orig_harmful_fn,
            'harmful_fnr': round((orig_harmful_fn / orig_harmful_total) if orig_harmful_total > 0 else 0.0, 4),
            'classes': {
                lbl: {
                    'precision': round(orig_class_rep[lbl]['precision'], 4),
                    'recall': round(orig_class_rep[lbl]['recall'], 4),
                    'f1': round(orig_class_rep[lbl]['f1-score'], 4),
                    'support': orig_class_rep[lbl]['support']
                } for lbl in LABELS if orig_class_rep[lbl]['support'] > 0
            }
        }

    # 6. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=LABELS).tolist()

    # 7. Qualitative Error Review (Misclassifications & Correct Samples)
    errors = []
    correct_samples = []
    for i, (yt, yp, text, lang, res) in enumerate(zip(y_true, y_pred, texts, languages, results)):
        record = {
            'id': test_items[i].get('id', f'test_{i}'),
            'language': lang,
            'origin': test_items[i].get('origin', 'synthetic'),
            'source_dataset': test_items[i].get('source_dataset', 'Unknown'),
            'text': text,
            'expected': yt,
            'predicted': yp,
            'confidence': res['confidence'],
            'risk_score': res['risk_score'],
            'explanation': res['explanation']
        }
        if yt != yp:
            errors.append(record)
        else:
            if len(correct_samples) < 15:
                correct_samples.append(record)

    report = {
        'model': detector.name,
        'model_kind': detector.kind,
        'test_samples_total': len(test_items),
        'overall': {
            'accuracy': round(acc, 4),
            'macro_f1': round(macro_f1, 4),
            'weighted_f1': round(weighted_f1, 4),
        },
        'safety_rates': {
            'neutral_total': neutral_total,
            'neutral_false_positives': neutral_false_positives,
            'neutral_false_positive_rate': round(neutral_fpr, 4),
            'harmful_total': harmful_total,
            'harmful_missed_false_negatives': harmful_missed,
            'harmful_false_negative_rate': round(harmful_fnr, 4),
        },
        'per_class': {
            lbl: {
                'precision': round(class_rep[lbl]['precision'], 4),
                'recall': round(class_rep[lbl]['recall'], 4),
                'f1': round(class_rep[lbl]['f1-score'], 4),
                'support': class_rep[lbl]['support']
            } for lbl in LABELS if lbl in class_rep
        },
        'per_language': per_language,
        'per_origin': per_origin,
        'confusion_matrix': {
            'labels': LABELS,
            'matrix': cm
        },
        'misclassifications_count': len(errors),
        'misclassifications': errors,
        'sample_correct_predictions': correct_samples
    }

    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')

    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['baseline', 'indicbert'], default='indicbert')
    parser.add_argument('--output', help='JSON file to save evaluation results')
    args = parser.parse_args()

    report = evaluate_model(args.mode, args.output)
    print("=" * 65)
    print(f"EVALUATION REPORT: {report['model']}")
    print("=" * 65)
    print(f"Overall Accuracy:  {report['overall']['accuracy']:.4f}")
    print(f"Macro F1 Score:    {report['overall']['macro_f1']:.4f}")
    print(f"Weighted F1 Score: {report['overall']['weighted_f1']:.4f}")
    print(f"Neutral FPR:       {report['safety_rates']['neutral_false_positive_rate'] * 100:.2f}% "
          f"({report['safety_rates']['neutral_false_positives']}/{report['safety_rates']['neutral_total']})")
    print(f"Harmful Missed FNR: {report['safety_rates']['harmful_false_negative_rate'] * 100:.2f}% "
          f"({report['safety_rates']['harmful_missed_false_negatives']}/{report['safety_rates']['harmful_total']})")
    
    print("\nPer-Class Breakdown:")
    for lbl, m in report['per_class'].items():
        print(f"  {lbl:<30} P: {m['precision']:.3f} | R: {m['recall']:.3f} | F1: {m['f1']:.3f} (N={m['support']})")

    print("\nCross-Language Breakdown:")
    for lang, m in report['per_language'].items():
        print(f"  {lang:<15} Acc: {m['accuracy']:.3f} | Macro F1: {m['macro_f1']:.3f} | Neutral FPR: {m['neutral_fpr']*100:.1f}% (N={m['samples']})")

    print("\nReal vs. Synthetic Origin Breakdown:")
    for orig, m in report['per_origin'].items():
        print(f"  {orig.upper():<12} Acc: {m['accuracy']:.3f} | Macro F1: {m['macro_f1']:.3f} | "
              f"Neutral FPR: {m['neutral_fpr']*100:.1f}% ({m['neutral_false_positives']}/{m['neutral_samples']}) | "
              f"Harmful FNR: {m['harmful_fnr']*100:.1f}% ({m['harmful_false_negatives']}/{m['harmful_samples']}) | (N={m['samples']})")
        for cl_lbl, cl_m in m['classes'].items():
            print(f"    - {cl_lbl:<28} F1: {cl_m['f1']:.3f} (N={cl_m['support']})")

    print(f"\nTotal Misclassifications on Held-Out Test Set: {report['misclassifications_count']} / {report['test_samples_total']}")
    if report['misclassifications']:
        print("\nQualitative Misclassification Review (Sample):")
        for err in report['misclassifications'][:5]:
            print(f"  - [{err['origin'].upper()} - {err['language']}] Expected: '{err['expected']}' -> Got: '{err['predicted']}' (Conf: {err['confidence']:.2f})")
            print(f"    Text: \"{err['text'][:90]}...\"" if len(err['text']) > 90 else f"    Text: \"{err['text']}\"")

if __name__ == '__main__':
    main()
