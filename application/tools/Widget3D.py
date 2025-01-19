from PySide6.QtGui import Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pywavefront
import numpy as np
from PIL import Image
import os

from application.tools.path import get_resource_path

addon_colors = {
            "wentylacja": (1.0, 0.0, 0.0),  # Czerwony
            "drzwi_w_bramie": (51, 56, 52),  # Zielony
            "klamka_do_drzwi": (0, 0, 0),  # Niebieski
            "szyba_okna_1": (75, 127, 156),  # Szary
            "szyba_okna_2": (75, 127, 156),  # Szary
            "szyba_okna_3": (75, 127, 156),  # Szary
            "ramka_okna_1": (51, 56, 52),  # Szary
            "ramka_okna_2": (51, 56, 52),  # Szary
            "ramka_okna_3": (51, 56, 52),  # Szary
            "klamka-1.001": (0, 0, 0),  # Szary
            "klamka-2.001": (122, 101, 64),  # Szary
            "klamka-3.001": (134, 149, 156),  # Szary
            "klamka-4.001": (77, 59, 57),  # Szary
            "szyny": (0,0,0)
        }

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
    """
    Klasa odpowiedzialna za renderowanie obiektu 3D w widoku aplikacji.

    Umożliwia wyświetlanie bramy, szyn oraz dodatków z obsługą tekstur,
    oświetlenia, dynamicznej interakcji z użytkownikiem (obracanie, przesuwanie,
    zoom) oraz zarządzania plikami OBJ i MTL.
    """
    def __init__(self, obj_file, rails_obj_file, parent=None):
        """
        Inicjalizuje widżet OpenGL.

        Args:
            obj_file (str): Ścieżka do pliku OBJ reprezentującego model bramy.
            rails_obj_file (str): Ścieżka do pliku OBJ reprezentującego model szyn.
            parent (QWidget, optional): Rodzic widżetu OpenGL. Domyślnie None.
        """
        super().__init__(parent)
        self.obj_file = obj_file
        self.rails_obj_file = rails_obj_file
        self.addons_file = get_resource_path("application/generator/dodatki/combined_addons.obj")  # Ścieżka do pliku dodatków

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
        self.addon_colors = addon_colors  # Słownik z kolorami dla dodatków (nazwa dodatku -> (R, G, B))

    def initializeGL(self):
        """
        Inicjalizuje ustawienia OpenGL, takie jak oświetlenie, materiały i głębia,
        oraz ładuje modele bramy, szyn i dodatków.
        """
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_MULTISAMPLE)
        glClearColor(0.1, 0.2, 0.3, 1.0)

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glEnable(GL_LIGHT0)
        light0_position = [10.0, 10.0, 10.0, 1.0]  # Główne światło z przodu, prawego górnego rogu
        glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])  # Jasne światło rozproszone
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.5, 1.5, 1.5, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.05, 0.05, 0.05, 1.0])  # Bardzo minimalne światło otoczenia

        glEnable(GL_LIGHT1)
        light1_position = [-10.0, 10.0, 10.0, 1.0]  # Światło wspierające z lewego górnego rogu
        glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.4, 0.4, 0.4, 1.0])  # Delikatniejsze światło
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.02, 0.02, 0.02, 1.0])

        self.load_model(self.obj_file)
        self.load_rails(self.rails_obj_file)  # Szyny
        self.load_addons(self.addons_file)  # Wczytaj dodatki


    def load_texture(self, texture_file, rotation_angle=90):
        """
        Ładuje teksturę z pliku i aplikuje obrót.

        Args:
            texture_file (str): Ścieżka do pliku tekstury.
            rotation_angle (int, optional): Kąt obrotu tekstury w stopniach. Domyślnie 90.

        Returns:
            int: ID tekstury OpenGL.
        """
        if not os.path.exists(texture_file):
            print(f"UWAGA: Plik tekstury {texture_file} nie istnieje.")
            return None

        image = Image.open(texture_file)
        self.read_color(image)

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
        """
        Ładuje model bramy z pliku OBJ i oblicza normalne oraz tekstury.

        Args:
            obj_file (str): Ścieżka do pliku OBJ reprezentującego model bramy.
        """
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

        if hasattr(self.scene.parser, 'tex_coords'):
            self.uv_coordinates = np.array(self.scene.parser.tex_coords, dtype=np.float32)

        self.normals = compute_normals(self.vertices, self.faces)
        adjusted_center = self.compute_adjusted_center(self.vertices)
        self.vertices -= adjusted_center

        # Obliczenie przekątnej i ustawienie zoomu
        self.set_camera_based_on_model_size()
        self.update()

    @staticmethod
    def parse_mtl_file(mtl_path):
        """
        Parsuje plik MTL w celu przypisania tekstur do materiałów.

        Args:
            mtl_path (str): Ścieżka do pliku MTL.

        Returns:
            dict: Słownik z mapowaniem nazw materiałów na ścieżki tekstur.
        """
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
        """
        Renderuje model bramy, w tym tekstury i oświetlenie.
        """
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
        """
        Oblicza środek modelu, uwzględniając tylko współrzędne Y.

        Args:
            vertices (np.ndarray): Współrzędne wierzchołków modelu.

        Returns:
            np.ndarray: Środek modelu z uwzględnieniem współrzędnych Y.
        """
        min_y = np.min(vertices[:, 1])
        max_y = np.max(vertices[:, 1])
        center_y = (min_y + max_y) / 2
        centroid = np.mean(vertices, axis=0)
        adjusted_center = np.array([centroid[0], center_y, centroid[2]])
        return adjusted_center

    def resizeGL(self, width, height):
        """
        Oblicza środek modelu, uwzględniając tylko współrzędne Y.

        Args:
            vertices (np.ndarray): Współrzędne wierzchołków modelu.

        Returns:
            np.ndarray: Środek modelu z uwzględnieniem współrzędnych Y.
        """
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def load_obj_simple(filepath):
        """
        Ładuje wierzchołki i twarze z pliku OBJ.

        Args:
            filepath (str): Ścieżka do pliku OBJ.

        Returns:
            tuple: Wierzchołki (np.ndarray) i twarze (np.ndarray) modelu.
        """
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
        """
        Ładuje model szyn z pliku OBJ.

        Args:
            obj_file (str): Ścieżka do pliku OBJ reprezentującego szyny.
        """
        vertices, faces = self.load_obj_simple(obj_file)
        self.vertices = np.array(self.scene.vertices)

        if vertices is not None and faces is not None:
            self.rails_vertices = vertices
            self.rails_faces = faces
        else:
            print("Error loading rails data.")

    def draw_rails(self):
        """
        Renderuje model szyn w widoku OpenGL.
        """
        glPushAttrib(GL_ALL_ATTRIB_BITS)  # Zapisz aktualny stan OpenGL
        if not hasattr(self, 'rails_vertices') or not hasattr(self, 'rails_faces'):
            print("No rails data to render.")
            glPopAttrib()
            return

        color = tuple(value / 255 for value in self.addon_colors["szyny"])  # Domyślny kolor szary (RGB w skali 0-1)

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

                glColor3f(*color)  # Kolor dla każdego wierzchołka (aby mieć pewność)

                glVertex3fv(v1)
                glVertex3fv(v2)
                glVertex3fv(v3)
        glEnd()
        glPopMatrix()

        glPopAttrib()  # Przywróć poprzedni stan OpenGL

    def clear_addons(self):
        """
        Czyści wszystkie dodatki załadowane do widoku i odświeża scenę.
        """
        self.addons.clear()  # Usunięcie wszystkich danych o dodatkach
        self.update()  # Odśwież widok

    def load_addons(self, obj_file):
        """
        Ładuje dodatki z pliku OBJ.

        Args:
            obj_file (str): Ścieżka do pliku OBJ z dodatkami.
        """
        self.clear_addons()  # Wyczyść poprzednie dodatki

        if not os.path.exists(obj_file):
            print(f"Plik {obj_file} nie istnieje.")
            return

        global_vertex_offset = 0  # Przesunięcie indeksów wierzchołków
        vertices_global = []  # Globalna lista wszystkich wierzchołków
        current_object = None  # Obecnie przetwarzany obiekt

        with open(obj_file, 'r') as file:
            for line in file:
                if line.startswith('o '):  # Nowy obiekt w pliku
                    if current_object:  # Dodaj poprzedni obiekt, jeśli istnieje
                        self.addons.append(current_object)

                        # Ustaw kolor dla ostatnio dodanego obiektu
                        addon_name = current_object['name']
                        if addon_name in self.addon_colors:
                            self.addons[-1]['color'] = tuple(c / 255.0 for c in self.addon_colors[addon_name])
                        else:
                            self.addons[-1]['color'] = (0.5, 0.5, 0.5)  # Domyślny szary kolor

                        global_vertex_offset += len(current_object['vertices'])
                        vertices_global.extend(current_object['vertices'])

                    # Rozpocznij nowy obiekt
                    current_object = {'name': line.split()[1], 'vertices': [], 'faces': [], 'color': None}

                elif line.startswith('v '):  # Wczytaj wierzchołki
                    if current_object:
                        vertex = [float(x) for x in line.split()[1:]]
                        current_object['vertices'].append(vertex)

                elif line.startswith('f '):  # Wczytaj twarze
                    if current_object:
                        face = [int(idx.split('/')[0]) - 1 for idx in line.split()[1:]]
                        shifted_face = [idx - global_vertex_offset for idx in face]
                        current_object['faces'].append(shifted_face)

        # Obsłuż ostatni obiekt po zakończeniu pętli
        if current_object:
            self.addons.append(current_object)

            # Ustaw kolor dla ostatnio dodanego obiektu
            addon_name = current_object['name']
            if addon_name in self.addon_colors:
                self.addons[-1]['color'] = tuple(c / 255.0 for c in self.addon_colors[addon_name])
            else:
                self.addons[-1]['color'] = (0.5, 0.5, 0.5)  # Domyślny szary kolor

        self.update()  # Odśwież widok po wprowadzeniu zmian

    def draw_addons(self):
        """
        Renderuje wszystkie załadowane dodatki na scenie.
        """
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
                    # Zakładamy, że normalne zostały już obliczone w pliku .obj
                    # Jeśli normalne są zapisane w pliku .obj, można je wykorzystać tutaj
                    for i in range(1, len(face) - 1):
                        v1 = vertices[face[0]]
                        v2 = vertices[face[i]]
                        v3 = vertices[face[i + 1]]

                        # Nie obliczamy normalnych w czasie rzeczywistym
                        glVertex3fv(v1)
                        glVertex3fv(v2)
                        glVertex3fv(v3)
                except IndexError as e:
                    print(f"Błąd indeksu w twarzy dodatku {addon['name']}: {e}")
            glEnd()
            glPopMatrix()
            glPopAttrib()  # Przywróć poprzedni stan OpenGL

    def paintGL(self):
        """
        Renderuje scenę OpenGL, w tym model bramy, szyny oraz dodatki.
        """
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

    def read_color(self, image):
        """
        Pobiera kolor z obrazu i modyfikuje kolory dodatków.

        Args:
            image (PIL.Image): Obraz do analizy kolorów.
        """
        addons = ["drzwi_w_bramie", "ramka_okna_1","ramka_okna_2", "ramka_okna_3", "szyny"]
        x, y = 50, 50  # Przykładowe współrzędne

        if image.mode != "RGB":
            image = image.convert("RGB")
        # Pobierz kolor z obrazu
        rgb_color = image.getpixel((x, y))
        factor = 0.5

        # Przyciemnianie każdego kanału RGB
        r = int(rgb_color[0] * factor)
        g = int(rgb_color[1] * factor)
        b = int(rgb_color[2] * factor)

        # Przyciemniony kolor
        darkened_color = (r, g, b)
        for addon in addons:
            self.addon_colors[addon] = darkened_color

    def mousePressEvent(self, event):
        """
        Obsługuje kliknięcia myszą, ustawiając punkt początkowy dla przesuwania i obracania.

        Args:
            event (QMouseEvent): Zdarzenie kliknięcia myszą.
        """
        self.last_mouse_position = event.position()

    def mouseMoveEvent(self, event):
        """
        Obsługuje ruch myszą, umożliwiając przesuwanie i obracanie widoku.

        Args:
            event (QMouseEvent): Zdarzenie ruchu myszą.
        """
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
        """
        Resetuje pozycję myszy po zakończeniu interakcji.

        Args:
            event (QMouseEvent): Zdarzenie zwolnienia przycisku myszy.
        """
        self.last_mouse_position = None

    def wheelEvent(self, event):
        """
        Obsługuje scroll myszki, umożliwiając przybliżanie i oddalanie widoku.

        Args:
            event (QWheelEvent): Zdarzenie przewijania.
        """
        delta = event.angleDelta().y() / 120
        self.zoom += delta * 0.2
        self.update()

    def mouseDoubleClickEvent(self, event):
        """
        Resetuje widok kamery po podwójnym kliknięciu.

        Args:
            event (QMouseEvent): Zdarzenie podwójnego kliknięcia.
        """
        previous_pan_y = self.pan_y  # Zapisujemy bieżącą pozycję Y, aby jej nie zmieniać
        self.set_camera_based_on_model_size()  # Ustaw ponownie widok kamery
        self.pan_y = previous_pan_y  # Przywróć pan_y, aby nie zmieniać pozycji bramy
        self.rotation_x = 0  # Reset obrotu X
        self.rotation_y = 0  # Reset obrotu Y
        self.update()

    def set_camera_based_on_model_size(self):
        """
        Dostosowuje zoom i pozycję kamery na podstawie rozmiarów modelu.
        """
        min_coords = np.min(self.vertices, axis=0)  # Najmniejsze współrzędne (x, y, z)
        max_coords = np.max(self.vertices, axis=0)  # Największe współrzędne (x, y, z)
        dimensions = max_coords - min_coords  # Rozmiar modelu (szerokość, wysokość, głębokość)
        diagonal = np.linalg.norm(dimensions)  # Długość przekątnej bryły (wymiary 3D)

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


