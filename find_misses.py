from src.detector import PIIDetector
from tests.benchmark_data import get_benchmark_dataset

detector = PIIDetector()
dataset = get_benchmark_dataset()

for sample in dataset:
    print(f"=== SAMPLE: {sample.sample_id} ===")
    detected = detector.detect(sample.text)
    det_texts = [d.text.strip().lower() for d in detected]
    
    print("DETECTED ENTITIES:")
    for d in detected:
        print(f"  [{d.entity_type}] '{d.text}'")
        
    print("\nMISSED GROUND TRUTH ENTITIES (False Negatives):")
    for gt in sample.ground_truth_entities:
        gt_t = gt["text"].strip().lower()
        matched = any(gt_t in dt or dt in gt_t for dt in det_texts)
        if not matched:
            print(f"  MISSED: [{gt['type']}] '{gt['text']}'")
    print("\n" + "="*50 + "\n")
