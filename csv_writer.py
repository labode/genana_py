import networkx as nx


def write(graph, target_file, labels):

    # Initiate File
    filename = str(target_file) + ".csv"
    output_file = open(filename, "w")

    # Write header
    output_file.write("start; end;")
    i = len(labels)
    for label in labels:
        i -= 1
        output_file.write(' ' + label)
        if i > 0:
            output_file.write(';')
    output_file.write("\n")

    # Write data
    # Get all edges
    edges = list(nx.edges(graph))
    for edge in edges:
        output_file.write(edge[0] + '; ' + edge[1] + ';')
        # Write each labels content
        i = len(labels)
        for label in labels:
            i -= 1
            output_file.write(' ' + str(graph[edge[0]][edge[1]][label]))
            if i > 0:
                output_file.write(';')
        output_file.write("\n")

    output_file.close()
