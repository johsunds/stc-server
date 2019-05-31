
def lookup_key_sequence(keys, d):
    if isinstance(keys, tuple) or isinstance(keys, list):
        for k in keys:
            d = d[k]
        return d
    else:
        return d[keys]