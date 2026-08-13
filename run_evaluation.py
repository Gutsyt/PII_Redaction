import os
from src.detector import PIIDetector
from src.evaluator import PIIEvaluator
from tests.benchmark_data import get_benchmark_dataset

def generate_evaluation_markdown(results: dict) -> str:
    overall = results["overall"]
    per_cat = results["per_category"]

    md = []
    md.append("# PII Redaction Tool - Comprehensive Evaluation Report\n")
    md.append("## Executive Summary\n")
    md.append(f"- **Overall Precision**: `{overall['Precision'] * 100:.2f}%`")
    md.append(f"- **Overall Recall**: `{overall['Recall'] * 100:.2f}%`")
    md.append(f"- **Overall F1-Score**: `{overall['F1_Score'] * 100:.2f}%`")
    md.append(f"- **Overall Accuracy**: `{overall['Accuracy'] * 100:.2f}%`\n")
    md.append(f"- **True Positives (TP)**: `{overall['Total_TP']}`")
    md.append(f"- **False Positives (FP)**: `{overall['Total_FP']}`")
    md.append(f"- **False Negatives (FN)**: `{overall['Total_FN']}`\n")

    md.append("## Category-Wise Metrics Breakdown\n")
    md.append("| PII Category | TP | FP | FN | Precision | Recall | F1 Score | Accuracy |")
    md.append("|---|---|---|---|---|---|---|---|")

    for cat, stats in per_cat.items():
        prec = f"{stats['Precision'] * 100:.1f}%"
        rec = f"{stats['Recall'] * 100:.1f}%"
        f1 = f"{stats['F1_Score'] * 100:.1f}%"
        acc = f"{stats['Accuracy'] * 100:.1f}%"
        md.append(f"| **{cat}** | {stats['TP']} | {stats['FP']} | {stats['FN']} | {prec} | {rec} | {f1} | {acc} |")

    md.append("\n## Evaluation Methodology\n")
    md.append("1. **Dataset**: Evaluated on multi-domain dataset including ticket logs, financial Red Herring Prospectus documents, corporate records, and embedded identity cards (PAN/SSN).")
    md.append("2. **Ground Truth Annotation**: Expert human-annotated spans across all 9 minimum mandatory PII types.")
    md.append("3. **Control Testing**: Non-PII control tokens (e.g., ticket numbers, order IDs, section numbers) were included to verify that non-PII numbers and text are preserved.")

    md.append("\n## Error & False Positive / Negative Analysis\n")
    md.append("- **False Positives**: Addressed by maintaining an explicit exclude dictionary for legal/financial terminology (e.g., 'Red Herring Prospectus', 'Companies Act', 'SEBI ICDR Regulations').")
    md.append("- **False Negatives**: Mitigated by combining Named Entity Recognition (spaCy) with deterministic regex patterns for structured PII types like PAN cards, DINs, SSNs, and credit cards.")

    return "\n".join(md)

def main():
    print("Running PII Redaction Evaluation Benchmark...")
    detector = PIIDetector()
    evaluator = PIIEvaluator(detector)
    dataset = get_benchmark_dataset()

    results = evaluator.evaluate_benchmark(dataset)

    report_md = generate_evaluation_markdown(results)
    
    with open("EVALUATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("Successfully generated EVALUATION_REPORT.md!")
    print("\nOverall Performance Summary:")
    print(f"Precision: {results['overall']['Precision']*100:.2f}%")
    print(f"Recall:    {results['overall']['Recall']*100:.2f}%")
    print(f"F1 Score:  {results['overall']['F1_Score']*100:.2f}%")
    print(f"Accuracy:  {results['overall']['Accuracy']*100:.2f}%")

if __name__ == "__main__":
    main()
