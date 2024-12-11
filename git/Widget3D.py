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
        self.addons_file = "../generator/dodatki/combined_addons.obj"  # Ścieżka do pliku dodatków

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
        self.addons = []  # Lista dodatków (każdy jako dict z vertices i faces)
        self.addon_colors = {}  # Słownik z kolorami dla dodatków (nazwa dodatku -> (R, G, B))

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_FLAT)
        glEnable(GL_MULTISAMPLE)
        glClearColor(0.1, 0.2, 0.3, 1.0)

        glEnable(GL_COLOR_MATERIAL)  # Dodane - umożliwia kolory dla materiałów
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

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
        self.load_addons(self.addons_file)  # Wczytaj dodatki


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

        if hasattr(self.scene.parser, 'tex_coords'):
            self.uv_coordinates = np.array(self.scene.parser.tex_coords, dtype=np.float32)
        else:
            print("Brak UV współrzędnych w modelu.")

        self.normals = compute_normals(self.vertices, self.faces)
        adjusted_center = self.compute_adjusted_center(self.vertices)
        self.vertices -= adjusted_center

        # Obliczenie przekątnej i ustawienie zoomu
        self.set_camera_based_on_model_size()
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
        glPushAttrib(GL_ALL_ATTRIB_BITS)  # Zapisz aktualny stan OpenGL
        scale_uv = 8.0  # Skalowanie UV (liczba powtórzeń tekstury na osi X i Y)
        glDisable(GL_COLOR_MATERIAL)  # Wyłącz koloryzację materiałów dla bramy
        for mesh in self.scene.meshes.values():
            texture_id = None
            if mesh.materials:
                material = mesh.materials[0]
                texture_id = self.material_textures.get(material.name)

            if texture_id:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            else:
                glDisable(GL_TEXTURE_2D)

            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_idx in face:
                    if texture_id and self.uv_coordinates is not None and vertex_idx < len(self.uv_coordinates):
                        uv = self.uv_coordinates[vertex_idx]
                        glTexCoord2f(uv[0] * scale_uv, uv[1] * scale_uv)
                    glNormal3fv(self.normals[vertex_idx])
                    glVertex3fv(self.vertices[vertex_idx])
            glEnd()

            if texture_id:
                glBindTexture(GL_TEXTURE_2D, 0)
                glDisable(GL_TEXTURE_2D)
        glPopAttrib()  # Przywróć poprzedni stan OpenGL

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
        glPushAttrib(GL_ALL_ATTRIB_BITS)  # Zapisz aktualny stan OpenGL
        if not hasattr(self, 'rails_vertices') or not hasattr(self, 'rails_faces'):
            print("No rails data to render.")
            glPopAttrib()
            return

        color = (51 / 255, 56 / 255, 52 / 255)  # Domyślny kolor szary (RGB w skali 0-1)

        glDisable(GL_TEXTURE_2D)  # Wyłącz tekstury dla szyn
        glEnable(GL_COLOR_MATERIAL)  # Włącz kolorowanie
        glColor3f(*color)  # Ustaw kolor szyn

        glPushMatrix()
        glBegin(GL_TRIANGLES)
        for face in self.rails_faces:
            for i in range(1, len(face) - 1):
                v1 = self.rails_vertices[face[0]]
                v2 = self.rails_vertices[face[i]]
                v3 = self.rails_vertices[face[i + 1]]

                normal = np.cross(v2 - v1, v3 - v1)
                normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else normal

                glNormal3fv(normal)
                glColor3f(*color)  # Kolor dla każdego wierzchołka (aby mieć pewność)

                glVertex3fv(v1)
                glVertex3fv(v2)
                glVertex3fv(v3)
        glEnd()
        glPopMatrix()

        glPopAttrib()  # Przywróć poprzedni stan OpenGL

    def clear_addons(self):
        """Czyści wszystkie dodatki i odświeża widok."""
        print(f"Czyszczenie dodatków...")
        self.addons.clear()  # Usunięcie wszystkich danych o dodatkach
        self.update()  # Odśwież widok

    def load_addons(self, obj_file):
        """Ładowanie dodatków z pliku .obj."""
        self.clear_addons()  # Wyczyść poprzednie dodatki

        if not os.path.exists(obj_file):
            print(f"Plik {obj_file} nie istnieje.")
            return

        global_vertex_offset = 0  # Przesunięcie indeksów wierzchołków
        vertices_global = []  # Globalna lista wszystkich wierzchołków
        current_object = {'name': None, 'vertices': [], 'faces': []}

        with open(obj_file, 'r') as file:
            for line in file:
                if line.startswith('o '):  # Nowy obiekt w pliku
                    if current_object['name'] is not None:
                        print(
                            f"Załadowano obiekt: {current_object['name']}, Wierzchołki: {len(current_object['vertices'])}, Twarze: {len(current_object['faces'])}")
                        self.addons.append(current_object)
                        global_vertex_offset += len(current_object['vertices'])
                        vertices_global.extend(current_object['vertices'])

                    current_object = {'name': line.split()[1], 'vertices': [], 'faces': []}

                elif line.startswith('v '):  # Wczytaj wierzchołki
                    vertex = [float(x) for x in line.split()[1:]]
                    current_object['vertices'].append(vertex)

                elif line.startswith('f '):  # Wczytaj twarze
                    face = [int(idx.split('/')[0]) - 1 for idx in line.split()[1:]]
                    shifted_face = [idx - global_vertex_offset for idx in face]
                    current_object['faces'].append(shifted_face)

        if current_object['name'] is not None:
            self.addons.append(current_object)
            vertices_global.extend(current_object['vertices'])

        # Słownik z kolorami dla dodatków
        addon_colors = {
            "wentylacja": (1.0, 0.0, 0.0),  # Czerwony
            "drzwi.001": (51, 56, 52),  # Zielony
            "klamka-1.001": (0, 0, 0),  # Niebieski
            "szyba": (0.5, 0.5, 0.5)  # Szary
        }

        # Ustaw kolory dla wszystkich dodatków
        for addon_name, color in addon_colors.items():
            self.set_addon_color(addon_name, color)

        self.update()  # Odśwież widok po wprowadzeniu zmian

    def draw_addons(self):
        for addon in self.addons:
            glPushAttrib(GL_ALL_ATTRIB_BITS)  # Zapisz aktualny stan OpenGL
            vertices = np.array(addon['vertices'], dtype=np.float32)
            color = addon.get('color', (1.0, 1.0, 1.0))  # Domyślny kolor biały
            glDisable(GL_TEXTURE_2D)  # Wyłącz teksturę dla dodatków
            glEnable(GL_COLOR_MATERIAL)  # Włącz kolorowanie dla dodatków
            glColor3f(*color)  # Ustaw kolor dodatku

            glPushMatrix()
            glBegin(GL_TRIANGLES)
            for face in addon['faces']:
                if len(face) < 3:
                    continue
                try:
                    for i in range(1, len(face) - 1):
                        v1 = vertices[face[0]]
                        v2 = vertices[face[i]]
                        v3 = vertices[face[i + 1]]
                        normal = np.cross(v2 - v1, v3 - v1)
                        normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else normal
                        glNormal3fv(normal)
                        glVertex3fv(v1)
                        glVertex3fv(v2)
                        glVertex3fv(v3)
                except IndexError as e:
                    print(f"Błąd indeksu w twarzy dodatku {addon['name']}: {e}")
            glEnd()
            glPopMatrix()
            glPopAttrib()  # Przywróć poprzedni stan OpenGL

    def set_addon_color(self, addon_name, color):
        """Ustaw kolor dla danego dodatku."""
        for addon in self.addons:
            if addon.get('name') == addon_name:  # Sprawdzenie klucza 'name'
                addon['color'] = tuple([c / 255.0 for c in color])  # Konwersja 0-255 do 0.0-1.0
                print(f"Kolor dla dodatku '{addon_name}' został ustawiony na {addon['color']}.")
                return  # Zatrzymaj, bo znaleziono dodatek
        print(f"Nie znaleziono dodatku o nazwie '{addon_name}' w liście dodatków.")

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.pan_x, self.pan_y, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        if self.scene:
            self.draw_model()

        if self.rails_vertices is not None and self.rails_faces is not None:
            self.draw_rails()

        self.draw_addons() #

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
        """
        Resetowanie widoku kamery po podwójnym kliknięciu.
        """
        previous_pan_y = self.pan_y  # Zapisujemy bieżącą pozycję Y, aby jej nie zmieniać
        self.set_camera_based_on_model_size()  # Ustaw ponownie widok kamery
        self.pan_y = previous_pan_y  # Przywróć pan_y, aby nie zmieniać pozycji bramy
        self.rotation_x = 0  # Reset obrotu X
        self.rotation_y = 0  # Reset obrotu Y
        self.update()

    def set_camera_based_on_model_size(self):
        """
        Oblicza wymiary obiektu i dostosowuje zoom oraz pozycję Y, aby obiekt mieścił się w widoku.
        """
        min_coords = np.min(self.vertices, axis=0)  # Najmniejsze współrzędne (x, y, z)
        max_coords = np.max(self.vertices, axis=0)  # Największe współrzędne (x, y, z)
        dimensions = max_coords - min_coords  # Rozmiar modelu (szerokość, wysokość, głębokość)
        diagonal = np.linalg.norm(dimensions)  # Długość przekątnej bryły (wymiary 3D)
        print(f"Rozmiary modelu: {dimensions}, Przekątna: {diagonal}")

        # Obliczamy dolną krawędź Y (dla OpenGL to "góra-dół")
        min_y = min_coords[1]  # Dolna krawędź bramy
        height = dimensions[1]  # Wysokość bramy
        center_y = (min_y + max_coords[1]) / 2  # Środek osi Y (do debugowania, ale już niepotrzebny)

        # Ustawienie pozycji zoomu
        self.zoom = -(diagonal * 1)  # Pomnóż przez współczynnik, aby było trochę miejsca wokół obiektu

        # Przesunięcie bramy tak, aby dolna krawędź bramy była na Y = 0
        # Opcja 1: Dynamiczne przesunięcie (oparte na wysokości bramy)
        self.pan_y = -min_y - 1 * height  # 10% wysokości bramy dodatkowo w dół

        # Opcja 2: Stałe przesunięcie (zawsze ta sama wartość)
        # self.pan_y = -min_y - 0.5  # Przesunięcie o stałą wartość 0.5 w dół

        self.pan_x = 0.0  # Ustaw pozycję X na środek ekranu

        print(f"Pan Y ustawione na {self.pan_y} dla minimalnego Y: {min_y}")

