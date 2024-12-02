import scores

def do_dfs(graph, node, visited, threshold):
    '''
    given start node, perform
    forward and backward traversal using dfs
    params: graph: the original provenance graph
            node: start node
            visited: track nodes that have been visited
            threshold: limit for number of compromises
    '''
    dfs_helper(graph, node, visited, [node], threshold)

def dfs_helper(graph, node, visited, path, threshold):
    if node not in visited:
        visited.add(node)
        if scores.find_minimum_common_ancestors(graph, path) < threshold:
            for neighbor in graph[node]:
                dfs_helper(graph, neighbor, visited, path + [neighbor], threshold)

def do_simple_dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    if node not in visited:
        visited.add(node)
        if node in graph:
            for neighbor in graph[node]:
                do_simple_dfs(graph, neighbor, visited)
    return visited

def do_simple_undirected_bfs(graph, node):
    undirected = graph.to_undirected()
    queue = [node]
    visited = [node]
    while len(queue) > 0:
        curr = queue.pop(0)
        for neighbor in undirected[curr]:
            if neighbor not in visited:
                visited.append(neighbor)
                queue.append(neighbor)
    
    return visited