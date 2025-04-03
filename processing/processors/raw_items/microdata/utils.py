import re

from processing.data.utils import flatten_list

def cleanup_str(string_var):
    if string_var is None:
        return None
    if not hasattr(string_var, 'strip'):
        return string_var
    return re.sub("\n", "", string_var.strip())


def map_microdata_node(node, key='name'):
    value = None
    if node is None:
        value = None
    elif type(node) == dict:
        properties = node.get('properties')
        if properties is not None:
            value = properties.get(key, '')
        else:
            value = node.get(key, '')
    else:
        value = node
    return value


# todorefactor this for microdata and json-ld
def better_map(raw_val, key='name'):
    nodes = None
    if raw_val is None:
        return None
    if type(raw_val) == list:
        nodes = raw_val
    else:
        nodes = [raw_val]

    mapped_nodes = list(map(lambda n: map_microdata_node(n, key), nodes))
    flattened_nodes = flatten_list(mapped_nodes)
    res = list(filter(lambda n: n is not None and n != "", flattened_nodes))
    res = list(set(list(map(lambda n: cleanup_str(n), res))))

    if len(res) == 1:
        return res[0]
    return res
