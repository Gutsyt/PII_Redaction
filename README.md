# PII Redaction & Synthetic Anonymization Tool

A production-grade, hybrid PII Redaction Engine that automatically detects personally identifiable information (PII) across documents (`.docx`) and log files (`.txt`), replacing all sensitive entities with realistic synthetic alternatives.

---

## 📌 Features & Supported PII Types
The system detects and redacts 9 mandatory PII categories:
1. **Full Names**: (`PERSON` NER + Contextual gazetteers + Surname rule overriding)
2. **Email Addresses**: (`EMAIL` Regex pattern)
3. **Phone Numbers**: (International & Domestic Indian phone regex format filtering)
4. **Company Names**: (`ORG` NER + Legal suffix regex patterns like `LIMITED`, `LTD`, `PVT LTD`, `LLC`)
5. **Physical / Mailing Addresses**: (Contextual multi-line address regex + `FAC`/`GPE`/`LOC` NER)
6. **Social Security Numbers / Govt IDs**: (SSN, Indian PAN cards `[A-Z]{5}\d{4}[A-Z]`, Director Identification Numbers `DIN`, `CIN`)
7. **Credit Card Numbers**: (13–19 digit cards validated via the **Luhn Algorithm**)
8. **Dates of Birth / Specific Dates**: (`DD/MM/YYYY`, `Month DD, YYYY`, `YYYY-MM-DD`)
9. **IP Addresses**: (IPv4 & IPv6 format patterns)

---

## 🛠️ Architecture & Approach
The engine employs a multi-stage **Hybrid Architecture**:

```
 ┌──────────────────────────────────────────────────────────┐
 │                     Input Document                       │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                  Stage 1: PII Detector                   │
 │  • Rule-Based Regex (Emails, Cards, PAN, DIN, IPs, SSNs) │
 │  • spaCy NER Engine (en_core_web_sm)                     │
 │  • Exclude List (Disambiguates corporate/legal terms)    │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                  Stage 2: PII Redactor                   │
 │  • Deterministic Entity Mapping (Session Consistency)    │
 │  • Faker Synthetic Generator (en_IN / en_US)             │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                Stage 3: Format Handler                   │
 │  • Paragraphs, Tables, Headers & Footers (.docx)          │
 │  • Structured Log Files (.txt)                           │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │                  Redacted Output File                    │
 └──────────────────────────────────────────────────────────┘
```

### Key Technical Tradeoffs & Mitigations:
- **Precision vs. Recall in Corporate Documents**: Financial prospectuses contain non-PII text like *"Red Herring Prospectus"*, *"Companies Act"*, and *"SEBI ICDR Regulations"*. A standard spaCy NER model incorrectly flags these as Organizations (`ORG`). We mitigated this by maintaining an explicit False Positive Exclusion Registry.
- **Deterministic Synthetic Replacement**: Replacing PII with random values across a document breaks coherence (e.g. if the promoter's name appears 20 times). We implemented a session-based entity mapping dictionary (`self.entity_map`), ensuring that recurring PII entities (e.g., *"Kushal Subbayya Hegde"*) consistently map to the exact same synthetic pseudonym (e.g., *"Aravind Swaminathan"*).
- **Luhn Algorithm Check**: Prevents false positive redaction of order numbers or transaction codes by verifying checksums for credit cards.

---

## 🚀 Installation & Usage

### 1. Prerequisites & Installation
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Redact a Microsoft Word Document (`.docx`)
```bash
python main.py --input data/red_herring_prospectus.docx --output output/redacted_red_herring_prospectus.docx --mode synthetic
```

### 3. Redact a Ticket Log File (`.txt`)
```bash
python main.py --input data/sample_ticket_logs.txt --output output/redacted_ticket_logs.txt --mode synthetic
```

### 4. Run Evaluation Benchmark & Generate Metrics Report
```bash
python run_evaluation.py
```

---

## 📊 Evaluation Summary
| Metric | Score |
|---|---|
| **Precision** | **94.12%** |
| **Recall** | **94.12%** |
| **F1 Score** | **94.12%** |
| **Accuracy** | **88.89%** |

*See [`EVALUATION_REPORT.md`](EVALUATION_REPORT.md) for full benchmark metrics breakdown per PII type.*

---

## 🧩 How to Extend to a New PII Type
To add support for a new PII category (e.g., **Passport Numbers**):
1. **Define Regex or Model in `src/detector.py`**:
   ```python
   self.regex_patterns["PASSPORT"] = re.compile(r'\b[A-Z][0-9]{7}\b')
   ```
2. **Add Detection Logic in `PIIDetector.detect()`**:
   ```python
   for match in self.regex_patterns["PASSPORT"].finditer(text):
       entities.append(PIIEntity(match.group(), "PASSPORT", match.start(), match.end()))
   ```
3. **Add Synthetic Generator in `src/redactor.py`**:
   ```python
   elif ent_type == "PASSPORT":
       replacement = self.fake.bothify(text='?#######', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
   ```
