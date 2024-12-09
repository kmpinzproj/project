import trimesh
import numpy as np
import matplotlib.pyplot as plt


def is_parallel_to_axis(v0, v1, axis, tolerance=1e-2):
    """
    Sprawdza, czy krawędź jest równoległa do określonej osi (X, Y lub Z).
    """
    vec = v1 - v0
    if axis == 'x':  # Równoległa do osi X
        return np.isclose(vec[1], 0, atol=tolerance) and np.isclose(vec[2], 0, atol=tolerance)
    elif axis == 'y':  # Równoległa do osi Y
        return np.isclose(vec[0], 0, atol=tolerance) and np.isclose(vec[2], 0, atol=tolerance)
    elif axis == 'z':  # Równoległa do osi Z
        return np.isclose(vec[0], 0, atol=tolerance) and np.isclose(vec[1], 0, atol=tolerance)
    return False


def filter_edges(edges, vertices, tolerance=1e-2):
    """
    Filtruje krawędzie, pozostawiając tylko te, które są dokładnie pionowe lub poziome
    względem osi X, Y lub Z w przestrzeni 3D.
    """
    filtered_edges = []
    for edge in edges:
        v0, v1 = vertices[edge[0]], vertices[edge[1]]
        if (is_parallel_to_axis(v0, v1, 'x', tolerance) or
                is_parallel_to_axis(v0, v1, 'y', tolerance) or
                is_parallel_to_axis(v0, v1, 'z', tolerance)):
            filtered_edges.append(edge)
    return filtered_edges


def apply_isometric_projection(vertices):
    """
    Zastosowanie rzutu izometrycznego na wierzchołkach 3D.
    """
    # Macierz transformacji izometrycznej
    iso_matrix = np.array([
        [np.sqrt(3) / 2, 0, -np.sqrt(3) / 2],
        [0.5, 1, 0.5],
        [0, 0, 0]
    ])
    return np.dot(vertices, iso_matrix.T)


def draw_filtered_edges_isometric(obj_file_path, output_image_path):
    """
    Generuje rzut izometryczny z filtrowaniem krawędzi pionowych i poziomych.
    """
    # Wczytaj plik OBJ
    mesh = trimesh.load(obj_file_path)

    # Wyciągnij współrzędne wierzchołków i zastosuj rzut izometryczny
    vertices = mesh.vertices
    projected_vertices = apply_isometric_projection(vertices)

    # Filtracja krawędzi
    edges = filter_edges(mesh.edges, vertices)

    # Rysowanie krawędzi
    plt.figure(figsize=(10, 10))
    for edge in edges:
        v0, v1 = projected_vertices[edge[0]], projected_vertices[edge[1]]
        plt.plot([v0[0], v1[0]], [v0[1], v1[1]], color='black', linewidth=0.5)

    # Ustawienia osi
    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(output_image_path, dpi=300)
    plt.close()


def draw_orthogonal_edges(obj_file_path, output_image_path):
    """
    Generuje zwykły rzut z filtrowaniem krawędzi pionowych i poziomych.
    """
    # Wczytaj plik OBJ
    mesh = trimesh.load(obj_file_path)

    # Wyciągnij współrzędne wierzchołków
    vertices = mesh.vertices

    # Filtracja krawędzi
    edges = filter_edges(mesh.edges, vertices)

    # Rysowanie krawędzi
    plt.figure(figsize=(10, 10))
    for edge in edges:
        v0, v1 = vertices[edge[0]], vertices[edge[1]]
        plt.plot([v0[0], v1[0]], [v0[1], v1[1]], color='black', linewidth=0.5)

    # Ustawienia osi
    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(output_image_path, dpi=300)
    plt.close()


# Ścieżki do plików
input_obj_file = "../generator/model.obj"
output_isometric_file = "../generator/sketch_iso_no_diagonals.png"
output_orthogonal_file = "../generator/sketch_orthogonal.png"

# Generowanie rzutu izometrycznego
draw_filtered_edges_isometric(input_obj_file, output_isometric_file)

# Generowanie zwykłego rzutu
draw_orthogonal_edges(input_obj_file, output_orthogonal_file)