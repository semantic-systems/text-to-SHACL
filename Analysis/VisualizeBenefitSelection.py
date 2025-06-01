"""
VisualizeBenefitSelection.py

Create Sankey diagram that visualizes the selection process of selecting 
suitable social benefits from all administrative services.
"""

import plotly.graph_objects as go
from typing import List

def create_benefits_selection_sankey(node_labels: List[str], 
                                     node_colors: List[str], 
                                     sources: List[str], 
                                     targets: List[str],
                                     values: List[int],
                                     link_colors: List[str],
                                     save_path: str = None):
    """Create a Sankey diagram to visualize the selection of benefits.
    
    :param node_labels: List of node labels.
    :param node_colors: List of node colors (hex).
    :param sources: List of source nodes.
    :param targets: List of target nodes
    :param values: List of values for the links between nodes.
    :param link_colors: List of link colors (hex).
    :param save_path: Optional path to save the Sankey diagram as an SVG file.
    """
    # Convert hex colors to rgba format for Plotly
    rgba_colors = [
        f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.5)"
        for c in link_colors
    ]

    # Create sankey diagram
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="black", width=1),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=[f"{v} items" for v in values],
            color=rgba_colors
        )
    ))

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        width=1200,
        height=600
    )

    # Optionally save to SVG
    if save_path:
        fig.write_image(save_path, format='svg')
        print(f"Sankey diagram saved to: {save_path}")

    fig.show()