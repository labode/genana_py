import networkx as nx
import sys


def read_graph(file):
    # Read graph from .dot file using pydot and turn it into a networkx graph
    dot_graph = nx.drawing.nx_pydot.read_dot(dotfile)

    return dot_graph


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dotfile = sys.argv[1]
    graph = read_graph(dotfile)
    if len(graph) != 0:
        print("Graph read")

