from typing import List, Dict, Any
from pydantic import BaseModel


class ConfusionMatrixSchema(BaseModel):
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int


class MeasuredMetricsSchema(BaseModel):
    total_samples: int
    confusion_matrix: ConfusionMatrixSchema
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    evaluation_notes: str


def evaluate_dataset_classification_metrics(
    evaluations: List[Dict[str, Any]]
) -> MeasuredMetricsSchema:
    """
    Computes measured classification metrics (Precision, Recall, F1, Accuracy)
    for a controlled evaluation dataset of emails.

    Expected entry in evaluations:
    {
      "email_id": str,
      "expected_is_malicious": bool,
      "predicted_is_malicious": bool
    }
    """
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for item in evaluations:
        exp = item.get("expected_is_malicious", False)
        pred = item.get("predicted_is_malicious", False)

        if exp and pred:
            tp += 1
        elif not exp and not pred:
            tn += 1
        elif not exp and pred:
            fp += 1
        elif exp and not pred:
            fn += 1

    total = len(evaluations)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0

    return MeasuredMetricsSchema(
        total_samples=total,
        confusion_matrix=ConfusionMatrixSchema(
            true_positives=tp,
            true_negatives=tn,
            false_positives=fp,
            false_negatives=fn,
        ),
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1_score=round(f1, 4),
        accuracy=round(accuracy, 4),
        evaluation_notes=f"Measured against {total} controlled dataset emails including legitimate and malicious samples.",
    )
