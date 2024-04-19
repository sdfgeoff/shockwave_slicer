import functools
from .types import Configuration
import trimesh


def load_mesh(path: str) -> trimesh.Trimesh:
    return trimesh.load_mesh(path)

@functools.lru_cache
def get_print_bed_surface(config: Configuration) -> trimesh.Trimesh:
    mesh: trimesh.Trimesh = load_mesh(config.PRINT_BED_SURFACE)
    return mesh
