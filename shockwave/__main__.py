from manifold3d import Manifold
from manifold3d import Mesh
import trimesh
import os
import json

from . import operations
from .configuration import Configuration
from .slicer import slice_volume
from .perimeter import generate_extrusions
from . import util

from . import manifold_fixer


CONFIG_FILE_PATH = "config.json"



def run():
    # Print bed
    # todo: use trimesh library
    #model = util.load_mesh("Suzanne.stl")
    model = util.load_mesh("TestModel.stl")

    if not os.path.exists(CONFIG_FILE_PATH):
        print("No config file found, creating one")
        config = Configuration()
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(config.model_dump_json(indent=4))

    else:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = Configuration(**json.load(config_file))
    
    # Test extrude using trimesh
    # test_extruded = operations.extrude(trimesh.load_mesh("extrude_test.stl"), 10)
    # test_extruded.show()
    # exit(0)

    manifold_geom = manifold_fixer.ensure_manifold_and_on_bed(config, model)

    slices = slice_volume(config, manifold_geom)

    # Create a mesh of all the surfaces
    # print_surfaces = [slice.surface for slice in slices]
    # print_surfaces_mesh: trimesh.Trimesh = trimesh.util.concatenate(print_surfaces)
    # print_surfaces_mesh.export("slices.obj")

    # It would be nice to do this in parallel, but manifold objects aren't pickleable
    all_linestrings = []
    for slice in slices:
        linestrings = generate_extrusions(config, slice)
        all_linestrings.extend(linestrings)
        break




if __name__ == "__main__":
    run()
   
