import bpy
import math
import json
import mathutils
import os

# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["brama-segmentowa", "szyny-na-brame.001", "brama-segmentowa-z-szynami", "szyny", "brama-koniec"]

for object_name in object_names:
    obj = bpy.data.objects.get(object_name)
    if obj:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.delete()
    else:
        test = 0


def scale_stack_and_align_rails(width, height, przetloczenie):
    segment_name = "Cube.002"
    available_segments = {"Bez przetłoczenia": "Cube", "Niskie": "Cube.001", "Średnie": "Cube.002", "Kasetony": "Cube.003", "START": "Cube.004"}

    try:
        segment_name = available_segments[przetloczenie]
    except ValueError:
        print("Podano nieprawidłowy numer. Spróbuj ponownie.")
        return

    segment = bpy.data.objects.get(segment_name)
    if not segment:
        print(f"Obiekt o nazwie '{segment_name}' nie został znaleziony.")
        return

    try:
        x_length_m = width / 1000
        z_height_m = height / 1000
        segment_width_m = 0.4  # Stała szerokość segmentu (40 cm w metrach)
        segment_height_m = 0.4  # Wysokość jednego segmentu w metrach

        segment_count_x = max(1, int(x_length_m // segment_width_m))
        segment_count_z = max(1, int(z_height_m // segment_height_m))

        segment_width_per_unit = round(x_length_m / segment_count_x, 3)
        segment_height_per_unit = round(z_height_m / segment_count_z, 3)

        segment_copies = []

        for row in range(segment_count_z):
            for col in range(segment_count_x):
                new_segment = segment.copy()
                new_segment.data = segment.data.copy()
                new_segment.scale[0] = segment_width_per_unit / segment.dimensions[0]
                new_segment.scale[2] = segment_height_per_unit / segment.dimensions[2]
                new_segment.location.x = col * segment_width_per_unit
                new_segment.location.z = row * segment_height_per_unit
                bpy.context.collection.objects.link(new_segment)
                segment_copies.append(new_segment)

        for segment in segment_copies:
            segment.select_set(True)
        bpy.context.view_layer.objects.active = segment_copies[0]
        bpy.ops.object.join()

        joined_gate = bpy.context.view_layer.objects.active
        joined_gate.name = "brama-koniec"
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        joined_gate.location = (0,0,joined_gate.dimensions[2]/2)

        add_and_align_rails(joined_gate)

        gate = bpy.data.objects.get("brama-koniec")
        bpy.context.view_layer.objects.active = gate
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if gate:
            gate_data = {
                "location": [gate.location.x, gate.location.y, gate.location.z],
                "dimensions": [gate.dimensions.x, gate.dimensions.y, gate.dimensions.z]
            }
            # Zapisz dane bramy do pliku JSON
            with open("../generator/dodatki/gate_data.json", "w") as json_file:
                json.dump(gate_data, json_file)
            print("Dane bramy zostały zapisane do pliku gate_data.json.")
        else:
            print("Nie znaleziono obiektu bramy.")

        return joined_gate
    except Exception as e:
        print(f"Wystąpił błąd podczas tworzenia bramy: {e}")
        return None

def add_and_align_rails(gate):
    rail_name = "szyny-na-brame"

    # Pobierz obiekt szyn
    rail = bpy.data.objects.get(rail_name)
    if not rail:
        print(f"Obiekt o nazwie '{rail_name}' nie został znaleziony.")
        return

    try:
        # Tworzenie kopii szyn i dopasowanie do bramy
        rail_copy = rail.copy()
        bpy.context.collection.objects.link(rail_copy)  # Dodanie kopii szyn do sceny

        # Skalowanie szyn - ustawienie Dimensions w osiach X i Z takie same jak brama, Y pozostaje oryginalne
        scale_x = (gate.dimensions[0] / rail.dimensions[0])  # Skalowanie szerokości (X)
        scale_z = gate.dimensions[2] / rail.dimensions[2]  # Skalowanie wysokości (Z)

        rail_copy.scale[0] = scale_x + 0.001 # Dopasowanie szerokości
        rail_copy.scale[2] = scale_z + 0.001 # Dopasowanie wysokości

        # Ustawienie Location szyn na to samo co brama
        rail_copy.location = gate.location

        bpy.context.view_layer.objects.active = rail_copy
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        # Oblicz dolną krawędź każdego obiektu
        rail_bottom_z = rail_copy.location.z - (rail_copy.dimensions[2] / 2)
        gate_bottom_z = gate.location.z - (gate.dimensions[2] / 2)

        # Przesuń obiekty w osi Z tak, aby dolna krawędź była dokładnie na Z = 0
        rail_copy.location.z -= rail_bottom_z
        gate.location.z -= gate_bottom_z

        final_gate = bpy.context.view_layer.objects.active
        final_gate.name = "szyny"

        gate = bpy.data.objects.get("szyny")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

# Eksport z teksturą
def custom_export_to_obj_with_texture(texture_path, object_name="brama-koniec",
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

def custom_export_to_obj_without_mtl(object_name="szyny", output_obj_path="szyny.obj"):
    obj = bpy.data.objects.get(object_name)
    if not obj:
        print(f"Obiekt '{object_name}' nie został znaleziony w scenie.")
        return

    output_obj_path = "../generator/" + output_obj_path

    # Obrót obiektu o -90 stopni w osi X
    rotation_matrix = mathutils.Matrix.Rotation(-math.radians(90), 4, 'X')
    transformed_matrix = rotation_matrix @ obj.matrix_world

    with open(output_obj_path, 'w') as obj_file:
        obj_file.write(f"# Exported from Blender with rotation -90 degrees in X-axis\n")
        obj_file.write(f"# Object: {object_name}\n\n")

        # Eksportuj wierzchołki
        mesh = obj.data
        for vertex in mesh.vertices:
            world_coord = transformed_matrix @ vertex.co
            obj_file.write(f"v {world_coord.x} {world_coord.y} {world_coord.z}\n")

        # Eksportuj normalne (opcjonalnie, jeśli istnieją wielokąty)
        if mesh.polygons:
            for poly in mesh.polygons:
                rotated_normal = rotation_matrix @ poly.normal
                obj_file.write(f"vn {rotated_normal.x} {rotated_normal.y} {rotated_normal.z}\n")

        # Eksportuj współrzędne UV (jeśli istnieją warstwy UV)
        if mesh.uv_layers:
            uv_layer = mesh.uv_layers.active.data
            for loop in uv_layer:
                obj_file.write(f"vt {loop.uv.x} {loop.uv.y}\n")

        # Eksportuj twarze
        for poly in mesh.polygons:
            face_vertices = []
            for loop_index in poly.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                if mesh.uv_layers:
                    uv_index = loop_index + 1
                    face_vertices.append(f"{vertex_index + 1}/{uv_index}/{vertex_index + 1}")
                else:
                    face_vertices.append(f"{vertex_index + 1}")
            obj_file.write(f"f {' '.join(face_vertices)}\n")

def read_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        existing_data = json.load(file)
        # Zachowaj 'Typ bramy' i 'Wymiary'
        if "Wymiary" in existing_data:
            wymiary = existing_data["Wymiary"]
        if "Rodzaj przetłoczenia" in existing_data and existing_data["Rodzaj przetłoczenia"] is not None:
            przetloczenie = existing_data["Rodzaj przetłoczenia"]
        else:
            przetloczenie = "START"
        if "Kolor standardowy" in existing_data and existing_data["Kolor standardowy"] is not None:
            name = existing_data["Kolor standardowy"]
            base_path = "../jpg/Kolor_Standardowy/"
            sanitized_name = name.strip()
            kolor = f"{base_path}{sanitized_name}.png"
        elif "Kolor RAL" in existing_data and existing_data["Kolor RAL"] is not None:
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

scale_stack_and_align_rails(width, height, przetloczenie)
custom_export_to_obj_with_texture(kolor)
custom_export_to_obj_without_mtl()

