# Generation analysis toolkit
Collection of tools for the analysis of graph branching. Supports atm. Generations, Order, Strahler Order and ID assignment.
Build to work on GraphViz output from https://github.com/phcerdan/SGEXT

## How does it work?
- Reads supplied .dot graph into networkx representation
- Walks through graph, assigning labels to edges according to one or more of the classification metrics
- Outputs labeled graph (.dot and .nrrd) or analysis results as .csv

## Input
- .dot graph containing nodes, edges and coordinate labels (graph **must** be a (rooted) tree i.e. may **not** contain any parallel edges/circular paths in the graph)
- output filename
- Analysis mode
- Volume size
- Volume offset (for .nrrd header)
- root node of graph
- voxel edge length (only symmetrical voxels are supported) for .nrrd header and length calculation (optional, if not supplied, value will be set to 1)
- .csv containing RGB values (comma separated, one RGB color per line) for coloring the output graph (optional) 


## Output
- .dot graph
- .png image of graph
- .nrrd representation of graph (can be stretched back over initial volume image thinned by SGEXT)
- .csv containing graph data

## Usage
### Modes
- 0 = Generation analysis (Output = .dot, .png, .nrrd) 
- 1 = Order (Output = .dot, .png, .nrrd)
- 2 = Strahler Order (Output = .dot, .png, .nrrd)
- 3 = ID assignment (Output = .dot, .png, .nrrd)
- 4 = Comparative analysis (Does all the classification methods plus edge length analysis, outputs results as .csv)

`python genana.py graph.dot, outputfile, analysis mode (number), label root node, volume dimension x, volume dimension y, volume dimension z, offset x, offset y, offset z, (optional) voxel size, (optional) color map as .csv`

### Example
For an Order analysis of the file graph.dot, target = test_run, root node = 0, volume size = 10 * 10 * 10 voxels, offset = 0, 0, 0 voxels, voxel size = 2 um, no extra color map

`python genana.py graph.dot, test_run, 1, 0, 10, 10, 10, 0, 0, 0, 2`

