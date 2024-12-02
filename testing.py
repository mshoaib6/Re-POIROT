import networkx as nx
from node import Node
import itertools

def is_process(graph, node):
    node = graph.nodes[node]['node']
    return node.type in ("BROWSER", "PROCESS", "LAUNCHER", "SPOOLS", "EXE", "JAVA", "process", "SUBJECT_PROCESS")

def do_process_dfs(graph, node, visited):
    if node not in visited and is_process(graph, node):
        visited.add(node)
        for neighbor in graph[node]:
            do_process_dfs(graph, neighbor, visited)

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

G = nx.DiGraph()
node1 = Node("node1", "process", "node1")
G.add_node(node1.id, node=node1)
print(find_single_process_ancestors(G, node1.id))
# print(find_minimum_common_ancestors(G, [node1.id]))
print()

node2  = Node("node2", "process", "node2")
G.add_node(node2.id, node=node2)
print(find_single_process_ancestors(G, node1.id))
print(find_single_process_ancestors(G, node2.id))
print(find_minimum_common_ancestors(G, [node1.id, node2.id]))
print()

G.add_edge(node2.id, node1.id)
print(find_single_process_ancestors(G, node1.id))
print(find_single_process_ancestors(G, node2.id))
print(find_minimum_common_ancestors(G, [node1.id, node2.id]))
print()

node3 = Node("node3", "not process", "node3")
G.add_node(node3.id, node=node3)
G.add_edge(node3.id, node2.id)
print(find_single_process_ancestors(G, node1.id))
print(find_single_process_ancestors(G, node2.id))
print(find_single_process_ancestors(G, node3.id))
print(find_minimum_common_ancestors(G, [node1.id, node2.id]))
print()

node4 = Node("node4", "process", "node4")
G.add_node(node4.id, node=node4)
G.add_edge(node4.id, node3.id)
print(find_single_process_ancestors(G, node1.id))
print(find_single_process_ancestors(G, node2.id))
print(find_single_process_ancestors(G, node3.id))
print(find_single_process_ancestors(G, node4.id))
print()

node5 = Node("node5", "process", "node5")
G.add_node(node5.id, node=node5)
G.add_edge(node5.id, node1.id)
print(find_single_process_ancestors(G, node1.id))
print(find_single_process_ancestors(G, node2.id))
print(find_single_process_ancestors(G, node3.id))
print(find_single_process_ancestors(G, node4.id))
print(find_single_process_ancestors(G, node5.id))
print(find_minimum_common_ancestors(G, [node5.id, node2.id]))
print(find_minimum_common_ancestors(G, [node1.id, node2.id, node4.id, node5.id]))
print()

all_ancestors = [{'master'}]
total = set().union(*all_ancestors)

# brute force algorithm for hitting set problem (NP-Complete)
for length in range(1, len(total) + 1):
    combinations = itertools.combinations(total, length)
    for combination in combinations:
        for ancestor_set in all_ancestors:
            if len(ancestor_set.intersection(set(combination))) != 0:
                print(len(combination))
print("ERROR")
print(all_ancestors)
exit(1)