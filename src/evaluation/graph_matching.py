""" 
graph_matching.py

- Functions to compute triple match, G-BERTScore, and Graph Edit Distance
- Similar implementations of these metrics have been published, see 
    https://github.com/Jiuzhouh/PiVe, https://github.com/ChristopheCruz/LLM4KGC, 
    https://github.com/swarnaHub/ExplaGraphs/tree/main/metrics
"""

from rdflib import Graph
from typing import List, Dict
from sklearn import preprocessing
from sklearn.metrics import precision_score, recall_score, f1_score

def extract_triples_from_turtle(file_path: str):
    """
    Extract triples from a Turtle file and return them as a list of triples.
    
    :param file_path: Path to the Turtle file.
    :return: List of triples, where each triple is a list [subject, predicate, object].
    """
    g = Graph()
    g.parse(file_path, format="turtle")
    triples = []
    
    # Convert each triple to list of normalized strings
    for subj, pred, obj in g:
        triple = [str(subj).lower().strip(), str(pred).lower().strip(), str(obj).lower().strip()]
        triples.append(triple)

    return triples

def get_triple_match(gen_graph: List[List[str]], gold_graph:  List[List[str]]) -> Dict[str, float]:
    """
    Calculate precision, recall and F1 score between the triples two graphs.

    :param gen_graph: Generated graph to be evaluated.
    :param gold_graph: Groundtruth graph.
    :return: Dictionary containing precision, recall, and F1 score.
    """
    gen_graph_list = [str(string).lower() for string in gen_graph]
    gold_graph_list = [str(string).lower() for string in gold_graph]
    
    # Get unique triples
    unique_triples = list(set(gen_graph_list + gold_graph_list))

    # Treat each triple as a label in a multi-label classification problem
    labels = preprocessing.MultiLabelBinarizer(classes=unique_triples)
    truth = labels.fit_transform([gold_graph_list])
    pred = labels.fit_transform([gen_graph_list])

    precision = precision_score(truth, pred, average='micro')
    recall = recall_score(truth, pred, average='micro')
    f1 = f1_score(truth, pred, average='micro')

    return {
            "tm_precision": precision,
            "tm_recall": recall,
            "tm_f": f1
            }

def get_ged(gen_graph, gold_graph):
    pass

def get_gbert_score(gen_graph, gold_graph):
    pass