import hashlib
import json

# Function to hash a string using SHA-1 and return its integer representation
def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode()).hexdigest(), 16)

# Helper method to check if a value is in the range (start, end]
def inbetween(k: int, start: int, end: int) -> bool:
    if start < end:
        return start < k <= end
    else:  # The interval wraps around 0
        return start < k or k <= end
    
def code_dict(d):
    try:
        clean_dict = {k.strip(): v for k, v in d.items()}
        return json.dumps(clean_dict)
    except (TypeError, ValueError) as e:
        print(f"Error coding dictionary: {e}")
        return ''

    
def decode_dict(dict):
    try:
        return json.loads(dict)
    except (TypeError, ValueError) as e:
        print(f"Error decoding json string: {e}")
        return {}