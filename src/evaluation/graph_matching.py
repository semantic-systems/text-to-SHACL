""" 
graph_matching.py

- Functions to compute triple match, G-BERTScore, and Graph Edit Distance
- Similar implementations of these metrics are publicly available at
    https://github.com/Jiuzhouh/PiVe, https://github.com/ChristopheCruz/LLM4KGC, 
    https://github.com/swarnaHub/ExplaGraphs/tree/main
"""
import numpy as np
import networkx as nx
from typing import List, Dict
from sklearn import preprocessing
from sklearn.metrics import precision_score, recall_score, f1_score
from scipy.optimize import linear_sum_assignment
from bert_score import score as score_bert
from rdflib import Graph
from eval_helpers import norm_string

def get_ged(gen_graph: List[List[str]], gold_graph: List[List[str]]) -> Dict[str, float]:
    """
    Computes the Graph Edit Distance (GED) between a generated graph and a 
    gold graph. GED is normalized to range from 0 (isomorphic graphs) to 1 
    (maximum dissimilarity), assuming an upper bound where all nodes and
    edges of the generated graph are deleted and those of the gold graph 
    are added.

    :param gen_graph: List of triples representing the generated graph. 
    :param gold_graph: List of triples representing the gold graph.
    :return: Dictionary containing the normalized GED.
    """
    # Simplify graphs by removing label and message properties
    simple_gen_graph = simplify_graph(gen_graph)
    simple_gold_graph = simplify_graph(gold_graph)
    
    # Convert list of triples to directed graphs
    gen_digraph = edge_list_to_digraph(simple_gen_graph)
    gold_dirgraph = edge_list_to_digraph(simple_gold_graph)

    # Define upper bound for normalizing GED (see docstring)
    normalizing_constant = gold_dirgraph.number_of_nodes() + gold_dirgraph.number_of_edges() + gen_digraph.number_of_nodes() + gen_digraph.number_of_edges()
    ged = nx.graph_edit_distance(gold_dirgraph, gen_digraph, timeout=60)
   
    assert normalizing_constant != 0 and ged <= normalizing_constant
    
    return {"GED": ged / normalizing_constant}

def get_triple_match(gen_graph: List[List[str]], gold_graph:  List[List[str]]) -> Dict[str, float]:
    """
    Calculates accuracy, precision, recall and F1 score between the triples
    of a generated graph and a gold graph.

    :param gen_graph: Generated graph.
    :param gold_graph: Groundtruth graph.
    :return: Dictionary containing precision, recall, and F1 score.
    """
    gen_triples = [norm_string(triple) for triple in gen_graph]
    gold_triples = [norm_string(triple) for triple in gold_graph]
    
    # Get all unique triples
    unique_triples = list(set(gen_triples + gold_triples))

    # Treat each triple as a label in a multi-label classification problem
    labels = preprocessing.MultiLabelBinarizer(classes=unique_triples)
    truth = labels.fit_transform([gold_triples])
    pred = labels.fit_transform([gen_triples])

    precision = precision_score(truth, pred, average='micro')
    recall = recall_score(truth, pred, average='micro')
    f1 = f1_score(truth, pred, average='micro')
    
    # Compute accuracy    
    gold_triples_set = set(gold_triples)
    matches = sum(1 for triple in gen_triples if triple in gold_triples_set)
    accuracy = matches / len(gen_triples) if len(gen_triples) > 0 else 0.0
            
    return {
            "Triple Accuracy": accuracy,
            "Triple Precision": precision,
            "Triple Recall": recall,
            "Triple F1": f1
            }

def get_gbert_score(gen_edges: List[List[str]], gold_edges: List[List[str]]) -> Dict[str, float]:
    """
    Computes the G-BERT score between a set of generated and gold edges.

    G-BERT treats each edge as a sentence and follows these steps:
    1. Compute BERTScore for each pair of generated and gold edges.
    2. Find a complete assignment of gold edges to generated edges that 
    maximizes the sum of BERTScores.
    3. Calculate precision, recall, and F1 score based on the optimal assignment.

    :param gen_edges: List of edges of the generated graph.
    :param gold_edges: List of edges of the gold graph.
    
    :return: The G-BERT F1 score based on the optimal assignment.
    """
    references = []
    candidates = []
    
    # For each gold edge, pair it with each generated edge
    ref_cand_index = {}
    for (i, gold_edge) in enumerate(gold_edges):
        for (j, gen_edge) in enumerate(gen_edges):
            references.append(gold_edge)
            candidates.append(gen_edge)
            ref_cand_index[(gold_edge, gen_edge)] = len(references) - 1

    # Compute BERTScore between all pairs of gold and generated edges
    _, _, bs_F1 = score_bert(cands=candidates, refs=references, lang='en', idf=False)
    print("Computed bert scores for all pairs")

    score_matrix = np.zeros((len(gold_edges), len(gen_edges)))
    for (i, gold_edge) in enumerate(gold_edges):
        for (j, gen_edge) in enumerate(gen_edges):
            score_matrix[i][j] = bs_F1[ref_cand_index[(gold_edge, gen_edge)]]
            
    # Solve the linear assignment problem to maximize the sum of BERTScores
    row_ind, col_ind = linear_sum_assignment(score_matrix, maximize=True)
    
    # Compute precision, recall, and F1 score based on the optimal assignment
    precision = score_matrix[row_ind, col_ind].sum() / len(gen_edges)
    recall = score_matrix[row_ind, col_ind].sum() / len(gold_edges)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"G-BERT F1": f1}

def extract_triples_from_turtle(file_path: str) -> List[List[str]]:
    """Extracts list of triples from a Turtle file."""
    g = Graph()
    g.parse(file_path, format="turtle")
    triples = []
    for s, p, o in g:
        # Convert each triple to list of normalized strings ["s", "p", "o"]
        triple = [norm_string(s), norm_string(p), norm_string(o)]
        triples.append(triple)
        
    return triples

def edge_list_to_digraph(edge_list: List[List[str]]) -> nx.DiGraph:
    """Converts a list of triples to a directed graph."""
    graph = nx.DiGraph()
    for edge in edge_list:
        # Ensure correct edge structure, i.e. [s,p,o]
        if len(edge) == 2:
            edge.append('NULL')
        elif len(edge) == 1:
            edge.append('NULL')
            edge.append('NULL')
        s, p, o = edge[0], edge[1], edge[2]
        graph.add_node(norm_string(s), label=norm_string(s))
        graph.add_node(norm_string(o), label=norm_string(o))
        graph.add_edge(norm_string(s), norm_string(o), label=norm_string(p))
        
    return graph

def is_excluded(triple: List[str]) -> bool:
    return (triple[1] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and 
            triple[2] == "https://foerderfunke.org/default#socialbenefit")

def simplify_graph(graph: List[List[str]]) -> List[List[str]]:
    """
    Simplifies the graph by removing label and message properties,
    and excludes any triple with predicate 'a' and object 'ff:SocialBenefit'.
    
    :param graph: List of triples representing the graph.
    :return: Simplified graph.
    """
    # Define predicates to be removed
    remove_predicates = {
        "http://www.w3.org/2000/01/rdf-schema#label",
        "http://www.w3.org/ns/shacl#message"
    }
    
    # Filter out unwanted triples
    simplified_graph = [
        triple for triple in graph
        if triple[1] not in remove_predicates and not is_excluded(triple)
    ]
    
    return simplified_graph