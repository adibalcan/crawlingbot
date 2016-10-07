import re

def filter(source, meta={}):
    # http://stackoverflow.com/a/7259618/769677
    match = re.search(r'<title>([^<]+)</title>', source, re.IGNORECASE | re.DOTALL)
    title = ''
    maxLength = 255
    if match and len(match.groups()) == 1:
        title = match.group(1)
        title = title[:maxLength] if len(title) > maxLength else title
    title = title.strip()
    return title
