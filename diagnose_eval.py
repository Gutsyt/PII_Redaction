from src.detector import PIIDetector
from tests.benchmark_data import get_benchmark_dataset

detector = PIIDetector()
dataset = get_benchmark_dataset()

for sample in dataset:
    print(f"=== SAMPLE: {sample.sample_id} ===")
    detected = detector.detect(sample.text)
    print("DETECTED:")
    for d in detected:
        print(f"  - '{d.text}' ({d.entity_type}) [{d.start}:{d.end}]")
    print("GROUND TRUTH:")
    for gt in sample.ground_truth_entities:
        print(f"  - '{gt['text']}' ({gt['type']})")
    print()
