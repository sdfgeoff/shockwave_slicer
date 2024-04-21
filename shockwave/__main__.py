from manifold3d import Manifold
from manifold3d import Mesh
import trimesh

from . import operations
from .configuration import Configuration
from .slicer import slice_volume
from . import util

from . import manifold_fixer



def run():
    # Print bed
    # todo: use trimesh library
    #model = util.load_mesh("Suzanne.stl")
    model = util.load_mesh("TestModel.stl")

    config = Configuration()
    
    # Test extrude using trimesh
    # test_extruded = operations.extrude(trimesh.load_mesh("extrude_test.stl"), 10)
    # test_extruded.show()
    # exit(0)

    manifold_geom = manifold_fixer.ensure_manifold_and_on_bed(config, model)

    slices = slice_volume(config, manifold_geom)

    # Create a mesh of all the surfaces
    print_surfaces = [slice.surface for slice in slices]
    print_surfaces_mesh: trimesh.Trimesh = trimesh.util.concatenate(print_surfaces)
    print_surfaces_mesh.show()

    print_surfaces_mesh.export("slices.obj")





if __name__ == "__main__":
    run()
   
