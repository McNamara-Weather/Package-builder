# List of allowed capitalized words (so legitimate weather queries like "Warsaw Poland" aren't blocked)
ALLOWED_CAPITALIZED_TERMS = {
    "poland", "warsaw", "gdansk", "krakow", "baltic", "sea", "europe", "weather", 
    "company", "january", "february", "march", "april", "may", "june", "july", 
    "august", "september", "october", "november", "december", "monday", "tuesday", 
    "wednesday", "thursday", "friday", "saturday", "sunday"
}

def check_for_restricted_data(text):
    """
    Scans input text for PII, Company Names, and Personal Human Names.
    Returns (True, "Data Type") if detected, otherwise (False, None).
    """
    # 1. Structural Patterns (SSN, Cards, Email, Phone, Corporate Suffixes)
    patterns = {
        "Social Security Number (SSN)": r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',
        "Credit/Debit Card Number": r'\b(?:\d[ -]*?){13,16}\b',
        "Email Address": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "Phone Number": r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "Company / Organization Name": r'\b[A-Za-z0-9&.\'-]+\s+(?:Inc|Inc\.|LLC|Corp|Corp\.|Corporation|Ltd|Ltd\.|Limited|Co|Company|Group|Holdings|GmbH|PLC)\b'
    }
    
    for data_type, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return True, data_type

    # 2. Personal Human Name Pattern (Detects "Firstname Lastname" like John Sullivan)
    # Finds two consecutive Title-Case words
    potential_names = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text)
    for pair in potential_names:
        words = pair.lower().split()
        # If neither word is a known location/weather term, treat it as a Person's Name
        if not any(word in ALLOWED_CAPITALIZED_TERMS for word in words):
            return True, f"Person Name ({pair})"
            
    return False, None
