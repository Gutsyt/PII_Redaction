import os
import time
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from src.detector import PIIDetector
from src.redactor import PIIRedactor
from src.docx_handler import DocxRedactor
from src.evaluator import PIIEvaluator
from tests.benchmark_data import get_benchmark_dataset

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'output')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload

detector = PIIDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/redact-text', methods=['POST'])
def redact_text_endpoint():
    data = request.get_json() or {}
    text = data.get('text', '')
    mode = data.get('mode', 'synthetic')

    if not text.strip():
        return jsonify({
            'redacted_text': '',
            'entities': [],
            'stats': {'total': 0},
            'execution_ms': 0
        })

    start_time = time.time()
    redactor = PIIRedactor(mode=mode)
    entities = detector.detect(text)
    redacted_text, changes = redactor.redact_text(text, entities)
    exec_ms = round((time.time() - start_time) * 1000, 2)

    cat_counts = {}
    for e in entities:
        cat_counts[e.entity_type] = cat_counts.get(e.entity_type, 0) + 1

    return jsonify({
        'original_text': text,
        'redacted_text': redacted_text,
        'entities': [e.to_dict() for e in entities],
        'changes': changes,
        'stats': {
            'total': len(entities),
            'categories': cat_counts
        },
        'execution_ms': exec_ms
    })

@app.route('/api/redact-file', methods=['POST'])
def redact_file_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    mode = request.form.get('mode', 'synthetic')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"uploaded_{filename}")
    output_filename = f"redacted_{filename}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    file.save(input_path)

    ext = os.path.splitext(filename)[1].lower()
    start_time = time.time()

    if ext == '.docx':
        redactor = PIIRedactor(mode=mode)
        handler = DocxRedactor(detector=detector, redactor=redactor)
        res = handler.redact_file(input_path, output_path)
        total_redactions = res['total_redactions']
    else:
        # Text file processing
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        redactor = PIIRedactor(mode=mode)
        redacted_lines = []
        total_redactions = 0
        for line in lines:
            ents = detector.detect(line)
            r_line, chgs = redactor.redact_text(line, ents)
            total_redactions += len(chgs)
            redacted_lines.append(r_line)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(redacted_lines)

    exec_ms = round((time.time() - start_time) * 1000, 2)

    return jsonify({
        'filename': filename,
        'output_filename': output_filename,
        'download_url': f"/download/{output_filename}",
        'total_redactions': total_redactions,
        'execution_ms': exec_ms
    })

@app.route('/api/evaluation', methods=['GET'])
def get_evaluation_metrics():
    evaluator = PIIEvaluator(detector)
    dataset = get_benchmark_dataset()
    results = evaluator.evaluate_benchmark(dataset)
    return jsonify(results)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("Starting PII Redaction Web Application on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
