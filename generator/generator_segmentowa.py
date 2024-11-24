import bpy
import os
import math
import json
import mathutils

# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["brama-segmentowa", "szyny-na-brame.001", "brama-segmentowa-z-szynami"]

for object_name in object_names:
    # Sprawdzenie, czy obiekt istnieje
    obj = bpy.data.objects.get(object_name)
    if obj:
        # Ustawienie obiektu jako aktywnego i zaznaczenie
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Usunięcie obiektu
        bpy.ops.object.delete()
        print(f"Obiekt '{object_name}' został usunięty.")
    else:
        print(f"Obiekt '{object_name}' nie istnieje.")

def scale_stack_and_align_rails(width, height, przetloczenie = "Bez przetłoczenia"):
    # Nazwy obiektów
    segment_name = "Cube.002"
    rail_name = "szyny-na-brame"
    # Lista dostępnych segmentów
    available_segments = {"Bez przetłoczenia": "Cube", "Niskie": "Cube.001","Średnie":  "Cube.002"}

    # Wyświetlenie dostępnych segmentów
    print("Dostępne segmenty:")
    for i, segment_name in enumerate(available_segments):
        print(f"{i + 1}. {segment_name}")
    # Pobranie wyboru użytkownika
    try:
        # segment_choice = przetloczenie #tu było pobieranie segmentu 1, 2, 3

        segment_name = available_segments[przetloczenie]
    except ValueError:
        print("Podano nieprawidłowy numer. Spróbuj ponownie.")
        return

    # Pobierz segment
    segment = bpy.data.objects.get(segment_name)
    if not segment:
        print(f"Obiekt o nazwie '{segment_name}' nie został znaleziony.")
        return

    # Pobierz obiekt szyn
    rail = bpy.data.objects.get(rail_name)
    if not rail:
        print(f"Obiekt o nazwie '{rail_name}' nie został znaleziony.")
        return

    try:
        # Pobranie danych od użytkownika
        x_length_cm = width
        x_length_m = x_length_cm / 1000  # Konwersja cm na metry
        segment_count = height//500

        # Aktualne wymiary segmentu
        current_length_x = segment.dimensions[0]
        current_height_z = segment.dimensions[2]

        # Oblicz współczynnik skalowania w osi X
        scale_factor_x = x_length_m / current_length_x

        # Lista kopii segmentów do połączenia
        segment_copies = []

        # Tworzenie i rozmieszczanie kopii segmentów
        for i in range(segment_count):
            new_segment = segment.copy()  # Tworzenie kopii segmentu
            new_segment.data = segment.data.copy()  # Niezależna kopia danych siatki
            new_segment.scale[0] = scale_factor_x  # Skalowanie w osi X
            new_segment.location.z = i * current_height_z  # Ustawienie w osi Z
            bpy.context.collection.objects.link(new_segment)  # Dodanie kopii do sceny
            segment_copies.append(new_segment)

        # Połączenie segmentów w jeden obiekt
        bpy.context.view_layer.objects.active = segment_copies[0]
        for segment in segment_copies:
            segment.select_set(True)  # Zaznacz wszystkie kopie
        bpy.ops.object.join()
        joined_gate = bpy.context.view_layer.objects.active
        joined_gate.name = "brama-segmentowa"  # Zmień nazwę obiektu

        # Ustawienie origin bramy na środek jej geometrii
        bpy.context.view_layer.objects.active = joined_gate
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        print(f"Stworzono i połączono {segment_count} segmentów w obiekt 'brama-segmentowa'.")

        # Tworzenie kopii szyn i dopasowanie do bramy
        rail_copy = rail.copy()
        bpy.context.collection.objects.link(rail_copy)  # Dodanie kopii szyn do sceny

        # Skalowanie szyn - ustawienie Dimensions w osiach X i Z takie same jak brama, Y pozostaje oryginalne
        original_y = rail.dimensions[1]  # Zachowujemy oryginalny wymiar Y (grubość)
        scale_x = joined_gate.dimensions[0] / rail.dimensions[0]  # Skalowanie szerokości (X)
        scale_z = joined_gate.dimensions[2] / rail.dimensions[2]  # Skalowanie wysokości (Z)

        rail_copy.scale[0] = scale_x  # Dopasowanie szerokości
        rail_copy.scale[2] = scale_z  # Dopasowanie wysokości
        rail_copy.scale[1] = rail.scale[1]  # Zachowanie oryginalnej skali w osi Y

        # Ustawienie Location szyn na to samo co brama
        rail_copy.location = joined_gate.location

        # Ustawienie Location szyn na to samo co brama
        rail_copy.location = joined_gate.location
        # Ustawienie pozycji obiektów w osi X i Y na (0, 0)
        rail_copy.location.x = 0
        rail_copy.location.y = 0

        joined_gate.location.x = 0
        joined_gate.location.y = 0

        bpy.context.view_layer.objects.active = rail_copy
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        # Oblicz dolną krawędź każdego obiektu
        rail_bottom_z = rail_copy.location.z - (rail_copy.dimensions[2] / 2)
        gate_bottom_z = joined_gate.location.z - (joined_gate.dimensions[2] / 2)

        # Przesuń obiekty w osi Z tak, aby dolna krawędź była dokładnie na Z = 0
        rail_copy.location.z -= rail_bottom_z  # Przesuwamy dolną krawędź szyny na Z = 0
        joined_gate.location.z -= gate_bottom_z  # Przesuwamy dolną krawędź bramy na Z = 0
        # Połączenie 'brama-segmentowa' i 'rail_copy'
        bpy.context.view_layer.objects.active = joined_gate
        joined_gate.select_set(True)
        rail_copy.select_set(True)
        bpy.ops.object.join()

        final_gate = bpy.context.view_layer.objects.active
        final_gate.name = "brama-segmentowa-z-szynami"

        print(f"Dodano i dopasowano szyny do obiektu 'brama-segmentowa'.")

    except ValueError:
        print("Podano nieprawidłowe dane. Spróbuj ponownie.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

def read_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        existing_data = json.load(file)
        # Zachowaj 'Typ bramy' i 'Wymiary'

        if "Wymiary" in existing_data:
            wymiary = existing_data["Wymiary"]
        if "Rodzaj przetłoczenia" in existing_data:
            przetloczenie = existing_data["Rodzaj przetłoczenia"]
        else:
            przetloczenie = "Bez przetłoczenia"

    return [wymiary, przetloczenie]
def custom_export_to_obj(object_name="brama-segmentowa-z-szynami", output_path="brama-segmentowa.obj"):
    """
    Eksportuje obiekt do pliku .obj z rotacją 90 stopni w osi X,
    ukrywając inne obiekty w scenie.
    """
    # Sprawdź, czy obiekt istnieje
    obj = bpy.data.objects.get(object_name)
    if not obj:
        print(f"Obiekt '{object_name}' nie został znaleziony w scenie.")
        return

    # Ścieżka wyjściowa
    output_path = "../generator/model.obj"

    # Rotacja o 90 stopni w osi X
    rotation_matrix = mathutils.Matrix.Rotation(-math.radians(90), 4, 'X')
    transformed_matrix = rotation_matrix @ obj.matrix_world

    # Otwórz plik wyjściowy
    with open(output_path, 'w') as obj_file:
        # Napisz nagłówek pliku .obj
        obj_file.write(f"# Exported from Blender with rotation -90 degrees in X-axis\n")
        obj_file.write(f"# Object: {object_name}\n\n")

        # Przechodzimy do siatki obiektu
        mesh = obj.data

        # Zapisz wierzchołki (vertices)
        for vertex in mesh.vertices:
            # Przelicz współrzędne wierzchołków na przestrzeń globalną z rotacją
            world_coord = transformed_matrix @ vertex.co
            obj_file.write(f"v {world_coord.x} {world_coord.y} {world_coord.z}\n")

        # Zapisz normalne (normals)
        if mesh.polygons:
            for poly in mesh.polygons:
                rotated_normal = rotation_matrix @ poly.normal
                obj_file.write(f"vn {rotated_normal.x} {rotated_normal.y} {rotated_normal.z}\n")

        # Zapisz współrzędne UV (jeśli istnieją)
        if mesh.uv_layers:
            uv_layer = mesh.uv_layers.active.data
            for loop in uv_layer:
                obj_file.write(f"vt {loop.uv.x} {loop.uv.y}\n")

        # Zapisz powierzchnie (faces)
        for poly in mesh.polygons:
            face_vertices = [str(vert + 1) for vert in poly.vertices]  # +1, bo .obj zaczyna od 1
            obj_file.write(f"f {' '.join(face_vertices)}\n")

    print(f"Obiekt '{object_name}' został wyeksportowany do pliku: {output_path}")

# Uruchom funkcję
dimensions, przetloczenie = read_json("../resources/selected_options.json")
width = dimensions.get("Szerokość")
height = dimensions.get("Wysokość")

scale_stack_and_align_rails(width, height, przetloczenie)
# add_cameras_and_render_with_light()
custom_export_to_obj()







