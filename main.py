import sys
import os
import argparse
from src.detector import PIIDetector
from src.redactor import PIIRedactor
from src.docx_handler import DocxRedactor

def redact_text_file(input_path: str, output_path: str, redactor_mode: str = "synthetic"):
    detector = PIIDetector()
    redactor = PIIRedactor(mode=redactor_mode)

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    redacted_lines = []
    total_redactions = 0

    for line in lines:
        entities = detector.detect(line)
        redacted_line, changes = redactor.redact_text(line, entities)
        total_redactions += len(changes)
        redacted_lines.append(redacted_line)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(redacted_lines)

    print(f"[SUCCESS] Redacted TXT file saved to: {output_path}")
    print(f"Total PII entities redacted: {total_redactions}")

def redact_docx_file(input_path: str, output_path: str, redactor_mode: str = "synthetic"):
    detector = PIIDetector()
    redactor = PIIRedactor(mode=redactor_mode)
    handler = DocxRedactor(detector=detector, redactor=redactor)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    res = handler.redact_file(input_path, output_path)

    print(f"[SUCCESS] Redacted DOCX file saved to: {output_path}")
    print(f"Total PII entities redacted: {res['total_redactions']}")

def main():
    parser = argparse.ArgumentParser(description="PII Redaction Tool - Detect and redact PII with synthetic alternatives.")
    parser.add_argument("--input", "-i", type=str, help="Path to input document or log file (.docx or .txt)")
    parser.add_argument("--output", "-o", type=str, help="Path to output redacted file (.docx or .txt)")
    parser.add_argument("--mode", "-m", type=str, default="synthetic", choices=["synthetic", "mask"], help="Redaction mode: 'synthetic' or 'mask'")
    parser.add_argument("--evaluate", "-e", action="store_true", help="Run benchmark evaluation suite")

    args = parser.parse_args()

    if args.evaluate:
        from run_evaluation import main as eval_main
        eval_main()
        return

    if not args.input or not args.output:
        parser.print_help()
        sys.exit(1)

    input_ext = os.path.splitext(args.input)[1].lower()

    if input_ext == ".docx":
        redact_docx_file(args.input, args.output, args.mode)
    else:
        redact_text_file(args.input, args.output, args.mode)

if __name__ == "__main__":
    main()
