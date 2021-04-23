import networkx as nx
import numpy as np
import pydot
import sys


def read_graph(file):
    # Read graph from .dot file using pydot and turn it into a networkx graph
    dot_graph = nx.drawing.nx_pydot.read_dot(file)

    return dot_graph


def generation_analysis(node):
    gen = 1
    edges = np.array([], int)
    visited = [node]
    nodes = [node]

    while len(nodes) != 0:
        nn = []
        for i in nodes:
            visited.append(i)
            neighbors = new_neighbors(i, visited)
            for j in neighbors:
                print("Edge between " + str(i) + " and " + str(j) + " has gen " + str(gen))
                edges = np.append(edges, [[[i, j, gen]]])
                nn.append(j)
        nodes = nn
        gen += 1

    return edges


# Return all neighbors excluding old (already known) ones (supplied in a list)
def new_neighbors(node, known):
    discovered = []

    neighbors = nx.neighbors(graph, node)
    for i in list(neighbors):
        if i in known:
            continue
        else:
            discovered.append(str(i))

    return discovered


# TODO: Is this really necessary? There must be something like this in numpy!
def reshape_array(array, width):
    size = array.size
    length = size//width

    array = array.reshape((length, width))

    return array


def write_dot(graph_data, edges, color=True, label='Gen'):
    colors = np.array(["red", "green", "blue", "yellow", "cyan", "magenta"], str)

    filename = "output_graph.dot"
    output_file = open(filename, "w")

    output_file.write("graph G {\n")

    # Get all nodes, print those out
    nodes = nx.nodes(graph_data)
    for i in nodes:
        output_file.write(str(i) + ";\n")

    edges = reshape_array(edges, 3)

    # Write each edge pair with generation marking
    for i in edges:
        if color == bool(True):
            col = int(i[2]) - 1
            col_str = " color = " + str(colors[col])
        else:
            col_str = ""
        output_file.write(
            str(i[0]) + "--" + str(i[1]) + " [ label = \"" + label + " " + str(i[2]) + "\"" + col_str + "];\n"
        )

    output_file.write("}")
    output_file.close()

    # Make PNG from graph
    (output_graph,) = pydot.graph_from_dot_file(filename)
    output_graph.write_png("output_graph.png")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dotfile = sys.argv[1]
    analysis_type = sys.argv[2]
    root_node = sys.argv[3]

    error = False

    if not dotfile or not analysis_type or not root_node:
        # TODO: Explain the needed parameters to the user
        print("Missing parameters")
        error = True

    if not error:
        graph = read_graph(dotfile)

        if int(analysis_type) == 0:
            edges_w_gens = generation_analysis(root_node)
            write_dot(graph, edges_w_gens)
        else:
            print("Analysis type not supported")



