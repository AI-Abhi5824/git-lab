import re
import string


PRN_PATTERN = re.compile(r"\b(\d{8,12})\b")


def clean_text(text: str) -> str:
    if not text:
        return ""
    lower_text = text.lower().strip()
    translator = str.maketrans("", "", string.punctuation)
    return lower_text.translate(translator)


def extract_prn(text: str):
    cleaned = clean_text(text)
    match = PRN_PATTERN.search(cleaned)
    return match.group(1) if match else None


def validate_prn(prn: str) -> bool:
    return bool(prn and re.fullmatch(r"\d{8,12}", prn))
