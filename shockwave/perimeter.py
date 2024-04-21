"""
This file takes in slices and generates perimeters/infill for the slices
"""

from typing import List
import trimesh
import numpy as np
from .types import LineString, Slice


def generate_extrusions(config, slice: Slice) -> List[LineString]:
    """
    Generate extrusions for a slice
    """

    edges = trimesh.geometry.faces_to_edges(slice.surface.faces)
    edges_sorted = np.sort(edges, axis=1)
    # edges which only occur once are on the boundary of the polygon
    edges_unique = trimesh.grouping.group_rows(edges_sorted, require_count=1)
    boundary_edges = edges[edges_unique]


    print(boundary_edges)

    return []