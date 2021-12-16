import networkx as nx


def write(graph, target_file, labels):

    # Initiate File
    filename = str(target_file) + ".csv"
    output_file = open(filename, "w")

    # Write header
    output_file.write("start; end;")
    for label in labels:
        output_file.write(' ' + label + ';')
    output_file.write("\n")

    # Write data
    # Get all edges
    edges = list(nx.edges(graph))
    for edge in edges:
        output_file.write(edge[0] + '; ' + edge[1] + ';')
        # Write each labels content
        for label in labels:
            output_file.write(' ' + str(graph[edge[0]][edge[1]][label]) + ';')
        output_file.write("\n")

    output_file.close()
