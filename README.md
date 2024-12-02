# Running this algorithm

This algorithm runs the POIROT algorithm on a provenance graph against a query graph. Paste the provenance and query graph files into the root directory (see accepted formats below). To run the algorithm, use `python main.py <provenance graph file> <query graph file> <threshold>`.

# Accepted Formats
Networkx graph in pickle format with file ending `.pkl`.

Text, with each line following this format:

TYPE:name->TYPE:name

For example:
PROCESS:myprocess->FILE:myfile

The arrow represents an outgoing edge from the entity on the left to the entity on the right.