import functools
from manifold3d import Manifold, Mesh
from .types import GenericModel, ManifoldVolume
from .configuration import Configuration
import trimesh
import numpy as np


def load_mesh(path: str) -> GenericModel:
    return trimesh.load_mesh(path)

@functools.lru_cache
def get_print_bed_surface(config: Configuration) -> GenericModel:
    mesh: trimesh.Trimesh = load_mesh(config.printer.print_bed_surface)
    return mesh


def mesh_to_manifold(mesh: GenericModel) -> ManifoldVolume:
    verts = np.array(mesh.vertices)
    faces = np.array(mesh.faces)
    manimesh = Mesh(vert_properties=verts, tri_verts=faces)
    return Manifold(manimesh)


def manifold_to_mesh(manifold: ManifoldVolume) -> GenericModel:
    mesh = manifold.to_mesh()

    if mesh.vert_properties.shape[1] > 3:
        vertices = mesh.vert_properties[:, :3]
        colors = (mesh.vert_properties[:, 3:] * 255).astype(np.uint8)
    else:
        vertices = mesh.vert_properties
        colors = None

    tmesh = trimesh.Trimesh(
        vertices=vertices, faces=mesh.tri_verts, vertex_colors=colors
    )
    return tmesh


def show_manifold(manifold: ManifoldVolume):
    mesh = manifold.to_mesh()

    if mesh.vert_properties.shape[1] > 3:
        vertices = mesh.vert_properties[:, :3]
        colors = (mesh.vert_properties[:, 3:] * 255).astype(np.uint8)
    else:
        vertices = mesh.vert_properties
        colors = None

    tmesh = trimesh.Trimesh(
        vertices=vertices, faces=mesh.tri_verts, vertex_colors=colors
    )
    tmesh.show()