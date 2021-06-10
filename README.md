# Generation analysis toolkit
Collection of tools for the analysis of graph branching. Supports atm. Generations, Order, Strahler Order and ID assignment.
Build to work on GraphViz output from https://github.com/phcerdan/SGEXT

## How does it work?
- Reads supplied .dot graph into networkx representation
- Walks through graph, assigning labels to edges according to one or more of the classification metrics
- Outputs labeled graph (.dot and .nrrd) or analysis results as .csv

## Input
- .dot graph containing nodes, edges and coordinate labels


## Output
- .dot graph
- .png image of graph
- .nrrd representation of graph (can be strtched back over initial volume image thinned by SGEXT)
- .csv containing graph data

## Usage
### Modes
- 0 = Generation analysis (Output = .dot, .png, .nrrd) 
- 1 = Order (Output = .dot, .png, .nrrd)
- 2 = Strahler Order (Output = .dot, .png, .nrrd)
- 3 = ID assignment (Output = .dot, .png, .nrrd)
- 4 = Comparative analysis (Does all the classification methods plus edge length analysis, outputs results as .csv)

`python main.py graph.dot, outputfile, analysis mode (number), label root node, volume dimension x, volume dimension y, volume dimension z`

### Example
For an Order analysis of the file graph.dot, target = test_run, root node = 0, volume size = 10 * 10 * 10 voxels
`python main.py graph.dot, test_run, 1, 0, 10, 10, 10`

