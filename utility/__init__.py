import uuid

def generate_uuid(length=8, upper=True):
    uid = uuid.uuid4().hex
    if length:
        uid = uid[:length]
    return uid.upper() if upper else uid

def parse_float(value, default=0, allow_negative=True):
    try:
        result = float(value) if value else default
    except ValueError:
        return None
    if not allow_negative and result is not None and result < 0:
        return None
    return result

def fmt_num(value):
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")
    
def truncate(text, limit=42):
    if len(text) <= limit:
        return text
    trimmed = text[:limit - 2]
    if trimmed[-1] == " ":
        trimmed = trimmed[:-1] + "."
    return trimmed + ".."