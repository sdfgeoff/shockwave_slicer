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




def slice_volume(config: Configuration, volume: ManifoldVolume) -> List[Slice]:

    assert volume.is_watertight

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
    nozzle_cone.vertices -= [0, 0, nozzle_cone_height / 2]
    assert nozzle_cone.is_watertight
    assert nozzle_cone.is_volume

    slices = []

    previous_printed_surface = util.get_print_bed_surface(config)
    previous_printed_volume = operations.extrude(previous_printed_surface, config.LAYER_HEIGHT)
    for i in range(25):
        print(i)

        extended_surface = operations.inflate(previous_printed_surface, config.LAYER_HEIGHT)
        printable_volume = operations.approx_minkowski(extended_surface, nozzle_cone)
        assert printable_volume.is_watertight

        volume_we_want_to_print = volume.intersection(
            printable_volume, engine="manifold"
        )
        volume_we_want_to_print = volume_we_want_to_print.difference(
            previous_printed_volume, engine="manifold"
        )

        if volume_we_want_to_print.is_empty:
            break

        if not volume_we_want_to_print.is_watertight:
            volume_we_want_to_print.export("failed_watertight.obj")
            raise Exception("Volume is not watertight")

        surface_to_print = operations.get_mesh_faces_in_direction(
            volume_we_want_to_print,
            [0, 0, 1],
            angle_tolerance=np.radians(config.LAYER_PERMISSABLE_ANGLE_DEGREES * 2),
        )

        slice = Slice(
            volume=volume_we_want_to_print,
            surface=surface_to_print,
        )
        slices.append(slice)

        previous_printed_volume = operations.inflate(
            volume_we_want_to_print, 0.01
        ).union(previous_printed_volume)
        if not previous_printed_volume.is_watertight:
            previous_printed_volume.export("failed_watertight.obj")
            # print_surfaces_mesh = trimesh.util.concatenate(print_surfaces)
            # print_surfaces_mesh.export("surfaces.obj")

            # print_surfaces_mesh.show()
            raise Exception("Volume is not watertight")
        previous_printed_surface = surface_to_print

    # Create a mesh of all the surfaces
    print_surfaces = [slice.surface for slice in slices]
    print_surfaces_mesh: trimesh.Trimesh = trimesh.util.concatenate(print_surfaces)
    print_surfaces_mesh.show()

    return slices

    # Minkowski causes vertex count to increase a lot every iteration.
    # -> Drape method? Select bounding, extend and move on Z?
    # -> Facets to simplify?
