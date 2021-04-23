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


def order_analysis(node):
    pos = leaf_node_finder(node)
    visited = []
    edges = np.array([], int)
    gen = 1

    # Only ascend from one point, if we have already visited n-1 of its neighbours; otherwise try other points first
    # We are done, when we reach the root node
    while len(pos) != 1 or pos[0] != node:
        add = []
        rm = []
        for i in pos:
            neighbors = list(nx.neighbors(graph, i))
            visited.append(i)

            rm_n = []
            for j in neighbors:
                if j in visited:
                    if j not in pos:
                        rm_n.append(j)
            for k in rm_n:
                neighbors.remove(k)

            if len(list(neighbors)) <= 1:
                print("The edge between node " + str(i) + " and " + str(neighbors[0]) + " has generation " + str(gen))
                edges = np.append(edges, [[[i, neighbors[0], gen]]])
                rm.append(i)
                add.append(neighbors[0])

        for i in add:
            if i not in pos:
                pos.append(i)

        for i in rm:
            pos.remove(i)
            if i not in visited:
                visited.append(i)

        gen += 1

    return edges


# TODO: Just like order, but after gen 1 only increment generation by one when two equal generations meet
def strahler_order(node):
    leaves = leaf_node_finder(node)

    print("Not done yet")


# just like genana, but every edge gets its unique id instead of a generation
# to be used for external grouping according to properties of the graph segments
# TODO: probably very over engineered
def give_id(node):
    unique_id = 0
    edges = np.array([], int)
    visited = [node]
    nodes = [node]

    while len(nodes) != 0:
        nn = []
        for i in nodes:
            visited.append(i)
            neighbors = new_neighbors(i, visited)
            for j in neighbors:
                print("Edge between " + str(i) + " and " + str(j) + " has id " + str(unique_id))
                edges = np.append(edges, [[[i, j, unique_id]]])
                nn.append(j)
                unique_id += 1
        nodes = nn

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


# Find the leaf nodes => Walk through tree til you can't walk no more
def leaf_node_finder(node):
    # TODO: read this maybe for more efficiency
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.chains.chain_decomposition.html#networkx.algorithms.chains.chain_decomposition
    touched = [node]
    to_search = [node]
    leaves = []

    while len(to_search) > 0:
        for i in list(to_search):
            to_search.remove(i)
            touched.append(str(i))
            neighbors = new_neighbors(i, touched)
            if len(neighbors) == 0:
                leaves.append(str(i))
            else:
                for j in neighbors:
                    to_search.append(j)

    return leaves


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
        elif int(analysis_type) == 1:
            edges_w_gens = order_analysis(root_node)
            write_dot(graph, edges_w_gens, True, "Ord")
        elif int(analysis_type) == 2:
            edges_w_gens = strahler_order(root_node)
            write_dot(graph, edges_w_gens, True, "Str_Ord")
        elif int(analysis_type) == 3:
            edges_w_gens = give_id(root_node)
            write_dot(graph, edges_w_gens, False, "Id")
        else:
            print("Analysis type not supported")
