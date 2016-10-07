import re

def filter(source, meta={}):
    list = re.findall(r'<a[^>]+href=[^>]+>', source)
    if list:
        return len(list)
    else:
        return 0
