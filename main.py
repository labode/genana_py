import networkx as nx
import numpy as np
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
        else:
            print("Analysis type not supported")



