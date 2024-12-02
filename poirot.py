import scores
import helpers

# step 1
def find_candidate_node_alignments(query_graph, provenance_graph):
    '''
    given a set of nodes from the query graph (G_q),
    find a candidate set of nodes in the actual
    provenance graph (G_p).

    params: query_graph -> networkx DiGraph representing query graph
            provenance_graph -> networkx DiGraph representing provenance graph
    returns: a dictionary like:
            {node_id : [node_alignments] where
            node_id is the node from query graph
            node_alignments is the list of nodes from the provenance graph
            that are aligned to nodes in the query graph
    ''' 
    query_types = {}
    for query_node_id in query_graph.nodes:
        query_node = query_graph.nodes[query_node_id]['node']
        query_node_type = query_node.type
        query_types[query_node_type] = query_types.get(query_node_type, []) + [query_node_id]
    
    candidate_alignments = {query_node_id: [] for query_node_id in query_graph.nodes}
    for provenance_node_id in provenance_graph.nodes:
        provenance_node = provenance_graph.nodes[provenance_node_id]['node']
        provenance_node_type = provenance_node.type
        if provenance_node_type in query_types:
            for query_node_id in query_types[provenance_node_type]:
                candidate_alignments[query_node_id] = candidate_alignments.get(query_node_id, []) + [provenance_node_id]

    return candidate_alignments

def find_candidate_node_alignments_with_custom_comparison(query_graph, provenance_graph, comparison_function):
    '''
    given a set of nodes from the query graph (G_q),
    find a candidate set of nodes in the actual
    provenance graph (G_p).

    params: query_graph -> networkx DiGraph representing query graph
            provenance_graph -> networkx DiGraph representing provenance graph
            comparison_function -> function that takes two Nodes as argument and returns true if they "align"
            and returns false if they don't
    returns: a dictionary like:
            {node_id : [node_alignments] where
            node_id is the node from query graph
            node_alignments is the list of nodes from the provenance graph
            that are aligned to nodes in the query graph
    ''' 
    candidate_alignments = {}
    for query_node_id in query_graph.nodes:
        query_node = query_graph.nodes[query_node_id]['node']
        for provenance_node_id in provenance_graph.nodes:
            provenance_node = provenance_graph.nodes[provenance_node_id]['node']
            if comparison_function(query_node, provenance_node):
                candidate_alignments[query_node_id] = candidate_alignments.get(query_node_id, []) + [provenance_node_id]
    
    return candidate_alignments

# step 2
def select_seed_node(candidate_alignments, index):
    '''
    params: candidate_alignments -> the dictionary representing alignments
            from nodes in the query graph to nodes in the provenance graph 
    returns: a seed node in G_q from which graph exploration
            should start.
    '''
    sorted_node_alignments = sorted(candidate_alignments,
            key=lambda k: len(candidate_alignments[k]))
    if index < len(sorted_node_alignments):
        return sorted_node_alignments[index]
    return sorted_node_alignments[-1]

# step 3
def search_expansion(candidate_alignments, seed_node, query_graph, provenance_graph, threshold):
    '''
    params: 
            candidate_alignments -> candidate alignments from nodes in G_q to nodes in G_p
            seed_node -> seed node in G_q from which graph exploration
            should start.
            query_graph -> networkx DiGraph representing query graph
            provenance_graph -> networkx DiGraph representing provenance graph
            threshold -> upper bound for number of distinct compromises attacker can reasonably exploit
    result: {node_id : [subset_node_alignments]} where node_id is the
            node from query graph.
            subset_node_alignments is the list of node alignments
            which are reachable from *seed node alignments* using a
            backward/forward search (this refines the original list of candidate alignments)
    '''
    reverse_provenance_graph = provenance_graph.reverse()

    # do forward and backward traversal
    all_nodes_visited = set()
    all_nodes = set(provenance_graph.nodes)
    query_nodes_to_visit = set(query_graph.nodes)
    start_nodes = candidate_alignments[seed_node]
    count_threshold = 20
    count = 0
    new_candidate_alignments = {}
    while len(query_nodes_to_visit) > 0 and count < count_threshold:
        count += 1
        for node in start_nodes:
            visited = set()
            helpers.do_dfs(provenance_graph, node, visited, threshold)
            backward_visited = set()
            helpers.do_dfs(reverse_provenance_graph, node, backward_visited, threshold)
            all_nodes_visited = all_nodes_visited.union(visited, backward_visited) 
        for query_node_alignment in candidate_alignments:
            intersection = list(set(candidate_alignments[query_node_alignment]).intersection(all_nodes_visited))
            if len(intersection) > 0:
                query_nodes_to_visit.discard(query_node_alignment)
                new_candidate_alignments[query_node_alignment] = new_candidate_alignments.get(query_node_alignment, []) + intersection
        if len(query_nodes_to_visit) > 0:
            # set start nodes to nodes adjacent to unvisited nodes but that have been visited in a previous traversal
            unvisited = all_nodes.difference(all_nodes_visited)
            start_nodes = []
            for node in unvisited:
                forward_neighbors = set(provenance_graph[node])
                reverse_neighbors = set(reverse_provenance_graph[node])
                neighbors = forward_neighbors.union(reverse_neighbors)
                visited_neighbors = neighbors.intersection(all_nodes_visited)
                start_nodes.extend(visited_neighbors)
    print("Printing candidate node alignment lengths: ")
    for node_alignment in new_candidate_alignments:
        print("{}: {}".format(node_alignment, len(new_candidate_alignments[node_alignment])))
    return new_candidate_alignments

