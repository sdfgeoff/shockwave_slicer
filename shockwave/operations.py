from typing import Any, List
import trimesh
import numpy as np
from . import util
import manifold3d



def extrude(mesh: trimesh.Trimesh, distance: float):
    faces_to_extrude = mesh.faces

    # stack the (n,3) faces into (3*n, 2) edges
    edges = trimesh.geometry.faces_to_edges(faces_to_extrude)
    edges_sorted = np.sort(edges, axis=1)
    # edges which only occur once are on the boundary of the polygon
    edges_unique = trimesh.grouping.group_rows(edges_sorted, require_count=1)

    edges_extruding = edges[edges_unique]

    # (n, 3, 2) set of line segments (positions, not references)
    boundary = mesh.vertices[edges_extruding]
    boundary_normals = mesh.vertex_normals[edges_extruding] * distance

    # we are creating two vertical triangles for every 3D line segment
    # on the boundary of the 3D triangulation
    vertical = np.tile(boundary.reshape((-1, 3)), 2).reshape((-1, 3))
    boundary_direction = np.tile(boundary_normals.reshape((-1, 3)), 2).reshape((-1, 3))
    vertical[1::2] += boundary_direction[1::2]
    vertical_faces = np.tile([3, 1, 2, 2, 1, 0], (len(boundary), 1))
    vertical_faces += np.arange(len(boundary)).reshape((-1, 1)) * 4
    vertical_faces = vertical_faces.reshape((-1, 3))

    # reversed order of vertices, i.e. to flip face normals
    bottom_faces_seq = faces_to_extrude[:, ::-1]

    top_faces_seq = faces_to_extrude.copy()

    # a sequence of zero- indexed faces, which will then be appended
    # with offsets to create the final mesh

    # manually create vertex and face arrays so that we have explicit ID's
    faces = []
    faces.extend(bottom_faces_seq)
    faces.extend(top_faces_seq + len(mesh.vertices))
    faces.extend(vertical_faces + len(mesh.vertices) + len(mesh.vertices))

    vertices = []
    vertices.extend(mesh.vertices)
    vertices.extend(mesh.vertices.copy() + mesh.vertex_normals * distance)
    vertices.extend(vertical)

    # faces_seq = [bottom_faces_seq,
    #              top_faces_seq,
    #              vertical_faces]
    # vertices_seq = [mesh.vertices,
    #                 mesh.vertices.copy() +  mesh.vertex_normals * distance,
    #                 vertical]

    # # append sequences into flat nicely indexed arrays
    # vertices, faces = trimesh.util.append_faces(vertices_seq, faces_seq)

    # create mesh object
    extruded_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    extruded_mesh.fix_normals()  # somehow face normals are inverted for some `direction`, fixing it here
    return extruded_mesh


def inflate(mesh: trimesh.Trimesh, distance: float) -> trimesh.Trimesh:
    return trimesh.Trimesh(
        vertices=mesh.vertices + mesh.vertex_normals * distance, faces=mesh.faces
    )


def approx_minkowski(mesh1: trimesh.Trimesh, mesh2: trimesh.Trimesh) -> trimesh.Trimesh:
    # This is not a true minkowski sum. It is the convex hull of the minkowski sum, which
    # is a faster approximation as it doens't need convex decomposition.
    # However it is only valid for parts without holes in them, so will need to be replaced soon
    all_verts = []
    for vert in mesh1.vertices:
        for vert2 in mesh2.vertices:
            all_verts.append(vert + vert2)
    return trimesh.convex.convex_hull(all_verts)

def exact_minkowski(mesh1: trimesh.Trimesh, mesh2: trimesh.Trimesh) -> trimesh.Trimesh:
    # This is a true minkowski sum, but it is very slow as it assumes the entire input meshes are all concave
    # It should be replaced with a faster algorithm soon

    convex1 = []
    if trimesh.convex.is_convex(mesh1):
        convex1.append(mesh1.vertices)
    else:
        for face in mesh1.faces:
            verts = []
            for vert in face:
                verts.append(mesh1.vertices[vert])
            convex1.append(verts)

    convex2 = []
    if trimesh.convex.is_convex(mesh2):
        convex2.append(mesh2.vertices)
    else:
        for face in mesh2.faces:
            verts = []
            for vert in face:
                verts.append(mesh2.vertices[vert])
            convex2.append(verts)

    volumes = []
    for verts1 in convex1:
        for verts2 in convex2:
            verts = []
            for vert in verts1:
                for vert2 in verts2:
                    verts.append(vert + vert2)
            hull = trimesh.convex.convex_hull(verts)
            volumes.append(util.mesh_to_manifold(hull))

    unioned = manifold3d.Manifold.batch_boolean(volumes, manifold3d.OpType.Add)
    as_mesh = util.manifold_to_mesh(unioned)

    if not as_mesh.is_watertight:
        print("Warning: Minkowski sum is not watertight")
        as_mesh.export("non-watertight.obj")
        as_mesh.show()
    assert as_mesh.is_watertight
    return as_mesh


def get_mesh_faces_in_direction(mesh, direction_normal, angle_tolerance=0.01) -> trimesh.Trimesh:
    tol_dot = np.cos(angle_tolerance)
    face_idxs = []
    for face_idx, face_normal in enumerate(mesh.face_normals):
        face_normal = face_normal / np.linalg.norm(face_normal)
        face_dir_dot = np.dot(face_normal, direction_normal)
        if face_dir_dot > tol_dot:  # face normal in same direction ?
            face_idxs.append(face_idx)

    return trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces[face_idxs])
