import re

def filter(source, meta={}):
    list = re.findall(r'<img[^>]+>', source)
    if list:
        return len(list)
    else:
        return 0