from typing import NamedTuple
from pydantic import BaseClass
import math
from .types import Configuration


class Position(NamedTuple):
    x: float
    y: float
    z: float




class PrinterState(NamedTuple):
    position: Position
    extrusion_mm: float


GCodeReturn = tuple[PrinterState, tuple[str, ...]]


def distance(start_position: Position, end_position: Position) -> float:
    """
    Return the distance between two positions
    """
    return (
        (start_position.x - end_position.x) ** 2
        + (start_position.y - end_position.y) ** 2
        + (start_position.z - end_position.z) ** 2
    ) ** 0.5


def setup(conf: Configuration) -> GCodeReturn:
    """
    Emit GCode for printer setup
    """
    return (
        PrinterState(Position(0, 0, 0), 0),
        (
            f"M82 ; Set extruder to absolute positioning",
            f"M140 S{conf.bed_temperature} ; Set bed temperature",
            f"M104 S{conf.extruder_temperature} ; Set extruder temperature",
            f"M106 S{int(conf.fan_speed * 255)} ; Set fan speed",
        ),
    )


def extrude(
    conf: Configuration,
    state: PrinterState,
    end_position: Position,
    material_mm3: float,
) -> GCodeReturn:
    """
    Emit GCode for a volumetric extrusion of material from start_position to end_position
    """
    extrusion_move_distance = distance(state.position, end_position)
    extrusion_time = extrusion_move_distance / conf.volumetric_flow_mm3s
    feedrate_mm3s = material_mm3 / extrusion_time

    filament_area = (conf.filament_diameter_mm / 2) ** 2 * math.pi
    extrude_position = state.extrusion_mm + material_mm3 / filament_area

    return (
        state._replace(position=end_position, extrusion_mm=extrude_position),
        (
            f"G1 X{end_position.x} Y{end_position.y} Z{end_position.z} E{extrude_position} F{feedrate_mm3s}",
        ),
    )


def travel(
    conf: Configuration, state: PrinterState, end_position: Position
) -> GCodeReturn:
    """
    Emit GCode for a travel move from start_position to end_position
    """

    return (
        state._replace(position=end_position),
        (f"G0 X{end_position.x} Y{end_position.y} Z{end_position.z}",),
    )
