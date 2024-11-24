from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pywavefront
import numpy as np


def compute_normals(vertices, faces):
    """Oblicza normalne dla podanych wierzchołków i ścian."""
    normals = np.zeros(vertices.shape, dtype=np.float32)

    for face in faces:
        # Pobierz wierzchołki trójkąta
        v1, v2, v3 = vertices[face]
        # Oblicz wektory krawędzi trójkąta
        edge1 = v2 - v1
        edge2 = v3 - v1
        # Oblicz iloczyn wektorowy (normalną)
        normal = np.cross(edge1, edge2)
        normal = normal / np.linalg.norm(normal)  # Normalizacja wektora
        # Dodaj normalną do każdego wierzchołka trójkąta
        for vertex in face:
            normals[vertex] += normal

    # Normalizacja normalnych dla każdego wierzchołka
    normals = np.array([normal / np.linalg.norm(normal) for normal in normals])
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
        self.rotation_x = 0  # Obrót wokół osi X
        self.rotation_y = 0  # Obrót wokół osi Y
        self.last_mouse_position = None  # Ostatnia pozycja myszy
        self.zoom = -5.0  # Domyślna odległość kamery (negatywne wartości, bo kamera patrzy na -Z)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)  # Włącz test głębokości
        glEnable(GL_LIGHTING)  # Włącz system oświetlenia
        glEnable(GL_LIGHT0)  # Główne światło
        glEnable(GL_NORMALIZE)  # Automatyczne normalizowanie wektorów normalnych
        glShadeModel(GL_SMOOTH)  # Płynne cieniowanie (Gouraud)
        glEnable(GL_MULTISAMPLE)  # Włącza antyaliasing
        # Tło
        glClearColor(0.1, 0.2, 0.3, 1.0)  # Niebieskie tło

        # Ustawienia światła ambient (otoczenia)
        ambient_light = [0.3, 0.3, 0.3, 1.0]  # Delikatne światło otoczenia
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_light)

        # Główne światło punktowe
        diffuse_light = [0.8, 0.8, 0.8, 1.0]  # Jasne światło rozproszone
        specular_light = [0.5, 0.5, 0.5, 1.0]  # Subtelne światło odbite

        # Zmieniona pozycja światła
        light_position = [2.0, 5.0, 2.0, 1.0]  # Światło ustawione wyżej
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        # Materiały
        material_ambient = [0.2, 0.2, 0.2, 1.0]
        material_diffuse = [0.6, 0.6, 0.6, 1.0]
        material_specular = [0.4, 0.4, 0.4, 1.0]  # Subtelne odbicie
        shininess = 50.0  # Połysk materiału

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, material_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, material_specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

        # Wczytaj model
        self.scene = pywavefront.Wavefront(self.obj_file, collect_faces=True)
        self.vertices = np.array(self.scene.vertices)
        self.faces = np.concatenate([mesh.faces for name, mesh in self.scene.meshes.items()])

        # Oblicz poprawiony środek i przesunięcie
        adjusted_center = self.compute_adjusted_center(self.vertices)
        self.vertices -= adjusted_center  # Przesuń model, aby był wyśrodkowany

        # Oblicz normalne
        self.normals = compute_normals(self.vertices, self.faces)

    def resizeGL(self, width, height):
        # Zwiększenie obszaru renderowania (2x więcej pikseli)
        render_width = width * 2
        render_height = height * 2
        glViewport(0, 0, render_width, render_height)  # Renderuj w zwiększonej "rozdzielczości"
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.zoom)

        # Obracanie sceny
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        # Rysuj model
        if self.scene:
            self.draw_model()

    def draw_model(self):
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            vertices = [self.vertices[vertex_index] for vertex_index in face]
            normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
            normal = normal / np.linalg.norm(normal)  # Normalizacja wektora normalnego
            glNormal3fv(normal)  # Ustaw normalną dla trójkąta

            for vertex in vertices:
                glVertex3fv(vertex)
        glEnd()

    def mousePressEvent(self, event):
        self.last_mouse_position = event.position()

    def mouseMoveEvent(self, event):
        if self.last_mouse_position is not None:
            dx = event.position().x() - self.last_mouse_position.x()
            dy = event.position().y() - self.last_mouse_position.y()
            self.rotation_x += dy * 0.5  # Obrót w pionie
            self.rotation_y += dx * 0.5  # Obrót w poziomie
            self.update()
        self.last_mouse_position = event.position()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom += delta * 0.2
        self.update()

    def load_model(self, obj_file):
        """Przeładuj nowy model 3D."""
        self.obj_file = obj_file
        self.scene = pywavefront.Wavefront(self.obj_file, collect_faces=True)
        self.vertices = np.array(self.scene.vertices)
        self.faces = np.concatenate([mesh.faces for name, mesh in self.scene.meshes.items()])

        # Oblicz poprawiony środek i przesunięcie
        adjusted_center = self.compute_adjusted_center(self.vertices)
        self.vertices -= adjusted_center  # Przesuń model, aby był wyśrodkowany

        # Oblicz normalne
        self.normals = compute_normals(self.vertices, self.faces)
        self.update()

    def compute_model_center(self, vertices):
        """
        Oblicza środek modelu na podstawie wierzchołków.
        """
        centroid = np.mean(vertices, axis=0)  # Środek modelu
        return centroid

    def compute_adjusted_center(self, vertices):
        """
        Oblicza poprawiony środek modelu, aby był wyśrodkowany na osi Y.
        """
        min_y = np.min(vertices[:, 1])  # Minimalna wartość Y (dolna krawędź)
        max_y = np.max(vertices[:, 1])  # Maksymalna wartość Y (górna krawędź)
        center_y = (min_y + max_y) / 2  # Środek wysokości
        centroid = np.mean(vertices, axis=0)  # Centroid na wszystkich osiach

        # Zastąp środek Y wyśrodkowaną wartością zakresu
        adjusted_center = np.array([centroid[0], center_y, centroid[2]])
        return adjusted_center

