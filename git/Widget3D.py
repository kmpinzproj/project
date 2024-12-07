from PySide6.QtGui import Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pywavefront
import numpy as np
from PIL import Image
import os


def compute_normals(vertices, faces):
    normals = np.zeros(vertices.shape, dtype=np.float32)
    for face in faces:
        v1, v2, v3 = vertices[face]
        edge1 = v2 - v1
        edge2 = v3 - v1
        normal = np.cross(edge1, edge2)
        norm = np.linalg.norm(normal)
        if norm != 0:
            normal /= norm
        for vertex in face:
            normals[vertex] += normal
    normals = np.array(
        [normal / np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else normal for normal in normals])
    return normals


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, obj_file, rails_obj_file, parent=None):
        super().__init__(parent)
        self.obj_file = obj_file
        self.rails_obj_file = rails_obj_file
        self.scene = None
        self.rails_scene = None
        self.gate_vertices = None
        self.gate_faces = None
        self.rails_vertices = None
        self.rails_faces = None

        self.vertices = None
        self.faces = None
        self.normals = None
        self.texture_id = None
        self.material_textures = {}
        self.uv_coordinates = None
        self.rotation_x = 0
        self.rotation_y = 0
        self.last_mouse_position = None
        self.zoom = -4.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_FLAT)
        glEnable(GL_MULTISAMPLE)
        glClearColor(0.1, 0.2, 0.3, 1.0)

        ambient_light = [0.3, 0.3, 0.3, 1.0]
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_light)

        light_position = [5.0, 5.0, 10.0, 1.0]  # Ustaw światło nad i przed bramą        ambient_light = [0.5, 0.5, 0.5, 1.0]  # Więcej światła otoczenia
        diffuse_light = [0.7, 0.7, 0.7, 1.0]  # Zmniejsz intensywność światła rozproszonego
        specular_light = [0.2, 0.2, 0.2, 1.0]  # Zmniejsz odbicia
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)

        glEnable(GL_LIGHT1)
        light1_position = [-5.0, 10.0, 10.0, 1.0]
        glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])

        self.load_model(self.obj_file)
        self.load_rails(self.rails_obj_file)  # Szyny

    def load_texture(self, texture_file, rotation_angle=90):
        if not os.path.exists(texture_file):
            print(f"UWAGA: Plik tekstury {texture_file} nie istnieje.")
            return None

        image = Image.open(texture_file)

        # Obrót tekstury
        if rotation_angle != 0:
            image = image.rotate(rotation_angle, expand=True)

        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image_data = image.convert("RGBA").tobytes()
        width, height = image.size

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glEnable(GL_TEXTURE_2D)
        return texture_id

    def load_model(self, obj_file):
        self.scene = pywavefront.Wavefront(obj_file, collect_faces=True, parse=True)
        self.vertices = np.array(self.scene.vertices)
        self.faces = np.concatenate([mesh.faces for name, mesh in self.scene.meshes.items()])

        # Parsowanie pliku .mtl
        mtl_path = obj_file.replace('.obj', '.mtl')  # Zakładamy, że plik .mtl ma tę samą nazwę
        material_textures = self.parse_mtl_file(mtl_path)

        # Przypisywanie tekstur do materiałów
        for material_name, material in self.scene.materials.items():
            if material_name in material_textures:
                texture_path = material_textures[material_name]
                self.material_textures[material_name] = self.load_texture(texture_path)
            else:
                print(f"Brak tekstury dla materiału {material_name}")

        # Debug UV współrzędnych
        if hasattr(self.scene.parser, 'tex_coords'):
            self.uv_coordinates = np.array(self.scene.parser.tex_coords, dtype=np.float32)
        else:
            print("Brak UV współrzędnych w modelu.")

        self.normals = compute_normals(self.vertices, self.faces)
        adjusted_center = self.compute_adjusted_center(self.vertices)
        self.vertices -= adjusted_center
        self.update()

    @staticmethod
    def parse_mtl_file(mtl_path):
        texture_map = {}
        try:
            with open(mtl_path, 'r', encoding='utf-8') as file:
                material_name = None
                for line in file:
                    if line.startswith("newmtl"):
                        material_name = line.split()[1].strip()
                    elif line.startswith("map_Kd") and material_name:
                        texture_path = line.split(maxsplit=1)[1].strip()
                        texture_map[material_name] = texture_path
            return texture_map
        except Exception as e:
            print(f"Błąd podczas parsowania pliku .mtl: {e}")
            return {}

    def draw_model(self):
        scale_uv = 8.0  # Skalowanie UV (liczba powtórzeń tekstury na osi X i Y)
        for mesh in self.scene.meshes.values():
            texture_id = None
            if mesh.materials:
                material = mesh.materials[0]
                texture_id = self.material_textures.get(material.name)

            if texture_id:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                # Ustaw tryb powielania tekstury w OpenGL
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            else:
                glDisable(GL_TEXTURE_2D)

            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_idx in face:
                    if texture_id and self.uv_coordinates is not None and vertex_idx < len(self.uv_coordinates):
                        # Skalowanie UV
                        uv = self.uv_coordinates[vertex_idx]
                        glTexCoord2f(uv[0] * scale_uv, uv[1] * scale_uv)
                    glNormal3fv(self.normals[vertex_idx])
                    glVertex3fv(self.vertices[vertex_idx])
            glEnd()

            if texture_id:
                glBindTexture(GL_TEXTURE_2D, 0)
                glDisable(GL_TEXTURE_2D)

    def compute_adjusted_center(self, vertices):
        min_y = np.min(vertices[:, 1])
        max_y = np.max(vertices[:, 1])
        center_y = (min_y + max_y) / 2
        centroid = np.mean(vertices, axis=0)
        adjusted_center = np.array([centroid[0], center_y, centroid[2]])
        return adjusted_center

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    @staticmethod
    def load_obj_simple(filepath):
        vertices = []
        faces = []
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    if line.startswith('v '):  # Wczytaj wierzchołki
                        vertices.append([float(v) for v in line.split()[1:]])
                    elif line.startswith('f '):  # Wczytaj twarze
                        face = [int(idx.split('/')[0]) - 1 for idx in line.split()[1:]]
                        faces.append(face)
            return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.int32)
        except Exception as e:
            print(f"Error loading OBJ file {filepath}: {e}")
            return None, None

    def load_rails(self, obj_file):
        """Ładowanie szyn z pliku .obj za pomocą własnego parsera."""
        vertices, faces = self.load_obj_simple(obj_file)
        self.vertices = np.array(self.scene.vertices)

        if vertices is not None and faces is not None:
            self.rails_vertices = vertices
            self.rails_faces = faces
        else:
            print("Error loading rails data.")

    def draw_rails(self):
        """Renderowanie szyn z ustalonym kolorem."""
        if not hasattr(self, 'rails_vertices') or not hasattr(self, 'rails_faces'):
            print("No rails data to render.")
            return

        glDisable(GL_TEXTURE_2D)
        glColor3f(0.5, 0.5, 0.5)  # Kolor szary dla szyn
        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.0)  # Tymczasowe przesunięcie szyn w stronę kamery
        glBegin(GL_TRIANGLES)
        for face in self.rails_faces:
            # Sprawdź, czy twarz ma więcej niż trzy wierzchołki
            for i in range(1, len(face) - 1):
                v1 = self.rails_vertices[face[0]]
                v2 = self.rails_vertices[face[i]]
                v3 = self.rails_vertices[face[i + 1]]
                # Oblicz normalne dla trójkąta
                normal = np.cross(v2 - v1, v3 - v1)
                normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else normal
                glNormal3fv(normal)
                glVertex3fv(v1)
                glVertex3fv(v2)
                glVertex3fv(v3)
        glEnd()
        glPopMatrix()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.pan_x, self.pan_y - 1.2, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        # Renderowanie bramy
        if self.scene:
            self.draw_model()

        # Renderowanie szyn
        if self.rails_vertices is not None and self.rails_faces is not None:
            self.draw_rails()
        else:
            print("No rails to render.")

    def mousePressEvent(self, event):
        self.last_mouse_position = event.position()

    def mouseMoveEvent(self, event):
        if self.last_mouse_position is not None:
            dx = event.position().x() - self.last_mouse_position.x()
            dy = event.position().y() - self.last_mouse_position.y()

            if event.buttons() & Qt.RightButton:  # Przesuwanie
                self.pan_x += dx * 0.01
                self.pan_y -= dy * 0.01
                self.update()

            elif event.buttons() & Qt.LeftButton:  # Obracanie
                self.rotation_x += dy * 0.5
                self.rotation_y += dx * 0.5
                self.update()

        self.last_mouse_position = event.position()

    def mouseReleaseEvent(self, event):
        self.last_mouse_position = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom += delta * 0.2
        self.update()

    def mouseDoubleClickEvent(self, event):
        self.rotation_x = 0
        self.rotation_y = 0
        bounding_box = np.ptp(self.vertices, axis=0)
        max_dimension = np.max(bounding_box)
        self.zoom = -(max_dimension * 1.5)
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()

