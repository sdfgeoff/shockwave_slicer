from manifold3d import Manifold
from manifold3d import Mesh
import trimesh
import numpy as np

from . import operations


LAYER_HEIGHT = 0.3
LAYER_PERMISSABLE_ANGLE = 15
PRINT_VOLUME_HEIGHT = 200

# Print bed
PRINT_BED_SURFACE = trimesh.load_mesh("Bed.stl")

# todo: use trimesh library
# MODEL = Mesh("suzanne.stl")
MODEL = trimesh.load_mesh("TestModel.stl")



# Test extrude using trimesh
# test_extruded = operations.extrude(trimesh.load_mesh("extrude_test.stl"), 10)
# test_extruded.show()
# exit(0)

assert MODEL.is_watertight

# Discard anything outside print bed bounds
print_volume = operations.extrude(PRINT_BED_SURFACE, PRINT_VOLUME_HEIGHT)
assert print_volume.is_watertight

model_clipped = MODEL.intersection(print_volume)
assert model_clipped.is_watertight


# The nozzle cone descibes where the nozzle can print given a piece of existing geometry at (0,0,0)
# A cone is just an approxmiation.
# - A hypothetical 6DOF printer would have a sphere
nozzle_cone_height = 2 * LAYER_HEIGHT
nozzle_cone_radius = np.tan(np.radians(90 - LAYER_PERMISSABLE_ANGLE)) * nozzle_cone_height
nozzle_cone = trimesh.creation.cone(
    radius=nozzle_cone_radius,
    height=nozzle_cone_height,
    sections=8,
)
nozzle_cone.vertices -= [0, 0, nozzle_cone_height / 2]
assert nozzle_cone.is_watertight
assert nozzle_cone.is_volume

print_surfaces = []
print_volumes = []

previous_printed_surface = PRINT_BED_SURFACE
previous_printed_volume = operations.extrude(previous_printed_surface, LAYER_HEIGHT)
for i in range(100):
    print(i)

    extended_surface = operations.inflate(previous_printed_surface, LAYER_HEIGHT)
    printable_volume = operations.approx_minkowski(extended_surface, nozzle_cone)
    assert printable_volume.is_watertight


    volume_we_want_to_print = model_clipped.intersection(printable_volume, engine='manifold')
    volume_we_want_to_print = volume_we_want_to_print.difference(previous_printed_volume, engine="manifold")

    if volume_we_want_to_print.is_empty:
        break 

    if not volume_we_want_to_print.is_watertight:
        volume_we_want_to_print.export('failed_watertight.obj')
        raise Exception("Volume is not watertight")

    surface_to_print = operations.get_mesh_faces_in_direction(volume_we_want_to_print, [0, 0, 1], angle_tolerance=np.radians(LAYER_PERMISSABLE_ANGLE * 2))
    print_surfaces.append(surface_to_print)
    print_volumes.append(volume_we_want_to_print)

    previous_printed_volume = operations.inflate(volume_we_want_to_print, 0.01).union(previous_printed_volume)
    if not previous_printed_volume.is_watertight:
        previous_printed_volume.export('failed_watertight.obj')
        print_surfaces_mesh = trimesh.util.concatenate(print_surfaces)
        print_surfaces_mesh.export('surfaces.obj')

        print_surfaces_mesh.show()
        raise Exception("Volume is not watertight")
    previous_printed_surface = surface_to_print

# Create a mesh of all the surfaces
print_surfaces_mesh = trimesh.util.concatenate(print_surfaces)
print_surfaces_mesh.show()

# Minkowski causes vertex count to increase a lot every iteration. 
# -> Drape method? Select bounding, extend and move on Z?
# -> Facets to simplify?