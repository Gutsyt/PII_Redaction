from src.evaluator import GroundTruthSample

def get_benchmark_dataset():
    return [
        GroundTruthSample(
            sample_id="ticket_log_1",
            text=(
                "Rashi Patil: John Doe\n"
                "rashhi.patil@gmail.com: john.doe@example.com\n"
                "Rohan Dey: Peter Parker\n"
                "rohan.dey@gmail.com: peter.parker@example.com\n"
                "+91 9876543210: +91 1234567645\n"
                "Ticket #10492 created for order #INV-9921."
            ),
            ground_truth_entities=[
                {"text": "Rashi Patil", "type": "NAME"},
                {"text": "John Doe", "type": "NAME"},
                {"text": "rashhi.patil@gmail.com", "type": "EMAIL"},
                {"text": "john.doe@example.com", "type": "EMAIL"},
                {"text": "Rohan Dey", "type": "NAME"},
                {"text": "Peter Parker", "type": "NAME"},
                {"text": "rohan.dey@gmail.com", "type": "EMAIL"},
                {"text": "peter.parker@example.com", "type": "EMAIL"},
                {"text": "+91 9876543210", "type": "PHONE"},
                {"text": "+91 1234567645", "type": "PHONE"},
            ],
            non_pii_tokens=["Ticket #10492", "order #INV-9921"]
        ),
        GroundTruthSample(
            sample_id="ticket_log_2",
            text=(
                "Customer: Vishal Singh, Email: vishal.singh@example.com, Phone: +91 9988776655.\n"
                "Address: 45 Park Avenue, Block C, Bandra West, Mumbai 400050, India.\n"
                "Govt ID / SSN: 324-55-9102, DOB: 06/05/2000, Credit Card: 4532-8910-4421-9018, IP: 192.168.1.104.\n"
                "Company: Acme Solutions Pvt Ltd. Order Number: 994812."
            ),
            ground_truth_entities=[
                {"text": "Vishal Singh", "type": "NAME"},
                {"text": "vishal.singh@example.com", "type": "EMAIL"},
                {"text": "+91 9988776655", "type": "PHONE"},
                {"text": "45 Park Avenue, Block C, Bandra West, Mumbai 400050, India", "type": "ADDRESS"},
                {"text": "324-55-9102", "type": "GOVT_ID"},
                {"text": "06/05/2000", "type": "DATE"},
                {"text": "4532-8910-4421-9018", "type": "CREDIT_CARD"},
                {"text": "192.168.1.104", "type": "IP_ADDRESS"},
                {"text": "Acme Solutions Pvt Ltd", "type": "COMPANY"}
            ],
            non_pii_tokens=["Order Number: 994812"]
        ),
        GroundTruthSample(
            sample_id="rhp_prospectus_snippet",
            text=(
                "KSH INTERNATIONAL LIMITED (Corporate Identity Number: U28129PN1979PLC141032).\n"
                "Registered Office: 11/3, 11/4 and 11/5, Village Birdewadi, Chakan Taluka - Khed, Pune – 410 501, Maharashtra, India.\n"
                "Compliance Officer: Sarthak Malvadkar, Telephone: +91 20 45053237, Email: cs.connect@kshinternational.com.\n"
                "Our Promoters: Kushal Subbayya Hegde, Pushpa Kushal Hegde, Rajesh Kushal Hegde, Rohit Kushal Hegde, Rakhi Girija Shetty.\n"
                "Director DIN: 00135070. PAN Card: NBWPS1951N, Name: VISHAL SINGH, DOB: 06/05/2000."
            ),
            ground_truth_entities=[
                {"text": "KSH INTERNATIONAL LIMITED", "type": "COMPANY"},
                {"text": "U28129PN1979PLC141032", "type": "GOVT_ID"},
                {"text": "11/3, 11/4 and 11/5, Village Birdewadi, Chakan Taluka - Khed, Pune – 410 501, Maharashtra, India", "type": "ADDRESS"},
                {"text": "Sarthak Malvadkar", "type": "NAME"},
                {"text": "+91 20 45053237", "type": "PHONE"},
                {"text": "cs.connect@kshinternational.com", "type": "EMAIL"},
                {"text": "Kushal Subbayya Hegde", "type": "NAME"},
                {"text": "Pushpa Kushal Hegde", "type": "NAME"},
                {"text": "Rajesh Kushal Hegde", "type": "NAME"},
                {"text": "Rohit Kushal Hegde", "type": "NAME"},
                {"text": "Rakhi Girija Shetty", "type": "NAME"},
                {"text": "00135070", "type": "GOVT_ID"},
                {"text": "NBWPS1951N", "type": "GOVT_ID"},
                {"text": "VISHAL SINGH", "type": "NAME"},
                {"text": "06/05/2000", "type": "DATE"}
            ],
            non_pii_tokens=["Section 32 of Companies Act, 2013", "100% Book Built Offer"]
        )
    ]
