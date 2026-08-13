import re
from typing import List, Dict, Any, Set
from src.detector import PIIDetector, PIIEntity

class GroundTruthSample:
    def __init__(self, sample_id: str, text: str, ground_truth_entities: List[Dict[str, Any]], non_pii_tokens: List[str] = None):
        self.sample_id = sample_id
        self.text = text
        self.ground_truth_entities = ground_truth_entities
        self.non_pii_tokens = non_pii_tokens or []

def normalize_str(s: str) -> str:
    s = s.strip().lower()
    for ch in ['–', '—', '', '\ufffd']:
        s = s.replace(ch, '-')
    return re.sub(r'\s+', ' ', s)

class PIIEvaluator:
    def __init__(self, detector: PIIDetector = None):
        self.detector = detector or PIIDetector()

    def evaluate_benchmark(self, dataset: List[GroundTruthSample]) -> Dict[str, Any]:
        category_stats: Dict[str, Dict[str, int]] = {}
        all_categories = ["NAME", "EMAIL", "PHONE", "COMPANY", "ADDRESS", "GOVT_ID", "CREDIT_CARD", "DATE", "IP_ADDRESS"]
        
        for cat in all_categories:
            category_stats[cat] = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}

        sample_results = []

        for sample in dataset:
            detected_entities = self.detector.detect(sample.text)
            
            matched_gt_indices: Set[int] = set()
            matched_det_indices: Set[int] = set()

            # Pass 1: Normalize & Match
            for det_idx, det in enumerate(detected_entities):
                det_norm = normalize_str(det.text)
                for gt_idx, gt in enumerate(sample.ground_truth_entities):
                    if gt_idx in matched_gt_indices:
                        continue
                    gt_norm = normalize_str(gt["text"])
                    if (det_norm == gt_norm or det_norm in gt_norm or gt_norm in det_norm) and det.entity_type == gt["type"]:
                        category_stats[det.entity_type]["TP"] += 1
                        matched_gt_indices.add(gt_idx)
                        matched_det_indices.add(det_idx)
                        break

            # False Positives
            for det_idx, det in enumerate(detected_entities):
                if det_idx not in matched_det_indices:
                    cat = det.entity_type if det.entity_type in category_stats else "NAME"
                    category_stats[cat]["FP"] += 1

            # False Negatives
            for gt_idx, gt in enumerate(sample.ground_truth_entities):
                if gt_idx not in matched_gt_indices:
                    cat = gt["type"] if gt["type"] in category_stats else "NAME"
                    category_stats[cat]["FN"] += 1

            sample_results.append({
                "sample_id": sample.sample_id,
                "detected": [d.to_dict() for d in detected_entities],
                "ground_truth": sample.ground_truth_entities
            })

        # Calculate final precision, recall, f1, accuracy
        report_per_cat = {}
        total_tp, total_fp, total_fn = 0, 0, 0

        for cat, stats in category_stats.items():
            tp, fp, fn = stats["TP"], stats["FP"], stats["FN"]
            total_tp += tp
            total_fp += fp
            total_fn += fn

            precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            accuracy = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 1.0

            report_per_cat[cat] = {
                "TP": tp,
                "FP": fp,
                "FN": fn,
                "Precision": round(precision, 4),
                "Recall": round(recall, 4),
                "F1_Score": round(f1, 4),
                "Accuracy": round(accuracy, 4)
            }

        overall_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
        overall_rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
        overall_f1 = (2 * overall_prec * overall_rec) / (overall_prec + overall_rec) if (overall_prec + overall_rec) > 0 else 0.0
        total_samples = total_tp + total_fp + total_fn
        overall_acc = total_tp / total_samples if total_samples > 0 else 1.0

        return {
            "per_category": report_per_cat,
            "overall": {
                "Total_TP": total_tp,
                "Total_FP": total_fp,
                "Total_FN": total_fn,
                "Precision": round(overall_prec, 4),
                "Recall": round(overall_rec, 4),
                "F1_Score": round(overall_f1, 4),
                "Accuracy": round(overall_acc, 4)
            },
            "sample_details": sample_results
        }
