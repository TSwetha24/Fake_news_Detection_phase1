import re

def test_entity_matcher(claim_text, articles):
    claim_lower = claim_text.lower()
    subject = None
    role = None

    match_role = re.search(r'\b([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+(?:is|was|became|appointed as|selected as|sworn in as)\s+(?:the\s+)?(cm|chief minister|pm|prime minister|governor|president|ceo|minister)\b', claim_lower)
    if match_role:
        subject = match_role.group(1).strip()
        role = match_role.group(2).strip()

    subject_aliases = {subject}
    if "vijay" in claim_lower:
        subject_aliases.update(["vijay", "joseph vijay", "c. joseph vijay", "c joseph vijay", "thalapathy vijay"])

    print(f"Subject parsed: '{subject}', Role: '{role}', Aliases: {subject_aliases}")

    ignored_tokens = {"c", "m", "k", "v", "dr", "mr", "mrs", "of", "for", "tn", "tamil", "nadu", "state", "delhi", "today", "tomorrow", "is", "the", "in", "to"}

    for art in articles:
        title = art.get('title', '')
        text = title.lower()

        # Clean visitor matching: check if headline says "Visitor meets/presents/submits to CM [Other]"
        # e.g., "Suriya's 'Karuppu' team meets honorable Tamil Nadu CM Vijay"
        # Match visitor word
        visitor_match = re.search(r'\b([a-zA-Z]+)', text)
        visitor = visitor_match.group(1) if visitor_match else ""

        # Check if CM name is mentioned
        cm_match = re.search(r'\b(?:cm|chief minister)\s+(?:thalapathy\s+)?([a-zA-Z]+)', text)
        actual_cm = cm_match.group(1) if cm_match else ""

        print(f"Article: '{title}'")
        print(f"  Extracted Visitor: '{visitor}', Extracted CM: '{actual_cm}'")

        if visitor in subject_aliases and actual_cm and actual_cm not in subject_aliases and actual_cm not in ignored_tokens:
            print(f"  -> CONTRADICTION! {visitor.title()} met CM {actual_cm.title()}")
        elif any(alias in text for alias in subject_aliases) and any(r_kw in text for r_kw in ["cm", "chief minister", "govt", "government", "ministry"]):
            if actual_cm and actual_cm not in subject_aliases and actual_cm not in ignored_tokens:
                print(f"  -> CONTRADICTION! Reports confirm {actual_cm.title()} as CM")
            else:
                print(f"  -> DIRECT SUPPORT for {subject.title()} as CM")

if __name__ == "__main__":
    print("--- TEST 1: Suriya is the CM of TamilNadu ---")
    test_entity_matcher("Suriya is the CM of TamilNadu", [
        {"title": "Suriya's 'Karuppu' team meets honorable Tamil Nadu CM Vijay"},
        {"title": "Jana Nayagan: Tamil Nadu CM Thalapathy Vijay Almost Ended Film Career"}
    ])

    print("\n--- TEST 2: vijay is the cm of TamilNadu ---")
    test_entity_matcher("vijay is the cm of TamilNadu", [
        {"title": "Tamil Nadu CM Vijay to host maiden Vetri Tamil Nadu Investors Conclave"},
        {"title": "CM Vijay administers State-level mass pledge for a Drug Free Tamil Nadu"}
    ])
