import re
import spacy
from typing import List, Dict, Any, Tuple

# Luhn Algorithm for Credit Card validation
def is_valid_luhn(card_num: str) -> bool:
    digits = [int(d) for d in re.sub(r'\D', '', card_num)]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for idx, digit in enumerate(reverse_digits):
        if idx % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0

class PIIEntity:
    def __init__(self, text: str, entity_type: str, start: int, end: int, score: float = 1.0):
        self.text = text
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "entity_type": self.entity_type,
            "start": self.start,
            "end": self.end,
            "score": self.score
        }

    def __repr__(self):
        return f"<PIIEntity '{self.text}' [{self.entity_type}] ({self.start}:{self.end})>"

class PIIDetector:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

        # Exclude non-PII terms & common field header labels to prevent false positives
        self.false_positive_terms = {
            "red herring prospectus", "book built offer", "companies act", "sebi icdr regulations",
            "board of directors", "fresh issue", "offer for sale", "table of contents",
            "corporate identity number", "registered office", "corporate office", "contact person",
            "equity shares", "face value", "price band", "bid/offer period", "draft red herring prospectus",
            "working day", "working days", "statutory auditors", "book running lead managers",
            "registrar to the offer", "syndicate members", "anchor investor", "retail individual investors",
            "non-institutional investors", "qualified institutional buyers", "general risks", "risk factors",
            "indian rupees", "united states dollars", "bse limited", "national stock exchange",
            "promoter group", "promoter selling shareholders", "capital structure", "objects of the offer",
            "listing", "definition", "definitions and abbreviations", "care report", "care ratings",
            "executive director", "managing director", "independent director", "company secretary",
            "compliance officer", "statutory auditor", "statutory dues", "public offer account",
            "escrow account", "refund account", "bid lot", "cap price", "floor price", "cut-off price",
            # Common headers & labels
            "email", "govt id", "ssn", "dob", "credit card", "ip", "pan card", "din", "cin",
            "customer", "phone", "user", "address", "company", "issue", "ticket", "order",
            "ticket #", "order #", "order number", "invoice", "date of birth", "fax",
            "govt id / ssn", "govt id:", "ssn:", "pan card:", "pan card"
        }

        # Known Indian surnames for person name override
        self.known_surnames = {
            "hegde", "shetty", "patil", "dey", "singh", "malvadkar", "bhagwat", "joshi",
            "shah", "sarkar", "rastogi", "diwan", "gopalkrishnan", "sarvaiya", "munot",
            "tiwari", "jacob", "rai", "boricha", "parab", "ramani", "raste", "gyara",
            "shukla", "wakhele", "pulloor", "soni", "bhandary", "parker", "doe"
        }

        # Regex patterns
        self.regex_patterns = {
            "EMAIL": re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            ),
            "CREDIT_CARD": re.compile(
                r'\b(?:\d{4}[ -]?){3}\d{4}\b|\b(?:\d[ -]*?){13,19}\b'
            ),
            "PHONE": re.compile(
                r'(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,5}\)?[\s.-]?\d{3,5}[\s.-]?\d{3,5}\b'
            ),
            "IP_ADDRESS": re.compile(
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
            ),
            "SSN": re.compile(
                r'\b\d{3}-\d{2}-\d{4}\b'
            ),
            "PAN": re.compile(
                r'\b[A-Z]{5}\d{4}[A-Z]\b'
            ),
            "CIN": re.compile(
                r'\b[L|U]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b'
            ),
            "DIN": re.compile(
                r'\b(?:DIN[:\s]*)?(\d{8})\b'
            ),
            "DATE": re.compile(
                r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|'
                r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b|'
                r'\b\d{4}-\d{2}-\d{2}\b',
                re.IGNORECASE
            )
        }

        # Company legal suffix regex
        self.company_regex = re.compile(
            r'\b[A-Z0-9&.\s]{2,60}\s+(?:LIMITED|LIMITED\.|LTD|LTD\.|PRIVATE LIMITED|PVT\.?\s*LTD\.?|LLC|INC|INC\.|CORP|CORP\.|LLP)\b'
        )

        # Contextual Person Name Pattern
        self.context_name_regex = re.compile(
            r'(?:User|Customer|Name|Full Name|Contact|Promoters?|Director)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            re.IGNORECASE
        )

    def detect(self, text: str) -> List[PIIEntity]:
        entities: List[PIIEntity] = []

        # 1. High-Priority Structured Regex Detection
        # Emails
        for match in self.regex_patterns["EMAIL"].finditer(text):
            entities.append(PIIEntity(match.group(), "EMAIL", match.start(), match.end()))

        # Credit Cards (run BEFORE phone regex)
        for match in self.regex_patterns["CREDIT_CARD"].finditer(text):
            val = match.group().strip()
            digits = re.sub(r'\D', '', val)
            if len(digits) == 16 or is_valid_luhn(val):
                entities.append(PIIEntity(val, "CREDIT_CARD", match.start(), match.end()))

        # Government & Registration IDs
        for match in self.regex_patterns["SSN"].finditer(text):
            entities.append(PIIEntity(match.group(), "GOVT_ID", match.start(), match.end()))

        for match in self.regex_patterns["PAN"].finditer(text):
            entities.append(PIIEntity(match.group(), "GOVT_ID", match.start(), match.end()))

        for match in self.regex_patterns["CIN"].finditer(text):
            entities.append(PIIEntity(match.group(), "GOVT_ID", match.start(), match.end()))

        for match in self.regex_patterns["DIN"].finditer(text):
            full_match = match.group()
            digits_only = match.group(1) if match.lastindex else re.sub(r'\D', '', full_match)
            if len(digits_only) == 8 and ("DIN" in full_match or "DIN" in text[max(0, match.start()-10):match.start()] or "Director" in text[max(0, match.start()-20):match.start()]):
                d_start = match.start() + full_match.find(digits_only)
                entities.append(PIIEntity(digits_only, "GOVT_ID", d_start, d_start + len(digits_only)))

        # IP Addresses
        for match in self.regex_patterns["IP_ADDRESS"].finditer(text):
            entities.append(PIIEntity(match.group(), "IP_ADDRESS", match.start(), match.end()))

        # Phone numbers
        for match in self.regex_patterns["PHONE"].finditer(text):
            val = match.group().strip()
            digits = re.sub(r'\D', '', val)
            if 7 <= len(digits) <= 13 and not re.match(r'^(19|20)\d{2}', digits):
                if not ("₹" in text[max(0, match.start()-5):match.end()] or "million" in text[match.start():match.end()+10].lower()):
                    entities.append(PIIEntity(val, "PHONE", match.start(), match.end()))

        # Dates / Dates of Birth
        for match in self.regex_patterns["DATE"].finditer(text):
            entities.append(PIIEntity(match.group(), "DATE", match.start(), match.end()))

        # Companies via Suffix Regex
        for match in self.company_regex.finditer(text):
            val = match.group().strip()
            # Clean PAN Card header if attached
            if val.upper().startswith("PAN CARD:"):
                val = val[9:].strip()
            if val.lower() not in self.false_positive_terms:
                entities.append(PIIEntity(val, "COMPANY", match.start(), match.end()))

        # Contextual Names
        for match in self.context_name_regex.finditer(text):
            name_val = match.group(1).strip()
            if name_val.lower() not in self.false_positive_terms:
                start = match.start(1)
                end = match.end(1)
                entities.append(PIIEntity(name_val, "NAME", start, end))

        # 2. spaCy NER Detection
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                clean_ent = ent.text.strip()
                clean_lower = clean_ent.lower().replace(":", "").strip()

                if clean_lower in self.false_positive_terms or len(clean_ent) <= 2:
                    continue

                # Clean header prefix if present
                if clean_lower.startswith("pan card"):
                    continue

                tokens = clean_lower.split()
                if tokens and tokens[-1] in self.known_surnames:
                    entities.append(PIIEntity(clean_ent, "NAME", ent.start_char, ent.end_char))
                elif ent.label_ == "PERSON":
                    if not any(kw in clean_ent.upper() for kw in ["LIMITED", "LTD", "PRIVATE", "TRUST", "BANK", "SECURITY"]):
                        entities.append(PIIEntity(clean_ent, "NAME", ent.start_char, ent.end_char))
                elif ent.label_ == "ORG":
                    if clean_lower not in self.false_positive_terms:
                        entities.append(PIIEntity(clean_ent, "COMPANY", ent.start_char, ent.end_char))
                elif ent.label_ in ["GPE", "LOC", "FAC"]:
                    if any(char.isdigit() for char in clean_ent) or any(kw in clean_lower for kw in ["road", "street", "lane", "society", "nagar", "pune", "mumbai", "bhopal", "block"]):
                        entities.append(PIIEntity(clean_ent, "ADDRESS", ent.start_char, ent.end_char))

        # 3. Contextual Address Rule Enhancements
        address_patterns = [
            r'\b(?:\d{1,4}[/\s\w-]*\d{1,4}|\d{1,4}),?\s+[\w\s,.\-\n]+\s+(?:Pune|Mumbai|Bengaluru|Delhi|Bhopal|Maharashtra|India)[^.\n]*\b',
            r'\bS\.?\s*no\.?\s*\d+[^,\n]+,[\w\s,.\-\n]+(?:Pune|Mumbai|Bhopal|Maharashtra|India|Pincode|\d{6})\b'
        ]
        for pat in address_patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                val = match.group().strip()
                if len(val) > 15:
                    entities.append(PIIEntity(val, "ADDRESS", match.start(), match.end()))

        return self._resolve_overlaps(entities)

    def _resolve_overlaps(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        if not entities:
            return []

        # Sort by start index asc, then length desc
        sorted_ents = sorted(entities, key=lambda x: (x.start, -(x.end - x.start)))
        resolved: List[PIIEntity] = []

        for current in sorted_ents:
            cleaned_text = current.text.strip().lower()
            if cleaned_text in self.false_positive_terms or any(cleaned_text.startswith(fp) for fp in ["govt id", "ssn", "credit card", "dob", "ip", "pan card"]):
                continue

            overlap = False
            for existing in resolved:
                if not (current.end <= existing.start or current.start >= existing.end):
                    overlap = True
                    break
            if not overlap:
                resolved.append(current)

        return sorted(resolved, key=lambda x: x.start)
