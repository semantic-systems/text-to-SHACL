import os
import pandas as pd
from rdflib import Graph, URIRef
from rdflib.namespace import SH
from typing import Tuple

def compute_unknown_shacl_term_ratio(vocab_path: str, core_vocab_path: str, shapes_path: str) -> Tuple[float, float]:
    """
    Compute the proportion of SHACL terms used in a shapes graph
    that are not part of the official SHACL vocabulary.

    :param vocab_path: Path to the SHACL vocabulary Turtle file.
    :param core_vocab_path: Path to the SHACL core vocabulary Turtle file.
    :param shapes_path: Path to the SHACL shapes graph Turtle file.
    :return: Tuple with proportion of unknown SHACL terms (vocab, core vocab).
    """
    # Load vocabularies
    vocab_graph = Graph()
    vocab_graph.parse(vocab_path, format="turtle")
    core_vocab = Graph()
    core_vocab.parse(core_vocab_path, format="turtle")

    # Get all SHACL terms in vocab/core vocab
    sh_terms = {str(s) for s in vocab_graph.all_nodes() if isinstance(s, URIRef) and str(s).startswith(str(SH))}
    sh_core_terms = {str(s) for s in core_vocab.all_nodes() if isinstance(s, URIRef) and str(s).startswith(str(SH))}

    # Load shapes graph
    shapes_graph = Graph()
    shapes_graph.parse(shapes_path, format="turtle")

    # Get all SHACL terms used in shapes
    used_sh_terms = {
        str(term) for triple in shapes_graph
        for term in triple
        if isinstance(term, URIRef) and str(term).startswith(str(SH))
    }

    if not used_sh_terms:
        return 0.0, 0.0

    # Compute unknown terms
    unknown_terms = {term for term in used_sh_terms if term not in sh_terms}
    unknown_terms_core = {term for term in used_sh_terms if term not in sh_core_terms}

    return len(unknown_terms) / len(used_sh_terms), len(unknown_terms_core) / len(used_sh_terms)

def analyze_vocab_over_all_results(
    results_dir: str,
    vocab_path: str,
    core_vocab_path: str,
    save_path: str = None
) -> pd.DataFrame:
    """
    Traverse the experiment folder and compute average unknown SHACL term ratios.

    :param results_dir: Path to the top-level results directory.
    :param vocab_path: Path to SHACL vocabulary file (.ttl).
    :param core_vocab_path: Path to SHACL core vocabulary file (.ttl).
    :param save_path: Optionally save output to this path.
    """
    records = []

    # Traverse runs and models
    for run in os.listdir(results_dir):
        run_path = os.path.join(results_dir, run)
        if not os.path.isdir(run_path):
            continue

        for model in os.listdir(run_path):
            model_path = os.path.join(run_path, model)
            shapes_dir = os.path.join(model_path, "output", "parsed_output")
            if not os.path.isdir(shapes_dir):
                continue

            ratios = []
            core_ratios = []

            for fname in os.listdir(shapes_dir):
                if fname.endswith(".ttl"):
                    shapes_path = os.path.join(shapes_dir, fname)
                    try:
                        ratio, core_ratio = compute_unknown_shacl_term_ratio(
                            vocab_path, core_vocab_path, shapes_path
                        )
                        ratios.append(ratio)
                        core_ratios.append(core_ratio)
                    except Exception as e:
                        print(f"Error processing {shapes_path}: {e}")

            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                avg_core_ratio = sum(core_ratios) / len(core_ratios)
                records.append({
                    "experiment": run,
                    "model": model,
                    "unknown_shacl_ratio": avg_ratio,
                    "unknown_shacl_core_ratio": avg_core_ratio
                })
    
    df = pd.DataFrame(records)
    df["prompt"] = df["experiment"].apply(lambda x: x.split("_")[0])

    # Aggregate: sum Total Graphs, mean the rest
    macro_avg_df = df.groupby(["prompt", "model"], as_index=False).agg({
        "unknown_shacl_ratio": "mean",
        "unknown_shacl_core_ratio": "mean"
    })

    
    if save_path:
        macro_avg_df.to_csv(save_path, index=False)

    return macro_avg_df