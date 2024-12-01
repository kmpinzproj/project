import bpy
import os
import math
import json
import mathutils

# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["brama-segmentowa", "szyny-na-brame.001", "brama-segmentowa-z-szynami"]

for object_name in object_names:
    obj = bpy.data.objects.get(object_name)
    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.delete()
    else:
        test = 0
#metoda na kasetony
def create_gate():
    # Nazwy obiektów
    segment_name = "Cube.003"
    # Pobierz segment
    segment = bpy.data.objects.get(segment_name)
    if not segment:
        print(f"Obiekt o nazwie '{segment_name}' nie został znaleziony.")
        return

    try:
        # Pobranie danych od użytkownika

        x_length_cm = float(input("Podaj długość całkowitą w osi X (w cm): "))
        x_length_m = x_length_cm / 100  # Konwersja cm na metry
        z_height_cm = float(input("Podaj wysokość całkowitą w osi Z (w cm): "))
        z_height_m = z_height_cm / 100  # Konwersja cm na metry
        segment_width_m = 0.4  # Stała szerokość segmentu (40 cm w metrach)
        segment_height_m = 0.4  # Wysokość jednego segmentu w metrach

        # Oblicz liczbę segmentów w osi X i Z
        segment_count_x = max(1, int(x_length_m // segment_width_m))  # Co najmniej 1 segment w osi X
        print(segment_count_x)
        segment_count_z = max(1, int(z_height_m // segment_height_m))  # Co najmniej 1 segment w osi Z
        print(segment_count_z)

        # Oblicz nową szerokość segmentu w osi X
        segment_width_per_unit = round(x_length_m / segment_count_x, 3)
        print(segment_width_per_unit)
        segment_height_per_unit = round(z_height_m / segment_count_z, 3)
        print(segment_height_per_unit)

        # Lista kopii segmentów do połączenia
        segment_copies = []

        # Tworzenie i rozmieszczanie kopii segmentów w siatce (X, Z)
        for row in range(segment_count_z):
            for col in range(segment_count_x):
                new_segment = segment.copy()  # Tworzenie kopii segmentu
                new_segment.data = segment.data.copy()  # Niezależna kopia danych siatki
                new_segment.scale[0] = segment_width_per_unit / segment.dimensions[0]  # Skalowanie w osi X
                new_segment.scale[2] = segment_height_per_unit / segment.dimensions[2]  # Skalowanie w osi Z
                new_segment.location.x = col * segment_width_per_unit  # Ustawienie w osi X
                new_segment.location.z = row * segment_height_per_unit  # Ustawienie w osi Z
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
        joined_gate.location = (0, 0, joined_gate.dimensions[2]/2)

        print(f"Stworzono bramę o wymiarach {segment_count_x} segmentów w poziomie i {segment_count_z} segmentów w pionie.")
        print(f"Wymiary pojedynczego segmentu: szerokość = {segment_width_per_unit}m, wysokość = {segment_height_per_unit}m.")
        return joined_gate

    except ValueError:
        print("Podano nieprawidłowe dane. Spróbuj ponownie.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

def scale_stack_and_align_rails(width, height, przetloczenie="Bez przetłoczenia"):
    segment_name = "Cube.002"
    rail_name = "szyny-na-brame"
    available_segments = {"Bez przetłoczenia": "Cube", "Niskie": "Cube.001", "Średnie": "Cube.002"}

    try:
        segment_name = available_segments[przetloczenie]
    except ValueError:
        print("Podano nieprawidłowy numer. Spróbuj ponownie.")
        return

    segment = bpy.data.objects.get(segment_name)
    if not segment:
        print(f"Obiekt o nazwie '{segment_name}' nie został znaleziony.")
        return

    rail = bpy.data.objects.get(rail_name)
    if not rail:
        print(f"Obiekt o nazwie '{rail_name}' nie został znaleziony.")
        return

    try:
        #dałbym już tu if na kasetony
        x_length_m = width / 1000
        segment_count = height // 500

        current_length_x = segment.dimensions[0]
        current_height_z = segment.dimensions[2]

        scale_factor_x = x_length_m / current_length_x

        segment_copies = []

        for i in range(segment_count):
            new_segment = segment.copy()
            new_segment.data = segment.data.copy()
            new_segment.scale[0] = scale_factor_x
            new_segment.location.z = i * current_height_z
            bpy.context.collection.objects.link(new_segment)

            bpy.context.view_layer.objects.active = new_segment

            segment_copies.append(new_segment)

        bpy.context.view_layer.objects.active = segment_copies[0]
        for segment in segment_copies:
            segment.select_set(True)
        bpy.ops.object.join()
        joined_gate = bpy.context.view_layer.objects.active
        joined_gate.name = "brama-segmentowa"

        bpy.context.view_layer.objects.active = joined_gate
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        rail_copy = rail.copy()
        bpy.context.collection.objects.link(rail_copy)

        original_y = rail.dimensions[1]
        scale_x = joined_gate.dimensions[0] / rail.dimensions[0]
        scale_z = joined_gate.dimensions[2] / rail.dimensions[2]

        rail_copy.scale[0] = scale_x
        rail_copy.scale[2] = scale_z
        rail_copy.scale[1] = rail.scale[1]

        rail_copy.location = joined_gate.location
        rail_copy.location.x = 0
        rail_copy.location.y = 0

        joined_gate.location.x = 0
        joined_gate.location.y = 0

        bpy.context.view_layer.objects.active = rail_copy
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        rail_bottom_z = rail_copy.location.z - (rail_copy.dimensions[2] / 2)
        gate_bottom_z = joined_gate.location.z - (joined_gate.dimensions[2] / 2)

        rail_copy.location.z -= rail_bottom_z
        joined_gate.location.z -= gate_bottom_z

        bpy.context.view_layer.objects.active = joined_gate
        joined_gate.select_set(True)
        rail_copy.select_set(True)
        bpy.ops.object.join()

        final_gate = bpy.context.view_layer.objects.active
        final_gate.name = "brama-segmentowa-z-szynami"

    except ValueError:
        print("Podano nieprawidłowe dane. Spróbuj ponownie.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

# Eksport z teksturą
def custom_export_to_obj_with_texture(texture_path, object_name="brama-segmentowa-z-szynami",
                                      output_obj_path="model.obj", output_mtl_path="model.mtl"):
    obj = bpy.data.objects.get(object_name)
    if not obj:
        print(f"Obiekt '{object_name}' nie został znaleziony w scenie.")
        return

    output_obj_path = "../generator/" + output_obj_path
    output_mtl_path = "../generator/" + output_mtl_path

    rotation_matrix = mathutils.Matrix.Rotation(-math.radians(90), 4, 'X')
    transformed_matrix = rotation_matrix @ obj.matrix_world

    with open(output_mtl_path, 'w') as mtl_file:
        mtl_file.write(f"# Material file for {object_name}\n")
        mtl_file.write(f"newmtl BramaMaterial\n")
        mtl_file.write(f"Ka 0.2 0.2 0.2\n")
        mtl_file.write(f"Kd 1.0 1.0 1.0\n")
        mtl_file.write(f"Ks 0.5 0.5 0.5\n")
        mtl_file.write(f"Ns 50.0\n")
        mtl_file.write(f"d 1.0\n")
        mtl_file.write(f"illum 2\n")
        mtl_file.write(f"map_Kd {texture_path}\n")

    with open(output_obj_path, 'w') as obj_file:
        obj_file.write(f"mtllib {output_mtl_path}\n")
        obj_file.write(f"# Exported from Blender with rotation -90 degrees in X-axis\n")
        obj_file.write(f"# Object: {object_name}\n\n")

        mesh = obj.data
        for vertex in mesh.vertices:
            world_coord = transformed_matrix @ vertex.co
            obj_file.write(f"v {world_coord.x} {world_coord.y} {world_coord.z}\n")

        if mesh.polygons:
            for poly in mesh.polygons:
                rotated_normal = rotation_matrix @ poly.normal
                obj_file.write(f"vn {rotated_normal.x} {rotated_normal.y} {rotated_normal.z}\n")

        if mesh.uv_layers:
            uv_layer = mesh.uv_layers.active.data
            for loop in uv_layer:
                obj_file.write(f"vt {loop.uv.x} {loop.uv.y}\n")

        obj_file.write(f"usemtl BramaMaterial\n")
        for poly in mesh.polygons:
            face_vertices = []
            for loop_index in poly.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                uv_index = loop_index + 1
                face_vertices.append(f"{vertex_index + 1}/{uv_index}/{vertex_index + 1}")
            obj_file.write(f"f {' '.join(face_vertices)}\n")

    print(f"Obiekt '{object_name}' został wyeksportowany do:\n - OBJ: {output_obj_path}\n - MTL: {output_mtl_path}")

# Przykład użycia
texture_path = "../textures/sapeli.png"  # Ścieżka do pliku z teksturą
custom_export_to_obj_with_texture(texture_path=texture_path)

# # Przykład użycia
# custom_export_to_obj_with_mtl(color=(0.3, 0.5, 0.8))  # Eksport z kolorem niebieskim

def read_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        existing_data = json.load(file)
        # Zachowaj 'Typ bramy' i 'Wymiary'
        print(existing_data)
        if "Wymiary" in existing_data:
            wymiary = existing_data["Wymiary"]
        if "Rodzaj przetłoczenia" in existing_data and existing_data["Rodzaj przetłoczenia"] is not None:
            przetloczenie = existing_data["Rodzaj przetłoczenia"]
        else:
            przetloczenie = "Bez przetłoczenia"
        if "Kolor standardowy" in existing_data:
            name = existing_data["Kolor standardowy"]
            print(existing_data)
            base_path = "../jpg/Kolor_Standardowy/"
            sanitized_name = name.strip()
            kolor = f"{base_path}{sanitized_name}.png"
        elif "Kolor RAL" in existing_data:
            name = existing_data["Kolor RAL"]
            base_path = "../jpg/Kolor_RAL/"
            sanitized_name = name.strip()
            kolor = f"{base_path}{sanitized_name}.png"
        else:
            kolor = f"../jpg/Kolor_RAL/7040.png"
        return [wymiary, przetloczenie, kolor]

# Uruchom funkcję
dimensions, przetloczenie, kolor = read_json("../resources/selected_options.json")
width = dimensions.get("Szerokość")
height = dimensions.get("Wysokość")
print(przetloczenie)
scale_stack_and_align_rails(width, height, przetloczenie)
# add_cameras_and_render_with_light()
custom_export_to_obj_with_texture(kolor)
