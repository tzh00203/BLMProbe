import operator


def sort_dict(my_dict):
    sorted_list = sorted(my_dict.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dict = {}
    for [key, value] in sorted_list:
        sorted_dict[key] = value
    return sorted_dict
