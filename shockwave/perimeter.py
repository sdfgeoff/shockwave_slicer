"""
This file takes in slices and generates perimeters/infill for the slices
"""

from typing import List

from .types import LineString, Slice


def generate_extrusions(slice: Slice) -> List[LineString]:
    """
    Generate extrusions for a slice
    """
    pass