"""  
GraphMatch.py

- Class to compute quality of a generated SHACL graph relative to groundtruth
- Supported metrics: triple match, G-BERTScore, Graph Edit Distance, validation performance
- Similar implementations of these metrics are publicly available at
    https://github.com/Jiuzhouh/PiVe, https://github.com/ChristopheCruz/LLM4KGC, 
    https://github.com/swarnaHub/ExplaGraphs/tree/main
"""
import numpy as np
import os
import rdflib
import networkx as nx
from gklearn.ged.env import GEDEnv
from typing import Dict, List, Tuple
from sklearn import preprocessing
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from scipy.optimize import linear_sum_assignment
from bert_score import score as score_bert
from pyshacl import validate
from pyshacl.errors import ReportableRuntimeError
from Utils.Logger import setup_logger
from Utils.Parsing import norm_string

logger = setup_logger(__name__, "logs/GraphMatch.log")

class GraphMatcher:
    """ 
    :attr gold_file_path: Path to the gold SHACL graph (.ttl)
    :attr generated_file_path: Path to the generated SHACL graph (.ttl)
    :attr gold_graph: List of triples in the gold graph (List[Tuple[str,str,str]])
    :attr generated_graph: List of triplesin the generated graph.
    
    :metohd compute_triple_match: Computes accuracy, precision, recall, and F1 score between the triples
    :method compute_gbert: Computes the G-BERT score between a set of generated and gold edges.
    :method compute_ged: Computes the Graph Edit Distance between two graphs.
    :method compute_validation_performance: Computes precision, recall, accuracy, and F1 score of validation performance.
    """
    def __init__(self, gold_file_path: str, generated_file_path: str):
        self.gold_file_path = gold_file_path
        self.gen_file_path = generated_file_path
        self.gold_triples = self._get_triples_from_turtle(gold_file_path)
        self.gen_triples = self._get_triples_from_turtle(generated_file_path)
        
    def _get_triples_from_turtle(self, file_path: str) -> List[Tuple[str,str,str]]:
        """
        Extracts list of normalized triples from a Turtle file.
        
        :param file_path: Path to a Turtle file.
        :return: List of triples in the format [(s1, p1, o1),(s2,p2,o3),...].
        """
        g = rdflib.Graph()
        g.parse(file_path, format="turtle")
        triples = [(norm_string(s), norm_string(p), norm_string(o)) for s, p, o in g]  
        return triples
    
    def _load_digraph(self, turtle_file_path: str) -> nx.DiGraph:
        """
        Loads a Turtle RDF graph into a NetworkX DiGraph.
        
        :param turtle_file_path: Path to the .ttl file
        :return: NetworkX DiGraph representation of the RDF graph
        """
        rdf_graph = rdflib.Graph()
        rdf_graph.parse(turtle_file_path, format="turtle")
        digraph = nx.DiGraph()
        for subject, predicate, object in rdf_graph:
            digraph.add_edge(subject, object, predicate=predicate)
        return digraph
    
    def compute_triple_match(self) -> Dict[str, float]:
        """
        Calculates accuracy, precision, recall and F1 score between the triples
        of the generated graph and the gold graph.

        :return: Dictionary containing precision, recall, and F1 score.
        """
        # Extract unique triples from both graphs
        all_classes = self.gold_triples + self.gen_triples
        all_triples_set = list(set(all_classes))

        # Treat each triple as a label in a multi-label classification problem
        labels = preprocessing.MultiLabelBinarizer(classes=all_triples_set)
        truth = labels.fit_transform([self.gold_triples])
        pred = labels.fit_transform([self.gen_triples])

        precision = precision_score(truth, pred, average='micro')
        recall = recall_score(truth, pred, average='micro')
        f1 = f1_score(truth, pred, average='micro')  
        
        gold_triples_set = set(self.gold_triples)
        matches = sum(1 for triple in self.gen_triples if triple in gold_triples_set)
        accuracy = matches / len(self.gen_triples) if len(self.gen_triples) > 0 else 0.0
                
        return {
                "triple_accuracy": accuracy,
                "triple_precision": precision,
                "triple_recall": recall,
                "triple_f1": f1
                }
    
    def compute_gbert(self) -> float:
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
        # Convert triples to "sentences" (e.g. "s p o")
        gold_edges = [" ".join(edge) for edge in self.gold_triples]
        gen_edges = [" ".join(edge) for edge in self.gen_triples]
        
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
        logger.info(f"Computed BERTScores for all pairs.")

        score_matrix = np.zeros((len(gold_edges), len(gen_edges)))
        for (i, gold_edge) in enumerate(gold_edges):
            for (j, gen_edge) in enumerate(gen_edges):
                score_matrix[i][j] = bs_F1[ref_cand_index[(gold_edge, gen_edge)]]
                
        # Solve the linear assignment problem to maximize the sum of BERTScores
        row_ind, col_ind = linear_sum_assignment(score_matrix, maximize=True)
        
        # Compute final G-BERT Score based on the optimal assignment
        precision = score_matrix[row_ind, col_ind].sum() / len(gen_edges)
        recall = score_matrix[row_ind, col_ind].sum() / len(gold_edges)
        gbert_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return gbert_score

    def compute_ged(self) -> int:
        """Compute the Graph Edit Distance between two graphs."""
        # Load the SHACL graphs as NetworkX DiGraphs
        gold_digraph = self._load_digraph(self.gold_file_path)
        gen_digraph = self._load_digraph(self.gen_file_path)
        
        ged_env = GEDEnv()
        ged_env.set_edit_cost('CONSTANT', edit_cost_constants=[1, 1, 1, 1, 1, 1])  # Set uniform edit costs
        ged_env.add_nx_graph(gold_digraph, '')
        ged_env.add_nx_graph(gen_digraph, '')
        
        listID = ged_env.get_all_graph_ids()
        ged_env.init(init_type='LAZY_WITHOUT_SHUFFLED_COPIES')
        
        options = {'initialization_method': 'RANDOM', 'threads': 1}  # Use random initialization and single thread
        ged_env.set_method('BIPARTITE', options)  # Use bipartite method for GED
        ged_env.init_method()
        
        ged_env.run_method(listID[0], listID[1])
        dis = ged_env.get_upper_bound(listID[0], listID[1])

        normalizing_constant = gold_digraph.number_of_nodes() + gold_digraph.number_of_edges() + gen_digraph.number_of_nodes() + gen_digraph.number_of_edges()
        if normalizing_constant == 0:
            return 0.0
        
        dis = dis / normalizing_constant
        return dis
    
    def compute_validation_performance(self, user_profiles_dir: str) -> Dict[str, float]:
        y_true, y_pred = [], []
    
        # For each profile, check if it conforms with the generated and groundtruth graphs
        for profile in os.listdir(user_profiles_dir):
            profile_path = os.path.join(user_profiles_dir, profile)
            try:
                conforms_with_gen, _, _ = validate(data_graph=profile_path, shacl_graph=self.gen_file_path)
                conforms_with_gold, _, _ = validate(data_graph=profile_path, shacl_graph=self.gold_file_path)
            except Exception as e:
                print(f"Error during validation of {profile_path}: {e}")
                continue
            
            # Profile conforms with both graphs (TP)
            if conforms_with_gen and conforms_with_gold:
                y_pred.append(1)
                y_true.append(1)
            # Profile violates both graphs (TN)
            elif not conforms_with_gen and not conforms_with_gold:
                y_pred.append(0)
                y_true.append(0)
            # Profile conforms with generated graph but not with groundtruth (FP)
            elif conforms_with_gen and not conforms_with_gold:
                y_pred.append(1)
                y_true.append(0)
            # Profile violates generated graph but conforms with groundtruth (FN)
            else:
                y_pred.append(0)
                y_true.append(1)
                
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        accuracy = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        return {
            "Validation Precision": precision,
            "Validation Recall": recall,
            "Validation Accuracy": accuracy,
            "Validation F1": f1
        }