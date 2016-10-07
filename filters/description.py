import re

def filter(source, meta={}):
    # http://stackoverflow.com/a/7259618/769677
    match = re.search(r'<meta(?=[^>]*name\s*=\s*("|\')\s*description\s*\1)\s+[^>]*content\s*=\s*("|\')([^>\2]*?)\2', source, re.IGNORECASE | re.DOTALL)
    description = ''
    maxLength = 255
    if match and len(match.groups()) == 3:
        description = match.group(3)
        description = description[:maxLength] if len(description) > maxLength else description
    return description