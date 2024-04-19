from manifold3d import Manifold
from manifold3d import Mesh
import trimesh

from . import operations
from .types import Configuration
from .slicer import slice_volume
from . import util



PRINT_VOLUME_HEIGHT = 200



if __name__ == "__main__":
    # Print bed
    # todo: use trimesh library
    # MODEL = Mesh("suzanne.stl")
    MODEL = util.load_mesh("TestModel.stl")

    config = Configuration()


    print_bed_surface = util.get_print_bed_surface(config)

    # Test extrude using trimesh
    # test_extruded = operations.extrude(trimesh.load_mesh("extrude_test.stl"), 10)
    # test_extruded.show()
    # exit(0)

    # Discard anything outside print bed bounds
    print_volume = operations.extrude(print_bed_surface, PRINT_VOLUME_HEIGHT)
    assert print_volume.is_watertight

    model_clipped = MODEL.intersection(print_volume)
    assert model_clipped.is_watertight

    slices = slice_volume(config, model_clipped)
