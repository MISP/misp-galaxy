import operator


def get_top_x(dict, x, big_to_small=True):
    sorted_dict = sorted(
        dict.items(), key=operator.itemgetter(1), reverse=big_to_small
    )[:x]
    top_x = {key: value for key, value in sorted_dict}
    return top_x


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


def create_bar_chart(x_axis, y_axis, values, log=False, galaxy=False):
    if not log:
        chart = f"| No. | {x_axis} | {y_axis} {{ .bar-chart }}|\n"
    else:
        chart = f"| No. | {x_axis} | {y_axis} {{ .log-bar-chart }}|\n"
    chart += f"|----|--------|-------|\n"
    for i, (x, y) in enumerate(values.items()):
        if galaxy:
            chart += f"| {i+1} | {galaxy_transform_to_link(x)} | {y} |\n"
        else:
            chart += f"| {i+1} | {cluster_transform_to_link(x)} | {y} |\n"
    chart += "\n"
    return chart


def create_pie_chart(sector, unit, values):
    chart = f"| No. | {sector} | {unit} {{ .pie-chart }}|\n"
    chart += f"|----|--------|-------|\n"
    for i, (x, y) in enumerate(values.items()):
        chart += f"| {i+1} | {x} | {y} |\n"
    chart += "\n"
    return chart


def cluster_transform_to_link(cluster, uuid=False):
    placeholder = "__TMP__"
    section = (
        cluster.value.lower()
        .replace(" - ", placeholder)  # Replace " - " first
        .replace(" ", "-")
        .replace("/", "")
        .replace(":", "")
        .replace(placeholder, "-")
    )
    galaxy_folder = cluster.galaxy.json_file_name.replace(".json", "")
    if uuid:
        return f"[{cluster.value} ({cluster.uuid})](../../{galaxy_folder}/index.md#{section})"
    else:
        return f"[{cluster.value}](../../{galaxy_folder}/index.md#{section})"


def galaxy_transform_to_link(galaxy):
    galaxy_folder = galaxy.json_file_name.replace(".json", "")
    return f"[{galaxy.galaxy_name}](../../{galaxy_folder}/index.md)"


def generate_relations_table(cluster):
    relationships = cluster.relationships
    markdown = ""
    markdown += f"[Hide Navigation](#){{ .md-button #toggle-navigation }}\n"
    markdown += f"[Hide TOC](#){{ .md-button #toggle-toc }}\n"
    markdown += f"<div class=\"clearfix\"></div>\n"
    markdown += f"# {cluster.value} ({cluster.uuid}) \n\n"
    markdown += f"{cluster.description} \n\n"
    markdown += "|Cluster A | Galaxy A | Cluster B | Galaxy B | Level { .graph } |\n"
    markdown += "| --- | --- | --- | --- | --- |\n"
    for from_cluster, to_cluster, level in relationships:
        from_galaxy = from_cluster.galaxy
        if to_cluster.value != "Private Cluster":
            to_galaxy = to_cluster.galaxy
            markdown += f"{cluster_transform_to_link(from_cluster, uuid=True)} | {galaxy_transform_to_link(from_galaxy)} | {cluster_transform_to_link(to_cluster, uuid=True)} | {galaxy_transform_to_link(to_galaxy)} | {level}\n"
        else:
            markdown += f"{cluster_transform_to_link(from_cluster, uuid=True)} | {galaxy_transform_to_link(from_galaxy)} | {to_cluster.value} ({to_cluster.uuid}) | Unknown | {level}\n"
    return markdown
