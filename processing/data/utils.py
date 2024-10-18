import re

def filter_none(l):
    return list(filter(lambda x: x is not None, l))

def uniq_filter_none(l):
    return list(set(filter_none(l)))

def flatten_list(list_var):
    flattened = []
    for item in list_var:
        if type(item) == list:
            flattened += item
        else:
            flattened.append(item)
    return flattened

def format_float(value):
    if value == int(value):
        return str(int(value))
    else:
        return str(value)
    
def extract_floats(text):
    if text is None:
        return []
    pattern = r'[-+]?\d*\.\d+|\d+'  # Regular expression pattern for floats
    floats = re.findall(pattern, text.replace(',', '.').replace('_', '.'))
    return [float(num) for num in floats]