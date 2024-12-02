import pickle
import networkx as nx
from node import Node

def load_graph(filename):
    if filename.split(".")[-1] == "pkl":
        return load_pickle_graph(filename)
    elif filename.split(".")[-1] == "txt":
        return load_txt_graph(filename)
    elif filename.split(".")[-1] == "spt":
        return load_streamspot_graph(filename)
    else:
        print("Filetype not recognized, please provide a networkx graph in a pickle or use the text format.")
        exit(1)

def load_pickle_graph(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)
    
def load_txt_graph(filename):
    graph = nx.DiGraph()
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            from_node_string, to_node_string = [string.strip() for string in line.split("->")]
            from_node_type, from_node_label = from_node_string.split(":")
            to_node_type, to_node_label = to_node_string.split(":")
            from_node = Node(from_node_label, from_node_type, from_node_label)
            to_node = Node(to_node_label, to_node_type, to_node_label)
            graph.add_node(from_node.id, node=from_node)
            graph.add_node(to_node.id, node=to_node)
            graph.add_edge(from_node.id, to_node.id)
    return graph

node_type = {'a': "process",
             'b': "thread",
             'c': "file",
             'd': "map_anonymous",
             'e': "n/a",
             'f': "stdin",
             'g': "stdout",
             'h': "stderr",
             'i': "accept",
             'j': "access",
             'k': "bind",
             'l': "chmod", 
             'm': "clone",
             'n': "close",
             'o': "connect",
             'p': "execve",
             'q': "fstat",
             'r': "ftruncate",
             's': "listen",
             't': "mmap2",
             'u': "open",
             'v': "read",
             'w': "recv",
             'x': "recvfrom",
             'y': "recvmsg",
             'z': "send",
             'A': "sendmsg",
             'B': "sendto",
             'C': "stat",
             'D': "truncate",
             'E': "unlink",
             'F': "waitpid",
             'G': "write",
             'H': "writev"
             }

def load_streamspot_graph(filename):
    graph = nx.DiGraph()
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            from_node_id, to_node_id, parameters = line.split()
            from_node_type_letter, to_node_type_letter, _, _ = parameters.split(":")
            from_node_type = node_type[from_node_type_letter]
            to_node_type = node_type[to_node_type_letter]
            from_node = Node(from_node_id, from_node_type, from_node_id)
            to_node = Node(to_node_id, to_node_type, to_node_id)
            graph.add_node(from_node.id, node=from_node)
            graph.add_node(to_node.id, node=to_node)
            graph.add_edge(from_node.id, to_node.id)
    return graph