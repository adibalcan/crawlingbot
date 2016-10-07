# Make unique list and preserve items order
def unique(list):
    seen = set()
    uniqueList = [item for item in list if not (item in seen or seen.add(item))]
    return uniqueList