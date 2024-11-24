from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pywavefront


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, obj_file, parent=None):
        super().__init__(parent)
        self.obj_file = obj_file
        self.scene = None
        self.rotation_x = 0  # Obrót wokół osi X
        self.rotation_y = 0  # Obrót wokół osi Y
        self.last_mouse_position = None  # Ostatnia pozycja myszy
        self.zoom = -5.0  # Domyślna odległość kamery (negatywne wartości, bo kamera patrzy na -Z)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.2, 0.3, 1.0)  # Kolor tła

        # Wczytaj model
        self.scene = pywavefront.Wavefront(self.obj_file, collect_faces=True)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.zoom)  # Użyj zmiennej zoom do przybliżania i oddalania

        # Obracanie sceny
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)  # Obrót wokół osi X
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)  # Obrót wokół osi Y

        # Rysuj model
        if self.scene:
            self.draw_model()

    def draw_model(self):
        glBegin(GL_TRIANGLES)
        for name, mesh in self.scene.meshes.items():
            for face in mesh.faces:
                for vertex_index in face:
                    vertex = self.scene.vertices[vertex_index]
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
        """
        Obsługa scrollowania myszy w celu przybliżania i oddalania obiektu.
        """
        delta = event.angleDelta().y() / 120  # Przesunięcie rolki (120 = jeden "skok")
        self.zoom += delta * 0.2  # Zmiana zoomu, dostosuj szybkość przybliżania
        self.update()  # Wywołaj ponowne rysowanie


    def load_model(self, obj_file):
        """Przeładuj nowy model 3D."""
        self.obj_file = obj_file
        self.scene = pywavefront.Wavefront(self.obj_file, collect_faces=True)
        self.update()  # Wywołanie ponownego rysowania