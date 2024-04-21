from typing import List, TypeAlias
from pydantic import BaseModel
from dataclasses import dataclass
import trimesh
import manifold3d


GenericModel: TypeAlias = trimesh.Trimesh
ManifoldVolume: TypeAlias = manifold3d.Manifold
Surface: TypeAlias = trimesh.Trimesh


class Position:
    x: float
    y: float
    z: float


class Normal:
    x: float
    y: float
    z: float


class LineStringPoint:
    position: Position
    """ The location of this point in 3D space."""

    normal: Normal
    """
    A normal to the line that indicates what direction an extruder should approach this point from.
    The nozzle points along the negative directin, so a normal of (0,0,1) will have the extruder approach
    from the top/positive Z direction.
    """

    area: float
    """ The cross-sectional area at this point of the line. This can be used to determine the
    volume of the line by multiplying by the distance to the next point."""


class LineString:
    points: List[LineStringPoint]


@dataclass
class Slice():
    volume: ManifoldVolume
    surface: Surface