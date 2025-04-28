"""  
GraphMatch.py

- Class to compute quality of a generated SHACL graph relative to groundtruth
- Supported metrics: triple match, G-BERTScore, Graph Edit Distance, validation performance
- Similar implementations of these metrics are publicly available at
    https://github.com/Jiuzhouh/PiVe, https://github.com/ChristopheCruz/LLM4KGC, 
    https://github.com/swarnaHub/ExplaGraphs/tree/main
"""
import os
import rdflib
import time
from rdflib import Graph
from typing import Dict, List, Tuple
from sklearn import preprocessing
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from scipy.optimize import linear_sum_assignment
from bert_score import score as score_bert
from pyshacl import validate
import networkx as nx
import numpy as np
from Utils.Logger import setup_logger
from Utils.Parsing import norm_string

# Constants
GED_TIMEOUT = 100

class GraphMatcher:
    """ 
    A class for comparing a generated SHACL graph against a gold standard
    SHACL graph. Supports metrics:
    - Triple match (accuracy, precision, recall, F1 score)
    - G-BERTScore (precision, recall, F1 score)
    - Graph Edit Distance
    - Validation performance (precision, recall, accuracy, F1 score)
    
    :attr gold_file_path: Path to the gold SHACL graph (.ttl)
    :attr gen_file_path: Path to the generated SHACL graph (.ttl)
    :attr gold_graph: List of triples in the gold graph.
    :attr gen_graph: List of triples in the generated graph.
    :attr logger: Logger for the class.
    """
    def __init__(self, gold_file_path: str, generated_file_path: str, logfile: str = "logs/GraphMatch.log"):
        self.gold_file_path = gold_file_path
        self.gen_file_path = generated_file_path
        self.gold_triples = self._load_triples(gold_file_path)
        self.gen_triples = self._load_triples(generated_file_path)
        self.ged_timed_out = 0
        self.logger = setup_logger(__name__, logfile)
    
    def _normalize_iri(self, iri: str) -> str:
        """Normalizes blank nodes and spelling of IRIs."""
        if isinstance(iri, rdflib.term.BNode):
            # Replace memory address with a common identifier for blank nodes
            return "_:blank"
        else:
            # Convert to lowercase and strip leading/trailing spaces
            return norm_string(iri)
    
    def _load_triples(self, turtle_file_path: str) -> List[Tuple[str,str,str]]:
        """Extracts a list of normalized triples from a Turtle file."""
        
        try:
            graph = rdflib.Graph()
            graph.parse(turtle_file_path, format="turtle")

            triples = [
                (self._normalize_iri(s), self._normalize_iri(p), self._normalize_iri(o))
                for s, p, o in graph
            ]
            return triples
        except Exception as e:
            self.logger.error(f"Error loading triples from {turtle_file_path}: {e}")
            raise
    
    def _load_digraph(self, turtle_file_path: str) -> nx.DiGraph:
        """Loads a NetworkX DiGraph from a Turtle file."""
        try:
            rdf_graph = rdflib.Graph()
            rdf_graph.parse(turtle_file_path, format="turtle")
            digraph = nx.DiGraph()
            for subject, predicate, object in rdf_graph:
                digraph.add_edge(subject, object, predicate=predicate)
            return digraph
        except Exception as e:
            self.logger.error(f"Error loading DiGraph from {turtle_file_path}: {e}")
            raise
    
    def compute_triple_match(self) -> Dict[str, float]:
        """
        Compares the triples between the generated and gold graphs using
        exact matching.

        :return: Triple match accuracy, precision, recall, and F1 score.
        """
        # Extract unique triples from both graphs
        all_classes = self.gold_triples + self.gen_triples
        all_triples_set = list(set(all_classes))

        # Treat each triple as a label in a multi-label classification problem
        labels = preprocessing.MultiLabelBinarizer(classes=all_triples_set)
        truth = labels.fit_transform([self.gold_triples])
        pred = labels.fit_transform([self.gen_triples])

        self.logger.info("Computing triple match metrics...")
        precision = precision_score(truth, pred, average='micro')
        recall = recall_score(truth, pred, average='micro')
        f1 = f1_score(truth, pred, average='micro')  
        
        gold_triples_set = set(self.gold_triples)
        matches = sum(1 for triple in self.gen_triples if triple in gold_triples_set)
        accuracy = matches / len(self.gen_triples) if len(self.gen_triples) > 0 else 0.0
        
        return {
                "triple_accuracy": round(accuracy,4),
                "triple_precision": round(precision,4),
                "triple_recall": round(recall,4),
                "triple_f1": round(f1,4)
                }
    
    def compute_gbert(self) -> Dict[str,float]:
        """
        Measures the similarity between the triples in the generated and
        gold graphs using G-BERTScore, a metric based on the token
        similarity between the contextual embeddings of the triples.
        
        G-BERTScore treats each edge as a sentence and follows these steps:
        1. Compute BERTScore for each pair of generated and gold edges.
        2. Find a complete assignment of gold edges to generated edges that 
        maximizes the sum of BERTScores.
        3. Calculate precision, recall, and F1 score based on the optimal assignment.
        
        :return: G-BERT precision, recall, and F1 score.
        """
        # Convert triples to sentences, e.g. from ("s","p","o") to ("s p o")
        gold_edges = [" ".join(edge) for edge in self.gold_triples]
        gen_edges = [" ".join(edge) for edge in self.gen_triples]
        
        references = []
        candidates = []
        ref_cand_index = {}
        # For each gold edge, pair it with each generated edge
        for (i, gold_edge) in enumerate(gold_edges):
            for (j, gen_edge) in enumerate(gen_edges):
                references.append(gold_edge)
                candidates.append(gen_edge)
                ref_cand_index[(gold_edge, gen_edge)] = len(references) - 1

        # Compute BERTScore between all pairs of gold and generated edges
        self.logger.info("Computing G-BERTScore...")
        try:
            _, _, bs_F1 = score_bert(cands=candidates, refs=references, lang='en', idf=False)
        except Exception as e:
            self.logger.error(f"Error computing BERTScores: {e}")
            raise

        score_matrix = np.zeros((len(gold_edges), len(gen_edges)))
        for (i, gold_edge) in enumerate(gold_edges):
            for (j, gen_edge) in enumerate(gen_edges):
                score_matrix[i][j] = bs_F1[ref_cand_index[(gold_edge, gen_edge)]]
                
        # Solve the linear assignment problem to maximize the sum of BERTScores
        row_ind, col_ind = linear_sum_assignment(score_matrix, maximize=True)
        
        # Compute final G-BERT Score based on the optimal assignment
        precision = score_matrix[row_ind, col_ind].sum() / len(gen_edges)
        recall = score_matrix[row_ind, col_ind].sum() / len(gold_edges)
        gbert_f1 = 2 * (precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            "gbert_precision": round(precision,4),
            "gbert_recall": round(recall,4),
            "gbert_f1": round(gbert_f1,4)
        }

    def compute_ged(self) -> float:
        """
        Computes Graph Edit Distance (GED), which measures the costs of 
        transforming the generated graph into a graph that is isomorphic
        to the gold graph. Normalizes the GED to fall between 0 and 1.
        
        :return: Normalized GED between the generated and gold graphs.
        """
        gold_graph = self._load_digraph(self.gold_file_path)
        gen_graph = self._load_digraph(self.gen_file_path)

        normalizing_constant = (
            gold_graph.number_of_nodes() +
            gold_graph.number_of_edges() +
            gen_graph.number_of_nodes() +
            gen_graph.number_of_edges()
        )

        self.logger.info("Computing GED...")
        start_time = time.time()
        ged = nx.graph_edit_distance(gold_graph, gen_graph, timeout=GED_TIMEOUT)
        elapsed_time = time.time() - start_time

        # Logging timeout, meaning the result may not be exact
        if elapsed_time >= GED_TIMEOUT:
            self.ged_timed_out = 1

        assert ged <= normalizing_constant

        ged_norm = ged / normalizing_constant

        return ged_norm
    
    def compute_validation_performance(self, user_profiles_dir: str) -> Dict[str, float]:
        """ 
        Compares the validation results of the generated and gold graphs
        (shapes graphs) over a set of user profiles (data graphs).
        
        :param user_profiles_dir: Directory with synthetic user profiles.
        :return: Dictionary with precision, recall, accuracy, and F1 score.
        """
        y_true, y_pred = [], []

        shacl_gen = Graph()
        shacl_gen.parse(self.gen_file_path, format="turtle")
        shacl_gold = Graph()
        shacl_gold.parse(self.gold_file_path, format="turtle")
        
        # For each profile, check if it conforms with the generated and groundtruth graphs
        self.logger.info("Computing validation performance...")
        for profile in os.listdir(user_profiles_dir):
            profile_path = os.path.join(user_profiles_dir, profile)
            data_graph = Graph()
            data_graph.parse(profile_path, format="turtle")
            try:
                conforms_with_gen, _, _ = validate(data_graph=data_graph, shacl_graph=shacl_gen)
                conforms_with_gold, _, _ = validate(data_graph=data_graph, shacl_graph=shacl_gold)
            except Exception as e:
                self.logger.error(f"Error validating {profile_path}: {e}")
                continue
            
            if conforms_with_gen and conforms_with_gold:
                y_pred.append(1)
                y_true.append(1)
            elif not conforms_with_gen and not conforms_with_gold:
                y_pred.append(0)
                y_true.append(0)
            elif conforms_with_gen and not conforms_with_gold:
                y_pred.append(1)
                y_true.append(0)
            else:
                y_pred.append(0)
                y_true.append(1)
                
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        accuracy = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        return {
            "validation_precision": round(precision,4),
            "validation_recall": round(recall,4),
            "validation_accuracy": round(accuracy,4),
            "validation_f1": round(f1,4)
        }