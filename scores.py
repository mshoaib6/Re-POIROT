import networkx as nx
import itertools 
import helpers
import time

min_common_ancestors_time = 0.0
path_finding_time = 0.0

# def find_single_process_ancestors(graph, node):
#     '''
#     finds ancestors of a single node
#     params: graph: networkx.DiGraph describing relationships between nodes
#             node: node to find ancestors of
#     returns: a set containing process node ancestors of the node
#     '''
#     ancestors = nx.ancestors(graph, node)
#     ancestors.add(node)
#     ancestors = {node for node in ancestors if graph.nodes[node]['node'].type == 'PROCESS'}
#     return ancestors

def do_process_dfs(graph, node, visited):
    if node not in visited and is_process(graph, node):
        visited.add(node)
        for neighbor in graph[node]:
            do_process_dfs(graph, neighbor, visited)

def is_process(graph, node):
    node = graph.nodes[node]['node']
    return node.type in ("BROWSER", "PROCESS", "LAUNCHER", "SPOOLS", "EXE", "JAVA", "process", "SUBJECT_PROCESS")

def find_single_process_ancestors(graph, node):
    '''
    finds ancestors of a single node
    params: graph: networkx.DiGraph describing relationships between nodes
            node: node to find ancestors of
    returns: a set containing process node ancestors of the node
    '''
    visited = set()
    reverse_graph = graph.reverse()
    ancestors = do_process_dfs(reverse_graph, node, visited)
    return visited

def find_process_ancestors_of_nodes(graph, nodes):
    '''
    finds ancestors of a list of nodes
    params: graph: networkx.DiGraph describing relationships between nodes
            nodes: nodes to find ancestors of
    returns: a list containing sets of process node ancestors of all nodes
    '''
    all_ancestors = [find_single_process_ancestors(graph, node) for node in nodes]
    return all_ancestors

def find_minimum_common_ancestors(graph, nodes):
    '''
    finds minimum number of process common ancestors of a bunch of nodes
    params: graph: networkx.DiGraph describing relationships between nodes
            nodes: nodes to find minimum number of common ancestors of
    returns: the number of minimum common ancestors shared between the nodes
    '''
    start_time = time.time()
    process_nodes = [node for node in nodes if is_process(graph, node)]
    all_ancestors = find_process_ancestors_of_nodes(graph, process_nodes)
    total = set().union(*all_ancestors)
    if len(total) == 0:
        return 1

    # brute force algorithm for hitting set problem (NP-Complete)
    for length in range(1, len(total) + 1):
        combinations = itertools.combinations(total, length)
        for combination in combinations:
            for ancestor_set in all_ancestors:
                if len(ancestor_set.intersection(set(combination))) == 0:
                    break
            else:
                return len(combination)
            
def find_all_paths(graph, node_start, node_end, path=[]):
    '''
    given two nodes node_start and node_end,
    this routine recursively finds all paths between
    the two nodes in the graph graph.

    credits: https://stackoverflow.com/a/24471320/
    '''
    global path_finding_time
    print("Finding all paths...")
    start_time = time.time()
    path = path + [node_start]
    if node_start == node_end:
        end_time = time.time()
        elapsed_time = end_time - start_time
        path_finding_time += elapsed_time
        print(f"Done Finding Paths\nPath Finding Time: {path_finding_time: .2f}")
        return [path]
    if node_start not in graph:
        end_time = time.time()
        elapsed_time = end_time - start_time
        path_finding_time += elapsed_time
        print(f"Done Finding Paths\nPath Finding Time: {path_finding_time: .2f}")
        return []
    paths = []
    for node in graph[node_start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, node_end, path)
            for newpath in newpaths:
                paths.append(newpath)
    end_time = time.time()
    elapsed_time = end_time - start_time
    path_finding_time += elapsed_time
    print(f"Done Finding Paths\nPath Finding Time: {path_finding_time: .2f}")
    return paths

def compute_influence_score(node_a, node_b, threshold, provenance_graph):
    '''
    This computes the influence score gamma(i, j) (page 1800)
    where i and j are the two nodes between whom the
    influence score is computed.
    params: start node: node_a
          : end node: node_b
          : threshold: upper bound for number of distinct compromises attacker can reasonably exploit
          : filename: the filename representing the graph
    returns: the influence score, gamma(i, j)
    '''
    # now that we have graph, try to find all paths
    # between the two nodes node_a and node_b
    if node_a == node_b and is_process(provenance_graph, node_a) and is_process(provenance_graph, node_b):
        return 0
    all_flows = find_all_paths(provenance_graph, node_a, node_b)
    # now that we have all paths/flows, find the minimum
    # number of compromise points for the attacker in
    # these flows/paths
    gamma = 0
    for flow in all_flows:
        cmin = find_minimum_common_ancestors(provenance_graph, flow)
        if cmin != 0 and cmin <= threshold:
            gamma = max(gamma, 1.0/cmin)
    return gamma

def compute_alignment_score(query_graph, provenance_graph, aligned_nodes, threshold):
    '''
    This computes the alignment score between two graph alignments
    S(Gq :: Gp) where Gq is query graph and Gp is alignment from
    provenance graph

    params: query_graph -> networkx DiGraph representing query graph
            provenance_graph -> networkx DiGraph representing provenance graph
            aligned_nodes -> graph alignment obtained from step 4 of poirot
            threshold -> upper bound for number of distinct compromises attacker can reasonably exploit
    returns: alignment score as outlined in equation 2.
    '''
    
    total_influence_score = 0
    num_flows = 0
    for node in query_graph.nodes:
        outgoing_flows = helpers.do_simple_dfs(query_graph, node)
        outgoing_flows.discard(node)
        for outgoing_flow in outgoing_flows:
            influence_score = compute_influence_score(aligned_nodes[node],
                    aligned_nodes[outgoing_flow], threshold,
                    provenance_graph)
            total_influence_score += influence_score
            # F(G) is the set of all flows s.t. i != j
            # if aligned_nodes[node] != aligned_nodes[visited_node]:
            num_flows += 1
    return float(total_influence_score)/float(num_flows)