import networkx as nx
import pandas as pd
import gzip
import gdown
import json
import os
import pickle
from node import Node

def preprocess(data):
    new_data = {}
    for x in data:
        check1 = x['object'] in ['PROCESS','FILE','FLOW','MODULE']
        if check1:
            check2 = not (x['action'] in ['START','TERMINATE'])
            check3 = x['subjectname'] != x['objectname']
            key = (x['action'],x['subjectname'],x['objectname'])
            if check1 and check2 and check3:
                new_data[key] = x
    return list(new_data.values())


def get_labels(x):
    event = x
    typ = event['object']
    props = event['properties']
    try:
        if typ == "PROCESS":
            event["subjectname"] = props['parent_image_path']
            event["objectname"] = props['image_path']

        if typ == "FILE":
            event["subjectname"] = props['image_path'] 
            event["objectname"] = props['file_path']
    
        if typ == "MODULE":
            event["subjectname"] = props['image_path']
            event["objectname"] = props['module_path']
    
        if typ == "FLOW":
            event["subjectname"] = props['image_path']
            event["objectname"] = props['dest_ip']+' '+props['dest_port']
    
        return event
    except:
        return None
    

def extract_logs(filepath, givenID):
    """
    This function extracts logs from the given optc filepath for a specific host ID.
    The extracted logs are saved in the 'raw_logs/logs.txt' file.

    Args:
        filepath (str): The path to the optc file.
        givenID (str): The ID of the host for which logs need to be extracted.

    Returns:
        None
    """

    # Create 'raw_logs' directory if it doesn't exist
    if not os.path.exists("raw_logs"):
        os.mkdir("raw_logs")

    logs = []
    with gzip.open(filepath, 'r') as fin:
        for line in fin:
            rawtext = line.decode('utf-8')
            text = json.loads(rawtext)
            hostID = text['hostname']

            if hostID == f"SysClient{givenID}.systemia.com":
                logs.append(rawtext)

    # Save the extracted logs to 'raw_logs/logs.txt'
    with open('raw_logs/logs.txt', "w") as out:
        out.writelines(logs)


def generate_networkx_graph():
    """
    This function converts the logs in "raw_logs/logs.txt" to a networkx graph.

    Returns:
        G (networkx.Graph): The networkx graph representing the logs.
    """
    path_to_host_dataset = "raw_logs/logs.txt"
    with open(path_to_host_dataset, 'r') as f:
        json_records = [json.loads(line) for line in f]
    
    lbldta = [get_labels(x) for x in json_records]
    lbldta = [x for x in lbldta if x != None]
    filtered = preprocess(lbldta)
    
    df = pd.DataFrame.from_dict(filtered)
    df['subject_type'] = 'PROCESS' 
    df = df.rename(columns={'object': 'object_type','action': 'syscall'})
    
    df = df[['subjectname','subject_type','objectname','object_type','syscall','timestamp']]

    G = nx.DiGraph()

    for _, row in df.iterrows():
        node1 = Node(row['subjectname'], row['subject_type'], row['subjectname'])
        G.add_node(node1.id, node=node1)
        node2 = Node(row['objectname'], row['object_type'], row['objectname'])
        G.add_node(node2.id, node=node2)
        G.add_edge(node1.id, node2.id)
    
    return G, df

    # edges = df[['subjectname', 'objectname']].values.tolist()

    # G = nx.Graph()
    # G.add_edges_from(edges)

    # return G, df


def save_graph_to_disk(graph, filepath):
    """
    Save the NetworkX graph to disk in GPickle format.

    Args:
        graph (networkx.Graph): The NetworkX graph to be saved.
        filepath (str): The path to save the graph.

    Returns:
        None
    """
    with open(filepath, "wb") as f:
        pickle.dump(graph, f)


def load_graph_from_disk(filepath):
    """
    Load a NetworkX graph from disk.

    Args:
        filepath (str): The path to the graph file.

    Returns:
        G (networkx.Graph): The loaded NetworkX graph.
    """
    with open(filepath, "rb") as f:
        graph = pickle.load(f)
    return graph


def main():
    # Downloading Dataset
    # url = "https://drive.google.com/file/d/1pScA6MgVTKSr11QkV4Z_zlgQXP1x5GE1/view?usp=drive_link"
    # gdown.download(url, quiet=True, use_cookies=False, fuzzy=True)
    
    # Extracting Logs
    # extract_logs("data/AIA-101-125.ecar-2019-12-07T02-20-06.258.json.gz", "0101")
    
    # Constructing Graph
    G,_ = generate_networkx_graph()
    save_graph_to_disk(G, "networkx_graph.pkl")
    # loaded_graph = load_graph_from_disk("networkx_graph.pickle")

if __name__ == "__main__":
    main()