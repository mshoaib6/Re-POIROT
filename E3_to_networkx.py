import networkx as nx
import pandas as pd
import gzip
import gdown
import json
import os
import pickle
import re
from node import Node

def Parse(path,uid_type,uid_label):

    f = open(path)
    data = [json.loads(x) for x in f if "EVENT" in x]

    info = []
    for x in data:
        try:
            action = x['datum']['com.bbn.tc.schema.avro.cdm18.Event']['type']
        except:
            action = ''

        try:
            actor = x['datum']['com.bbn.tc.schema.avro.cdm18.Event']['subject']['com.bbn.tc.schema.avro.cdm18.UUID']
        except:
            actor = ''

        try:
            obj = x['datum']['com.bbn.tc.schema.avro.cdm18.Event']['predicateObject']['com.bbn.tc.schema.avro.cdm18.UUID']
        except:
            obj = ''

        try:
            timestamp = x['datum']['com.bbn.tc.schema.avro.cdm18.Event']['timestampNanos']
        except:
            timestamp = ''

        try:
            cmd = x['datum']['com.bbn.tc.schema.avro.cdm18.Event']['properties']['map']['exec']
        except:
            cmd = ''

        try:
            path = x['datum']['com.bbn.tc.schema.avro.cdm18.Event']['predicateObjectPath']['string']
        except:
            path = ''

        try:
            path2 = x['datum']['com.bbn.tc.schema.avro.cdm18.Event']['predicateObject2Path']['string']
        except:
            path2 = ''

        try:
            obj2 = x['datum']['com.bbn.tc.schema.avro.cdm18.Event']['predicateObject2']['com.bbn.tc.schema.avro.cdm18.UUID']
        except:
            obj2 = ''

        objname,objtype,objname2,objtype2,subjname,subjtype = None,None,None,None,None,None

        if actor in uid_label:
            subjname = uid_label[actor]
            subjtype = uid_type[actor]

        if obj in uid_label:
            objname = uid_label[obj]
            objtype = uid_type[obj]

        if obj2 in uid_label:
            objname2 = uid_label[obj2]
            objtype2 = uid_type[obj2]

        if path != '':
            objname = path
            objtype = "FileObject"

        if path2 != '':
            objname2 = path2
            objtype2 = "FileObject"

        if cmd != '':
            subjname = cmd
            subjtype = "SUBJECT_PROCESS"

        if (subjname and subjtype and objname and objtype):
            info.append({'subjectname':subjname, 'subject_type':subjtype, 'objectname':objname ,'object_type':objtype,'syscall':action,'timestamp':timestamp})

        if (subjname and subjtype and objname2 and objtype2):
            info.append({'subjectname':subjname, 'subject_type':subjtype, 'objectname':objname2 ,'object_type':objtype2,'syscall':action,'timestamp':timestamp})


    df = pd.DataFrame.from_records(info).astype(str).drop_duplicates().dropna()

    return df.drop_duplicates().dropna()

def load_data(path):
    f = open(path)
    audit_logs = [x for x in f]
    return audit_logs

def extract_info(audit_logs):
    uid_type = {}
    uid_label = {}

    for audit_event in audit_logs:
        uuid = re.search(r'"uuid":"([^"]*)"',audit_event)
        if uuid:
            uuid = uuid.group(1)

            if "Subject" in audit_event:
                label = re.search(r'"cmdLine":\s*{\s*"string":\s*"([^"]+)"\s*}',audit_event)
                if label:
                    uid_type[uuid] = re.search(r'"type":"([^"]*)"',audit_event).group(1)
                    uid_label[uuid] = label.group(1)

            if "RegistryKeyObject" in audit_event:
                label = re.search(r'"key":"([^"]*)"',audit_event)
                if label:
                    uid_type[uuid] = "RegistryKeyObject"
                    uid_label[uuid] = label.group(1)

            if "NetFlowObject" in audit_event:
                label = re.search(r'"remoteAddress":"([^"]*)"',audit_event)
                if label:
                    uid_type[uuid] = "NetFlowObject"
                    uid_label[uuid] = label.group(1)

    return uid_type, uid_label

def generate_networkx_graph_from_paths(paths):
    df = pd.DataFrame()
    for path in paths:
        events = load_data(path)

        types,labels = extract_info(events)

        new_df = Parse(path,types,labels)
        df = pd.concat([df, new_df], ignore_index=True)
    
    df = df[['subjectname','subject_type','objectname','object_type','syscall','timestamp']]

    G = nx.DiGraph()

    for _, row in df.iterrows():
        node1 = Node(row['subjectname'], row['subject_type'], row['subjectname'])
        G.add_node(node1.id, node=node1)
        node2 = Node(row['objectname'], row['object_type'], row['objectname'])
        G.add_node(node2.id, node=node2)
        G.add_edge(node1.id, node2.id)
    
    return G, df

def generate_networkx_graph(path):
    
    events = load_data(path)

    types,labels = extract_info(events)

    df = Parse(path,types,labels)

    edges = df[['subjectname', 'objectname']].values.tolist()

    df = df[['subjectname','subject_type','objectname','object_type','syscall','timestamp']]

    G = nx.DiGraph()

    for _, row in df.iterrows():
        node1 = Node(row['subjectname'], row['subject_type'], row['subjectname'])
        G.add_node(node1.id, node=node1)
        node2 = Node(row['objectname'], row['object_type'], row['objectname'])
        G.add_node(node2.id, node=node2)
        G.add_edge(node1.id, node2.id)
    
    return G, df

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
    # paths = ["cadets/ta1-cadets-e3-official.json", "cadets/ta1-cadets-e3-official.json.1", "cadets/ta1-cadets-e3-official.json.2"]
    path = "cadets/ta1-cadets-e3-official.json"
    # Constructing Graph
    G, df = generate_networkx_graph(path)
    df.to_pickle("E3_df.pkl")
    save_graph_to_disk(G, "e3_networkx_graph.pkl")

if __name__ == "__main__":
    main()