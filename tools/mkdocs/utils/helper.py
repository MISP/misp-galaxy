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


def create_bar_chart(x_axis, y_axis, values, log=False):
    if not log:
        chart = f"| No. | {x_axis} | {y_axis} {{ .bar-chart }}|\n"
    else:
        chart = f"| No. | {x_axis} | {y_axis} {{ .log-bar-chart }}|\n"
    chart += f"|----|--------|-------|\n"
    for i, x, y in enumerate(values):
        chart += f"| {i+1} | {x} | {y} |\n"
    return chart

def create_pie_chart(sector, unit, values):
    chart = f"| No. | {sector} | {unit} {{ .pie-chart }}|\n"
    chart += f"|----|--------|-------|\n"
    for i, x, y in enumerate(values):
        chart += f"| {i+1} | {x} | {y} |\n"
    return chart
