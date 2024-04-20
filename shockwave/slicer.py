"""
Converts from manifold geometry into an ordered array of (surface, volume) pairs.
None of the surfaces are watertight, but the volumes are.
When all the volumes are unioned, they should idelaly result in the input geometry.
"""

import trimesh
from typing import List
import numpy as np
from .types import ManifoldVolume, Slice, Configuration
from . import operations
from . import util




def slice_volume(config: Configuration, model: ManifoldVolume) -> List[Slice]:

    # The nozzle cone descibes where the nozzle can print given a piece of existing geometry at (0,0,0)
    # A cone is just an approxmiation.
    # - A hypothetical 6DOF printer would have a sphere
    nozzle_cone_height = 2 * config.LAYER_HEIGHT
    nozzle_cone_radius = (
        np.tan(np.radians(90 - config.LAYER_PERMISSABLE_ANGLE_DEGREES)) * nozzle_cone_height
    )
    nozzle_cone = trimesh.creation.cone(
        radius=nozzle_cone_radius,
        height=nozzle_cone_height,
        sections=8,
    )
    nozzle_cone.vertices -= [0, 0, nozzle_cone_height]
    assert nozzle_cone.is_watertight
    assert nozzle_cone.is_volume

    nozzle_cone.export("NozzleCone.obj")

    slices = []

    previous_printed_surface = util.get_print_bed_surface(config)
    remaining_to_print = model

    for i in range(1000):
        print(i)
        extended_surface = operations.inflate(previous_printed_surface, config.LAYER_HEIGHT)
        printable_volume = operations.approx_minkowski(extended_surface, nozzle_cone)
        assert printable_volume.is_watertight
        printable_volume_manifold = util.mesh_to_manifold(printable_volume)


        inters, diff = remaining_to_print.split(printable_volume_manifold)

        remaining_to_print = diff
        volume_we_want_to_print = inters

        if volume_we_want_to_print.volume == 0:
            break

        surface_to_print = operations.get_mesh_faces_in_direction(
            util.manifold_to_mesh(volume_we_want_to_print),
            [0, 0, 1],
            angle_tolerance=np.radians(config.LAYER_PERMISSABLE_ANGLE_DEGREES * 2),
        )
        previous_printed_surface = surface_to_print


        if len(surface_to_print.faces) == 0:
            break

        slice = Slice(
            volume=volume_we_want_to_print,
            surface=surface_to_print,
        )
        slices.append(slice)


    return slices
