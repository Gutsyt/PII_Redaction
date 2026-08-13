# PII Redaction Tool - Comprehensive Evaluation Report

## Executive Summary

- **Overall Precision**: `100.00%`
- **Overall Recall**: `70.59%`
- **Overall F1-Score**: `82.76%`
- **Overall Accuracy**: `70.59%`

- **True Positives (TP)**: `24`
- **False Positives (FP)**: `0`
- **False Negatives (FN)**: `10`

## Category-Wise Metrics Breakdown

| PII Category | TP | FP | FN | Precision | Recall | F1 Score | Accuracy |
|---|---|---|---|---|---|---|---|
| **NAME** | 3 | 0 | 9 | 100.0% | 25.0% | 40.0% | 25.0% |
| **EMAIL** | 6 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% |
| **PHONE** | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% |
| **COMPANY** | 1 | 0 | 1 | 100.0% | 50.0% | 66.7% | 50.0% |
| **ADDRESS** | 2 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% |
| **GOVT_ID** | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% |
| **CREDIT_CARD** | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% |
| **DATE** | 2 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% |
| **IP_ADDRESS** | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% |

## Evaluation Methodology

1. **Dataset**: Evaluated on multi-domain dataset including ticket logs, financial Red Herring Prospectus documents, corporate records, and embedded identity cards (PAN/SSN).
2. **Ground Truth Annotation**: Expert human-annotated spans across all 9 minimum mandatory PII types.
3. **Control Testing**: Non-PII control tokens (e.g., ticket numbers, order IDs, section numbers) were included to verify that non-PII numbers and text are preserved.

## Error & False Positive / Negative Analysis

- **False Positives**: Addressed by maintaining an explicit exclude dictionary for legal/financial terminology (e.g., 'Red Herring Prospectus', 'Companies Act', 'SEBI ICDR Regulations').
- **False Negatives**: Mitigated by combining Named Entity Recognition (spaCy) with deterministic regex patterns for structured PII types like PAN cards, DINs, SSNs, and credit cards.