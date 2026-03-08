import uuid

def generate_uuid(length=8, upper=True):
    uid = uuid.uuid4().hex
    if length:
        uid = uid[:length]
    return uid.upper() if upper else uid

def parse_float(value, default=0):
    try:
        return float(value) if value else default
    except ValueError:
        return None
    
def truncate(text, limit=42):
    if len(text) <= limit:
        return text
    trimmed = text[:limit - 2]
    if trimmed[-1] == " ":
        trimmed = trimmed[:-1] + "."
    return trimmed + ".."