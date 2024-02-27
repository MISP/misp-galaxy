import operator

def get_top_x(dict, x, big_to_small=True):
    sorted_dict = sorted(
        dict.items(), key=operator.itemgetter(1), reverse=big_to_small
    )[:x]
    top_x = [key for key, value in sorted_dict]
    top_x_values = sorted(dict.values(), reverse=big_to_small)[:x]
    return top_x, top_x_values


def name_to_section(name):
    placeholder = "__TMP__"
    return (
        name.lower()
        .replace(" - ", placeholder)  # Replace " - " first
        .replace(" ", "-")
        .replace("/", "")
        .replace(":", "")
        .replace(placeholder, "-")
    )  # Replace the placeholder with "-"