# step 4
def find_graph_alignment(query_graph, provenance_graph, threshold, seed_node, candidate_alignments):
    '''
    params: 
            query_graph -> networkx DiGraph representing query graph
            provenance_graph -> networkx DiGraph representing provenance graph
            threshold -> upper bound for number of distinct compromises attacker can reasonably exploit
            seed_node -> seed node in G_q from which graph exploration
            should start.
            candidate_alignments -> candidate alignments from nodes in G_q to nodes in G_p
    result: {g_q : g_p}, a mapping from nodes in the query graph to nodes in the provenance graph, representing the best graph
            alignment for the given seed node
    '''
    aligned_nodes = {}
    query_graph_nodes = helpers.do_simple_undirected_bfs(query_graph, seed_node)
    reverse_query_graph = query_graph.reverse()

    for query_node in query_graph_nodes:
        outgoing_flows = helpers.do_simple_dfs(query_graph, query_node)
        outgoing_flows.discard(query_node)

        incoming_flows = helpers.do_simple_dfs(reverse_query_graph, query_node)
        incoming_flows.discard(query_node)

        candidates = candidate_alignments[query_node]
        
        candidate_node_alignment_scores = {}
        for candidate_alignment in candidates:
            out_final_influence_score = 0
            in_final_influence_score = 0

            for outgoing_flow in outgoing_flows:
                if outgoing_flow not in aligned_nodes:
                    influence_scores = []
                    candidate_outgoing_alignments = candidate_alignments[outgoing_flow]
                    for candidate_outgoing_alignment in candidate_outgoing_alignments:
                        influence_score = scores.compute_influence_score(candidate_alignment, candidate_outgoing_alignment, threshold, provenance_graph)
                        influence_scores.append(influence_score)
                    #TODO: handling empty candidate alignment? meaning nothing found in provenance graph
                    out_final_influence_score += max(influence_scores)
                else:
                    out_final_influence_score += scores.compute_influence_score(candidate_alignment, aligned_nodes[outgoing_flow], threshold, provenance_graph)
            
            for incoming_flow in incoming_flows:
                if incoming_flow not in aligned_nodes:
                    influence_scores = []
                    candidate_incoming_alignments = candidate_alignments[incoming_flow]
                    for candidate_incoming_alignment in candidate_incoming_alignments:
                        influence_score = scores.compute_influence_score(candidate_incoming_alignment, candidate_alignment, threshold, provenance_graph)
                        influence_scores.append(influence_score)
                    #TODO: handling empty candidate alignment? meaning nothing found in provenance graph
                    in_final_influence_score += max(influence_scores)
                else:
                    in_final_influence_score += scores.compute_influence_score(aligned_nodes[incoming_flow], candidate_alignment, threshold, provenance_graph)
            
            total_influence_score = out_final_influence_score + in_final_influence_score
            candidate_node_alignment_scores[candidate_alignment] = total_influence_score
        
        aligned_nodes[query_node] = max(candidate_node_alignment_scores, key = candidate_node_alignment_scores.get)
        print(f"Aligned node for candidate node {query_node} is {aligned_nodes[query_node]}")
    
    return aligned_nodes