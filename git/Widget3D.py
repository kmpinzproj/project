from PySide6.QtGui import Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pywavefront
import numpy as np
from PIL import Image

def compute_normals(vertices, faces):
    """Oblicza normalne dla podanych wierzchołków i ścian."""
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

    normals = np.array([normal / np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else normal for normal in normals])
    return normals

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, obj_file, parent=None):
        super().__init__(parent)
        self.obj_file = obj_file
        self.setGeometry(100, 100, 1920, 1080)  # Ustaw rozmiar okna na Full HD
        self.scene = None
        self.vertices = None
        self.faces = None
        self.normals = None
        self.texture_id = None
        self.rotation_x = 0
        self.rotation_y = 0
        self.last_mouse_position = None
        self.zoom = -4.0
        self.pan_x = 0.0  # Przesunięcie w osi X
        self.pan_y = 0.0  # Przesunięcie w osi Y

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_MULTISAMPLE)
        glClearColor(0.1, 0.2, 0.3, 1.0)

        ambient_light = [0.3, 0.3, 0.3, 1.0]
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_light)

        diffuse_light = [0.8, 0.8, 0.8, 1.0]
        specular_light = [0.5, 0.5, 0.5, 1.0]
        light_position = [2.0, 5.0, 2.0, 1.0]
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        material_ambient = [0.2, 0.2, 0.2, 1.0]
        material_diffuse = [0.6, 0.6, 0.6, 1.0]
        material_specular = [0.4, 0.4, 0.4, 1.0]
        shininess = 50.0

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, material_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, material_specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

        self.scene = pywavefront.Wavefront(self.obj_file, collect_faces=True)
        self.vertices = np.array(self.scene.vertices)
        self.faces = np.concatenate([mesh.faces for name, mesh in self.scene.meshes.items()])

        adjusted_center = self.compute_adjusted_center(self.vertices)
        self.vertices -= adjusted_center
        self.normals = compute_normals(self.vertices, self.faces)

    def load_texture(self, texture_file):
        """Ładuje teksturę z pliku i ustawia ją jako aktywną teksturę."""
        image = Image.open(texture_file)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image_data = image.convert("RGBA").tobytes()
        width, height = image.size

        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glEnable(GL_TEXTURE_2D)

    def resizeGL(self, width, height):
        glViewport(0, 0, width * 2, height * 2)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(self.pan_x, self.pan_y, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        if self.scene:
            self.draw_model()

    def draw_model(self):
        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        glBegin(GL_TRIANGLES)
        for face in self.faces:
            vertices = [self.vertices[vertex_index] for vertex_index in face]
            normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
            norm = np.linalg.norm(normal)
            if norm != 0:
                normal /= norm
            glNormal3fv(normal)

            for vertex in vertices:
                glVertex3fv(vertex)
        glEnd()

        if self.texture_id:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    def load_model(self, obj_file):
        self.obj_file = obj_file
        self.scene = pywavefront.Wavefront(self.obj_file, collect_faces=True)
        self.vertices = np.array(self.scene.vertices)
        self.faces = np.concatenate([mesh.faces for name, mesh in self.scene.meshes.items()])

        adjusted_center = self.compute_adjusted_center(self.vertices)
        self.vertices -= adjusted_center
        self.normals = compute_normals(self.vertices, self.faces)
        self.update()

    def compute_model_center(self, vertices):
        return np.mean(vertices, axis=0)

    def compute_adjusted_center(self, vertices):
        min_y = np.min(vertices[:, 1])
        max_y = np.max(vertices[:, 1])
        center_y = (min_y + max_y) / 2
        centroid = np.mean(vertices, axis=0)
        adjusted_center = np.array([centroid[0], center_y, centroid[2]])
        return adjusted_center

    def set_texture(self, texture_file):
        self.load_texture(texture_file)
        print(texture_file)
        self.update()

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