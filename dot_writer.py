import numpy as np
import networkx as nx
from node_finder import find_new_neighbors
import pydot
import csv


def read_colormap(colormap):
    colors = []

    with open(colormap) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            # We exclude white as a label color as we are printing on a white background
            if row[0] == '0' and row[1] == '0' and row[2] == '0':
                continue

            # Convert to hex code (and invert to match it to the later interpretation in makefile)
            r = hex(255 - int(row[0]))
            g = hex(255 - int(row[1]))
            b = hex(255 - int(row[2]))

            # Add leading # and remove leading 0x from hex
            colors.append('#' + r[2:] + g[2:] + b[2:])

    return colors


def write(nx_graph, target_file, root_node, color=True, label='Gen', colormap=''):
    # TODO: Check if colormap has enough entries to be used with the given graph?
    if len(colormap) == 0:
        colors = np.array(["red", "green", "blue", "yellow", "cyan", "magenta"], str)
    else:
        colors = read_colormap(colormap)
        # If a color map has been supplied, we can be sure that a colored output is requested
        color = True

    filename = str(target_file) + ".dot"
    output_file = open(filename, "w")

    output_file.write("graph G {\n")

    # Get all nodes, print those out
    nodes = nx.nodes(nx_graph)
    for i in nodes:
        output_file.write(str(i) + ";\n")

    # Write each edge pair with generation marking, hierarchically ordered
    visited = [root_node]
    nodes = [root_node]

    while len(nodes) != 0:
        nn = []
        for i in nodes:
            visited.append(i)
            neighbors = find_new_neighbors(i, visited, nx_graph)
            for j in neighbors:
                if color == bool(True):
                    col = int(nx_graph[i][j][label]) - 1
                    col_str = " color = " + str(colors[col])
                else:
                    col_str = ""
                output_file.write(
                    str(i) + "--" + str(j) +
                    " [ label = \"" + label + " " + str(nx_graph[i][j][label]) +
                    "\"" + col_str + "];\n"
                )
                nn.append(j)
        nodes = nn

    output_file.write("}")
    output_file.close()

    # Make PNG from graph
    (output_graph,) = pydot.graph_from_dot_file(filename)
    output_graph.write_png(str(target_file) + ".png")
