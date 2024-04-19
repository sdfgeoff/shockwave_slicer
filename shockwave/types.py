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
    normal: Normal


class LineString:
    points: List[LineStringPoint]


@dataclass
class Slice():
    volume: ManifoldVolume
    surface: Surface



class Configuration(BaseModel):
    LAYER_HEIGHT: float = 0.3
    LAYER_PERMISSABLE_ANGLE_DEGREES: float = 15
    PRINT_BED_SURFACE: str = "Bed.stl"
    PRINT_VOLUME_HEIGHT: float = 200


    volumetric_flow_mm3s: float = 7
    filament_diameter_mm: float = 1.75
    max_print_feedrate_mm_s: float = 300

    bed_temperature: float = 60
    extruder_temperature: float = 200
    fan_speed: float = 255

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


