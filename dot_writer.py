import numpy as np
import networkx as nx
import pydot


def write(graph_data, target_file, color=True, label='Gen'):
    # TODO: Extend color map
    colors = np.array(["red", "green", "blue", "yellow", "cyan", "magenta"], str)

    filename = str(target_file) + ".dot"
    output_file = open(filename, "w")

    output_file.write("graph G {\n")

    # Get all nodes, print those out
    nodes = nx.nodes(graph_data)
    for i in nodes:
        output_file.write(str(i) + ";\n")

    # Write each edge pair with generation marking
    edges = list(nx.edges(graph_data))
    for edge in edges:
        if color == bool(True):
            col = int(graph_data[edge[0]][edge[1]][0][label]) - 1
            col_str = " color = " + str(colors[col])
        else:
            col_str = ""
        output_file.write(
            str(edge[0]) + "--" + str(edge[1]) +
            " [ label = \"" + label + " " + str(graph_data[edge[0]][edge[1]][0][label]) +
            "\"" + col_str + "];\n"
        )

    output_file.write("}")
    output_file.close()

    # Make PNG from graph
    (output_graph,) = pydot.graph_from_dot_file(filename)
    output_graph.write_png(str(target_file) + ".png")
