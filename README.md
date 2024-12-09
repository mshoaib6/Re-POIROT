# Running this algorithm

This algorithm runs the POIROT algorithm on a provenance graph against a query graph. Paste the provenance and query graph files into the root directory (see accepted formats below). To run the algorithm, use `python main.py <provenance graph file> <query graph file> <threshold>`.

# Datasets
Our re-implementation of POIROT was evaluated on open-source datasets from Darpa and the research community. You can access these datasets using the following links.

## Darpa OpTC
```bash
https://github.com/FiveDirections/OpTC-data
```

## Darpa E3
```bash
https://drive.google.com/drive/folders/1fOCY3ERsEmXmvDekG-LUUSjfWs6TRdp
```

## Streamspot
```bash
https://github.com/sbustreamspot/sbustreamspot-data
```

# Accepted Formats
Networkx graph in pickle format with file ending `.pkl`.

Text, with each line following this format:

TYPE:name->TYPE:name

For example:
PROCESS:myprocess->FILE:myfile

The arrow represents an outgoing edge from the entity on the left to the entity on the right.

# How to go from raw dataset to the format accepted by our code?

Step 1: Download the dataset(s) from the provided links.
Step 2: Convert the DARPA datasets to .pkl format using the parsers. Streamspot dataset can be pre-processed using the provided parser.
Step 3: Crate a query graph using the format above, a one-hop sample generic graph to test the system is provided in test.txt. More complex graphs with higher hop counts will take more time to run.
Step 4: To run the algorithm, use `python main.py <provenance graph file> <query graph file> <threshold>`, e.g., for the provided example, run `python main.py e3_chunk.pkl query1-test.txt 0.35`. 
The terminal will output the alignment score and the exact aligned nodes.


# Contributing

We welcome all feedback and contributions. If you wish to file a bug or enhancement proposal or have other questions, please use the Github Issue. If you'd like to contribute code, please open a Pull Request.

