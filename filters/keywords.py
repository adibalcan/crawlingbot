import re

def filter(source, meta={}):
    # http://stackoverflow.com/a/7259618/769677
    match = re.search(r'<meta(?=[^>]*name\s*=\s*("|\')\s*keywords\s*\1)\s+[^>]*content\s*=\s*("|\')([^>\2]*?)\2', source,  re.IGNORECASE | re.DOTALL)
    keywords = []
    maxLength = 255
    if match and len(match.groups()) == 3:
        rawKeywords =  match.group(3)
        rawKeywords = rawKeywords[:maxLength] if len(rawKeywords) > maxLength else rawKeywords
        keywords = rawKeywords.split(',')
        keywords = list(set(keywords))
        keywords = [key.strip() for key in keywords]
    return keywords
