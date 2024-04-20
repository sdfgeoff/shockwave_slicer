from .types import Configuration, ManifoldVolume
from . import util
from . import operations
import trimesh


def ensure_manifold_and_on_bed(config: Configuration, model: trimesh.Trimesh) -> ManifoldVolume:

    assert model.is_watertight, "Model is not watertight and ensure_manifold can't handle this yet"
    model_manifold = util.mesh_to_manifold(model)

    print_bed_surface = util.get_print_bed_surface(config)

    # Discard anything outside print bed bounds
    print_volume = operations.extrude(print_bed_surface, config.PRINT_VOLUME_HEIGHT)
    assert print_volume.is_watertight
    print_volume_manifold = util.mesh_to_manifold(print_volume)

    model_clipped = model_manifold.__xor__(print_volume_manifold)
    return model_clipped
