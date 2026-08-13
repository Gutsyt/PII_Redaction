import random
import hashlib
from typing import Dict, List, Tuple
from faker import Faker
from src.detector import PIIEntity

class PIIRedactor:
    def __init__(self, mode: str = "synthetic", seed: int = None):
        self.mode = mode.lower()
        self.fake = Faker(['en_IN', 'en_US'])
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        # Session mapping for consistent replacements across the document/request
        self.entity_map: Dict[str, str] = {}

    def get_replacement(self, entity: PIIEntity) -> str:
        raw_text = entity.text.strip()
        if raw_text in self.entity_map:
            return self.entity_map[raw_text]

        if self.mode == "mask":
            replacement = f"[REDACTED_{entity.entity_type}]"
            self.entity_map[raw_text] = replacement
            return replacement

        # Deterministic seed per entity text so different entities get distinct fake names
        entity_hash = int(hashlib.md5(raw_text.encode('utf-8')).hexdigest(), 16) % (2**32)
        local_random = random.Random(entity_hash)
        self.fake.seed_instance(entity_hash)

        ent_type = entity.entity_type
        if ent_type == "NAME":
            replacement = self.fake.name()
        elif ent_type == "EMAIL":
            name_part = "".join(e for e in self.fake.name() if e.isalnum()).lower()
            replacement = f"{name_part}@example.com"
        elif ent_type == "PHONE":
            replacement = f"+91 {local_random.randint(7000000000, 9999999999)}"
        elif ent_type == "COMPANY":
            replacement = self.fake.company() + " Ltd."
        elif ent_type == "ADDRESS":
            replacement = f"{local_random.randint(10, 999)} {self.fake.street_name()}, {self.fake.city()}, {self.fake.state()} - {self.fake.postcode()}, India"
        elif ent_type == "GOVT_ID":
            letters = "".join(local_random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
            digits = "".join(local_random.choices("0123456789", k=4))
            checksum = local_random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            replacement = f"{letters}{digits}{checksum}"
        elif ent_type == "CREDIT_CARD":
            replacement = f"4532-{local_random.randint(1000,9999)}-{local_random.randint(1000,9999)}-{local_random.randint(1000,9999)}"
        elif ent_type == "DATE":
            replacement = self.fake.date_of_birth(minimum_age=25, maximum_age=60).strftime("%d/%m/%Y")
        elif ent_type == "IP_ADDRESS":
            replacement = f"198.51.100.{local_random.randint(1, 254)}"
        else:
            replacement = f"[REDACTED_{ent_type}]"

        self.entity_map[raw_text] = replacement
        return replacement

    def redact_text(self, text: str, entities: List[PIIEntity]) -> Tuple[str, List[Dict[str, str]]]:
        if not entities:
            return text, []

        sorted_entities = sorted(entities, key=lambda x: x.start, reverse=True)
        redacted_text = text
        changes = []

        for entity in sorted_entities:
            replacement = self.get_replacement(entity)
            orig = entity.text
            start, end = entity.start, entity.end
            
            redacted_text = redacted_text[:start] + replacement + redacted_text[end:]
            changes.append({
                "original": orig,
                "replacement": replacement,
                "type": entity.entity_type,
                "start": start,
                "end": end
            })

        return redacted_text, changes
