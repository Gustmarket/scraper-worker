
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
