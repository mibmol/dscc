def remove_key_from_list(key, list):
    result = []
    for item in list:
        item.pop(key, None)
        result.append(item)
    return result
