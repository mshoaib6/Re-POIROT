from node import Node
import sys
import loaders
import poirot
import scores

def compare(query_node, provenance_node):
    if query_node.type == "FILE" and provenance_node.type == "FileObject":
        return query_node.label == provenance_node.label
    elif query_node.type == "PROCESS":
        return provenance_node.type == "SUBJECT_PROCESS"
    elif query_node.type == "IP":
        return provenance_node.type == "NetFlowObject"

def main():
    print("Initiating POIROT algorithm...")
    if len(sys.argv) != 4:
        print("python main.py <provenance graph file> <query graph file> <threshold>")
        exit(1)
    provenance_graph_file = sys.argv[1]
    query_graph_file = sys.argv[2]
    threshold = int(sys.argv[3])

    provenance_graph = loaders.load_graph(provenance_graph_file)
    query_graph = loaders.load_graph(query_graph_file)
    candidate_alignments = poirot.find_candidate_node_alignments_with_custom_comparison(query_graph, provenance_graph, compare)

    for i in range(len(query_graph.nodes)):
        seed_node = poirot.select_seed_node(candidate_alignments, i)
        subset_candidate_alignments = poirot.search_expansion(candidate_alignments, seed_node, query_graph, provenance_graph, threshold)
        if candidate_alignments.keys() != subset_candidate_alignments.keys() or any(len(candidates) == 0 for candidates in subset_candidate_alignments.values()):
            print("Couldn't find 1-1 matching of query to provenance graph.")
            continue
        graph_alignment = poirot.find_graph_alignment(query_graph, provenance_graph, threshold, seed_node, subset_candidate_alignments)
        print(f"Final node alignment: {graph_alignment}")
        alignment_score = scores.compute_alignment_score(query_graph, provenance_graph,
                                        graph_alignment, threshold)
        print("Alignment score of the node alignment: {0:0.6f}".format(alignment_score))
        if alignment_score >= 1.0/float(threshold):
            print("Alert! Attacker may be present.")
            return
        else:
            print("Could not find attacker, trying again with another seed node...")
    print("Attacker may not be present in the system.")

if __name__ == "__main__":
    main()