import datetime
import re

def extract_target_dates(claim_text: str, reference_date: datetime.date = None):
    """
    Extracts target dates and relative day references ('tomorrow', 'today', '14/8/2026') from text.
    """
    if reference_date is None:
        from src.patches import get_reference_date
        reference_date = get_reference_date(reference_date)

    claim_lower = claim_text.lower()
    target_date = None

    # 1. Relative day keywords
    if "tomorrow" in claim_lower or "tmr" in claim_lower or "next day" in claim_lower:
        target_date = reference_date + datetime.timedelta(days=1)
    elif "today" in claim_lower:
        target_date = reference_date
    elif "yesterday" in claim_lower:
        target_date = reference_date - datetime.timedelta(days=1)

    # 2. Explicit numeric date patterns like 14/8/2026, 14-08-2026, 14.8.2026
    match_dmy = re.search(r'\b(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{4})\b', claim_text)
    if match_dmy:
        day, month, year = int(match_dmy.group(1)), int(match_dmy.group(2)), int(match_dmy.group(3))
        try:
            target_date = datetime.date(year, month, day)
        except ValueError:
            pass

    # 3. Explicit month name patterns like '14 August 2026', 'August 14, 2026'
    months_map = {
        'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
        'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
        'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9, 'october': 10, 'oct': 10,
        'november': 11, 'nov': 11, 'december': 12, 'dec': 12
    }
    
    match_name = re.search(r'\b(\d{1,2})\s*(?:st|nd|rd|th)?\s+([a-zA-Z]+)(?:\s+(\d{4}))?\b', claim_text, re.IGNORECASE)
    if match_name and not target_date:
        day = int(match_name.group(1))
        month_str = match_name.group(2).lower()
        year = int(match_name.group(3)) if match_name.group(3) else reference_date.year
        if month_str in months_map:
            try:
                target_date = datetime.date(year, months_map[month_str], day)
            except ValueError:
                pass

    if not target_date:
        return {
            "target_date_obj": None,
            "is_date_specific_claim": False,
            "strict_date_strings": []
        }

    iso_str = target_date.strftime("%Y-%m-%d")
    dmy_str = target_date.strftime("%d/%m/%Y")
    dmy_short = f"{target_date.day}/{target_date.month}/{target_date.year}"
    readable_str = target_date.strftime("%d %B %Y").lower()
    readable_alt = target_date.strftime("%B %d, %Y").lower()

    month_name_lower = target_date.strftime("%B").lower()
    # Dynamic date patterns using the actual parsed date
    strict_date_strings = [
        iso_str, dmy_str, dmy_short, readable_str, readable_alt,
        f"{target_date.day}/{target_date.month}/{target_date.year}",
        f"{target_date.day} {month_name_lower} {target_date.year}"
    ]

    is_today = (target_date == reference_date)
    is_future = (target_date > reference_date)
    is_past = (target_date < reference_date)

    return {
        "target_date_obj": target_date,
        "target_date_str_iso": iso_str,
        "target_date_str_dmy": dmy_str,
        "target_date_str_readable": target_date.strftime("%d %B %Y"),
        "is_date_specific_claim": True,
        "strict_date_strings": strict_date_strings,
        "is_today": is_today,
        "is_future": is_future,
        "is_past": is_past,
        "is_future_or_today": is_future or is_today
    }
