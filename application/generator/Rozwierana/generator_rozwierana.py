import bpy
import os
import math
import mathutils
import bmesh
from mathutils import Vector
from math import radians
import json
import sys
# Pobierz argumenty przekazane po "--"
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # Wszystkie argumenty po "--"

# Pierwszy argument to ścieżka do zasobów
resources_path = argv[0]

# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["szyny", "szyny-na-brame.001", "brama-uchylna-z-szynami", "Right_Door", "Left_Door", "brama-uchylna", "brama-koniec"]

for object_name in object_names:
    # Sprawdzenie, czy obiekt istnieje
    obj = bpy.data.objects.get(object_name)
    if obj:
        # Ustawienie obiektu jako aktywnego i zaznaczenie
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Usunięcie obiektu
        bpy.ops.object.delete()


def cut_object(obj, plane_co, plane_no, clear_outer):
    bpy.context.view_layer.objects.active = obj
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = bmesh.ops.bisect_plane(
        bm,
        geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
        plane_co=plane_co,
        plane_no=plane_no,
        clear_outer=clear_outer,
    )
    bmesh.ops.contextual_create(bm, geom=result['geom'])
    bm.to_mesh(obj.data)
    bm.free()


def tilt_gate_rozwierana(width, height, ilosc_skrzydel, wypelnienie=None):
    """
    Generuje model bramy rozwieranej z uwzględnieniem ilości skrzydeł i układu wypełnienia.

    Args:
        width (float): Szerokość bramy w milimetrach.
        height (float): Wysokość bramy w milimetrach.
        ilosc_skrzydel (str): Ilość skrzydeł bramy ("Jednoskrzydłowe prawe", "Jednoskrzydłowe lewe", "Dwuskrzydłowe").
        wypelnienie (str): Układ wypełnienia ("Poziome", "Pionowe", "Jodełka w górę", "Jodełka w dół", "START").
    """
    # Nazwa segmentu bazowego
    available_cube = {"Poziome": "Cube.002", "Pionowe": "Cube.003", "Jodełka w górę": "Cube.005", "START": "Cube.004","Jodełka w dół": "Cube.006"}
    segment_name = available_cube[uklad_wypelnienia]
    available_segments = {"Jednoskrzydłowe prawe": 1, "Jednoskrzydłowe lewe": 2, "Dwuskrzydłowe": 3, "START": 0}
    segment_choice = available_segments[ilosc_skrzydel]

    # Pobierz segment bazowy
    segment = bpy.data.objects.get(segment_name)
    if not segment:
        print(f"Obiekt o nazwie '{segment_name}' nie został znaleziony.")
        return

    try:
        x_length_m = width / 1000
        z_height_m = height / 1000

        segment_width = segment.dimensions[0]
        segment_height = segment.dimensions[2]

        if wypelnienie == "Jodełka w górę" or wypelnienie == "Jodełka w dół":
            # Jodełka w górę - Rozciąganie całego segmentu
            new_gate = segment.copy()
            new_gate.data = segment.data.copy()
            bpy.context.collection.objects.link(new_gate)

            new_gate.dimensions = (x_length_m, new_gate.dimensions[1], z_height_m)
            new_gate.location = (0, 0, z_height_m / 2)
            new_gate.name = "brama-koniec"
            # Ustawienie originu
            bpy.context.view_layer.objects.active = new_gate
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            joined_gate = new_gate

        elif wypelnienie == "Poziome" or wypelnienie == "START":
            # Rozciągamy pierwszy segment na szerokość
            first_segment = segment.copy()
            first_segment.data = segment.data.copy()
            bpy.context.collection.objects.link(first_segment)
            first_segment.dimensions[0] = x_length_m

            current_z = 0
            segment_copies_z = []

            while round(current_z + segment_height, 6) <= z_height_m:
                new_segment = first_segment.copy()
                new_segment.data = first_segment.data.copy()
                new_segment.location.z = current_z
                bpy.context.collection.objects.link(new_segment)
                segment_copies_z.append(new_segment)
                current_z += segment_height

            remaining_height = round(z_height_m - current_z, 6)
            if remaining_height > 0.0001:
                last_segment_z = first_segment.copy()
                last_segment_z.data = first_segment.data.copy()
                last_segment_z.location.z = current_z
                bpy.context.collection.objects.link(last_segment_z)

                bpy.context.view_layer.objects.active = last_segment_z
                bm = bmesh.new()
                bm.from_mesh(last_segment_z.data)
                result = bmesh.ops.bisect_plane(
                    bm,
                    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                    plane_co=(0, 0, -(segment_height / 2) + remaining_height),
                    plane_no=(0, 0, 1),
                    clear_outer=True
                )
                bmesh.ops.contextual_create(bm, geom=result['geom'])
                bm.to_mesh(last_segment_z.data)
                bm.free()

                segment_copies_z.append(last_segment_z)

            for segment in segment_copies_z:
                segment.select_set(True)
            bpy.context.view_layer.objects.active = segment_copies_z[0]
            bpy.ops.object.join()
            joined_gate = bpy.context.view_layer.objects.active
            joined_gate.name = "brama-koniec"

        elif wypelnienie == "Pionowe":
            # Rozciągamy pierwszy segment na wysokość
            first_segment = segment.copy()
            first_segment.data = segment.data.copy()
            bpy.context.collection.objects.link(first_segment)
            first_segment.dimensions[2] = z_height_m

            current_x = 0
            segment_copies_x = []

            while round(current_x + segment_width, 6) <= x_length_m:
                new_segment = first_segment.copy()
                new_segment.data = first_segment.data.copy()
                new_segment.location.x = current_x
                bpy.context.collection.objects.link(new_segment)
                segment_copies_x.append(new_segment)
                current_x += segment_width

            remaining_width = round(x_length_m - current_x, 6)
            if remaining_width > 0.0001:
                last_segment_x = first_segment.copy()
                last_segment_x.data = first_segment.data.copy()
                last_segment_x.location.x = current_x
                bpy.context.collection.objects.link(last_segment_x)

                bpy.context.view_layer.objects.active = last_segment_x
                bm = bmesh.new()
                bm.from_mesh(last_segment_x.data)
                result = bmesh.ops.bisect_plane(
                    bm,
                    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                    plane_co=(-(segment_width / 2) + remaining_width, 0, 0),
                    plane_no=(1, 0, 0),
                    clear_outer=True
                )
                bmesh.ops.contextual_create(bm, geom=result['geom'])
                bm.to_mesh(last_segment_x.data)
                bm.free()

                segment_copies_x.append(last_segment_x)

            for segment in segment_copies_x:
                segment.select_set(True)
            bpy.context.view_layer.objects.active = segment_copies_x[0]
            bpy.ops.object.join()
            joined_gate = bpy.context.view_layer.objects.active
            joined_gate.name = "brama-koniec"

        bpy.context.view_layer.objects.active = joined_gate
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        # --- POZYCJA BRAMY ---
        joined_gate.location.x = 0  # Środek w osi X
        joined_gate.location.y = 0  # Środek w osi Y
        joined_gate.location.z = joined_gate.dimensions[2] / 2

        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        add_and_align_rails(joined_gate)

        gate_data = {
            "location": [joined_gate.location.x, joined_gate.location.y, joined_gate.location.z],
            "dimensions": [joined_gate.dimensions.x, joined_gate.dimensions.y, joined_gate.dimensions.z]
        }

        with open(resources_path +"application/generator/dodatki/gate_data.json", "w") as json_file:
            json.dump(gate_data, json_file)


        if segment_choice == 3:  # ----------------------------------------------------- tu masz na podwójną warunek
            # Pobierz wymiary obiektu i jego połowę w osi X
            dimension_x = joined_gate.dimensions.x
            half_x = dimension_x / 2

            # Utwórz kopię dla lewej części drzwi
            left_door = joined_gate.copy()
            left_door.data = joined_gate.data.copy()
            bpy.context.collection.objects.link(left_door)

            # Utwórz kopię dla prawej części drzwi
            right_door = joined_gate.copy()
            right_door.data = joined_gate.data.copy()
            bpy.context.collection.objects.link(right_door)

            # Przycinamy lewą część (usuń prawą stronę)
            cut_object(
                left_door,
                plane_co=(0, 0, 0),  # Płaszczyzna cięcia na połowie wymiaru X
                plane_no=(1, 0, 0),  # Normalna płaszczyzny cięcia (w kierunku dodatniego X)
                clear_outer=True  # Usuń wszystko na prawo od płaszczyzny
            )

            # Przycinamy prawą część (usuń lewą stronę)
            cut_object(
                right_door,
                plane_co=(0, 0, 0),  # Płaszczyzna cięcia na połowie wymiaru X
                plane_no=(-1, 0, 0),  # Normalna płaszczyzny cięcia (w kierunku ujemnego X)
                clear_outer=True  # Usuń wszystko na lewo od płaszczyzny
            )

            # Nadajemy nazwy
            left_door.name = "Left_Door"
            # Pobierz bounding box obiektu w przestrzeni lokalnej---------------------------------------------------------------
            dimensions = left_door.dimensions
            bounding_box = [left_door.matrix_world @ Vector(corner) for corner in left_door.bound_box]

            # Znajdź prawą, pionową krawędź z tyłu
            # Maksymalna wartość X (prawo) i maksymalna wartość Y (tył)
            right_back_x = min(v.x for v in bounding_box)  # Maksymalny X
            right_back_y = max(v.y for v in bounding_box)  # Maksymalny Y
            right_back_z = left_door.dimensions[2] / 2  # Połowa wysokości Z

            # Utwórz współrzędne punktu
            right_back_corner = Vector((right_back_x, right_back_y, right_back_z))

            # Przenieś 3D Cursor na obliczoną pozycję
            bpy.context.scene.cursor.location = right_back_corner

            # Zaznacz obiekt i ustaw origin
            bpy.ops.object.select_all(action='DESELECT')  # Odznacz wszystkie obiekty
            left_door.select_set(True)  # Zaznacz tylko obiekt joined_gate
            bpy.context.view_layer.objects.active = left_door  # Ustaw go jako aktywny
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')  # Ustaw origin na kursorze
            left_door.rotation_euler[2] -= radians(5)

            right_door.name = "Right_Door"
            # przesuwam pivot prawych drzwi------------------------------------------------------------------------------------------
            # Pobierz bounding box obiektu w przestrzeni lokalnej
            bounding_box = [right_door.matrix_world @ Vector(corner) for corner in right_door.bound_box]

            # Znajdź prawą, pionową krawędź z tyłu
            # Maksymalna wartość X (prawo) i maksymalna wartość Y (tył)
            right_back_x = max(v.x for v in bounding_box)  # Maksymalny X
            right_back_y = max(v.y for v in bounding_box)  # Maksymalny Y
            right_back_z = joined_gate.dimensions[2] / 2  # Połowa wysokości Z

            # Utwórz współrzędne punktu
            right_back_corner = Vector((right_back_x, right_back_y, right_back_z))

            # Przenieś 3D Cursor na obliczoną pozycję
            bpy.context.scene.cursor.location = right_back_corner

            # Zaznacz obiekt i ustaw origin
            bpy.ops.object.select_all(action='DESELECT')  # Odznacz wszystkie obiekty
            right_door.select_set(True)  # Zaznacz tylko obiekt joined_gate
            bpy.context.view_layer.objects.active = joined_gate  # Ustaw go jako aktywny
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')  # Ustaw origin na kursorze
            right_door.rotation_euler[2] += radians(10)
            # Ukrycie oryginalnego obiektu
            joined_gate.hide_set(True)
        elif segment_choice in [1,2,0]:
            # Pobierz bounding box obiektu w przestrzeni lokalnej
            bounding_box = [joined_gate.matrix_world @ Vector(corner) for corner in joined_gate.bound_box]

            if segment_choice == 2:  # Lewa stronna
                right_back_x = bounding_box[0].x  # lewa dolna krawędź
            elif segment_choice == 1:  # Prawa stronna
                right_back_x = bounding_box[4].x  # prawa dolna krawędź
            elif segment_choice == 0:  # Prawa stronna
                right_back_x = bounding_box[4].x  # prawa dolna krawędź


            right_back_y = max(v.y for v in bounding_box)  # Tylna część bramy (maksymalna Y)
            right_back_z = joined_gate.dimensions[2] / 2  # Środek wysokości Z

            right_back_corner = Vector((right_back_x, right_back_y, right_back_z))

            bpy.context.scene.cursor.location = right_back_corner
            bpy.context.view_layer.update()

            bpy.ops.object.select_all(action='DESELECT')
            joined_gate.select_set(True)
            bpy.context.view_layer.objects.active = joined_gate
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            if segment_choice == 2:  # Lewa stronna
                bpy.context.view_layer.objects.active = joined_gate
                joined_gate.rotation_euler[2] -= radians(10)
                joined_gate.name = "Left_Door"
            elif segment_choice == 1:  # Prawa stronna
                bpy.context.view_layer.objects.active = joined_gate
                joined_gate.rotation_euler[2] += radians(10)
                joined_gate.name = "Right_Door"
            elif segment_choice == 0:
                joined_gate.name = "Right_Door"

            bpy.context.view_layer.objects.active = joined_gate
            bpy.context.view_layer.update()
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)




    except ValueError:
        print("Podano nieprawidłowe dane. Spróbuj ponownie.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


def add_and_align_rails(gate):
    """
    Dodaje szyny do bramy rozwieranej i dopasowuje je do wymiarów bramy.

    Args:
        gate (Object): Obiekt bramy rozwieranej, do którego dodawane są szyny.
    """
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
        scale_x = gate.dimensions[0] / rail.dimensions[0]  # Skalowanie szerokości (X)
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

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

def custom_export_to_obj_without_mtl(object_name="szyny", output_obj_path="szyny.obj"):
    """
    Eksportuje obiekt do pliku .obj bez pliku .mtl.

    Args:
        object_name (str): Nazwa obiektu w Blenderze do eksportu.
        output_obj_path (str): Ścieżka do pliku .obj.
    """
    obj = bpy.data.objects.get(object_name)
    if not obj:
        print(f"Obiekt '{object_name}' nie został znaleziony w scenie.")
        return

    output_obj_path = resources_path +"application/generator/" + output_obj_path

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

def export_doors_to_obj_with_mtl(texture_path, left_door_name="Left_Door", right_door_name="Right_Door",
                                 output_obj_path="model.obj", output_mtl_path1="model.mtl"):
    """
    Eksportuje drzwi (lewe i prawe) do pliku .obj wraz z plikiem .mtl, zawierającym informacje o teksturze.

    Args:
        texture_path (str): Ścieżka do pliku tekstury.
        left_door_name (str): Nazwa obiektu drzwi lewych w Blenderze.
        right_door_name (str): Nazwa obiektu drzwi prawych w Blenderze.
        output_obj_path (str): Ścieżka do pliku .obj.
        output_mtl_path (str): Ścieżka do pliku .mtl.
    """
    # Pobierz obiekty lewe i prawe drzwi
    left_door = bpy.data.objects.get(left_door_name)
    right_door = bpy.data.objects.get(right_door_name)

    # Sprawdzenie, czy przynajmniej jeden z obiektów istnieje
    if not left_door and not right_door:
        print(f"Nie znaleziono żadnych drzwi: {left_door_name} ani {right_door_name}.")
        return

    # Lista obiektów do eksportu
    objects_to_export = []

    if left_door:
        left_door_copy = left_door.copy()
        left_door_copy.data = left_door.data.copy()
        bpy.context.collection.objects.link(left_door_copy)
        objects_to_export.append(left_door_copy)

    if right_door:
        right_door_copy = right_door.copy()
        right_door_copy.data = right_door.data.copy()
        bpy.context.collection.objects.link(right_door_copy)
        objects_to_export.append(right_door_copy)

    # Jeśli jest więcej niż jeden obiekt, połącz je w jeden
    if len(objects_to_export) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects_to_export:
            obj.select_set(True)

        bpy.context.view_layer.objects.active = objects_to_export[0]
        bpy.ops.object.join()

        combined_doors = bpy.context.view_layer.objects.active
        combined_doors.name = "Combined_Doors"
    else:
        combined_doors = objects_to_export[0]
        combined_doors.name = "Single_Door"

    # Przygotowanie ścieżek do zapisu
    output_obj_path = resources_path + "application/generator/" + output_obj_path
    output_mtl_path = resources_path + "application/generator/" + output_mtl_path1

    # Obrót obiektu o -90 stopni w osi X
    rotation_matrix = mathutils.Matrix.Rotation(-math.radians(90), 4, 'X')
    transformed_matrix = rotation_matrix @ combined_doors.matrix_world

    # Przygotowanie pliku MTL
    with open(output_mtl_path, 'w') as mtl_file:
        mtl_file.write(f"# Material file for Doors\n")
        if texture_path:
            mtl_file.write(f"newmtl DoorMaterial\n")
            mtl_file.write(f"Ka 0.2 0.2 0.2\n")
            mtl_file.write(f"Kd 1.0 1.0 1.0\n")
            mtl_file.write(f"Ks 0.5 0.5 0.5\n")
            mtl_file.write(f"Ns 50.0\n")
            mtl_file.write(f"d 1.0\n")
            mtl_file.write(f"illum 2\n")
            mtl_file.write(f"map_Kd {texture_path}\n")
        else:
            print("Nie podano tekstury. Plik MTL będzie pusty.")

    # Eksportuj obiekt do pliku .obj
    with open(output_obj_path, 'w') as obj_file:
        obj_file.write(f"mtllib {os.path.basename(output_mtl_path1)}\n")
        obj_file.write(f"# Exported from Blender with rotation -90 degrees in X-axis\n")
        obj_file.write(f"# Object: Combined_Doors\n\n")

        # Eksportuj wierzchołki
        mesh = combined_doors.data
        for vertex in mesh.vertices:
            world_coord = transformed_matrix @ vertex.co
            obj_file.write(f"v {world_coord.x} {world_coord.y} {world_coord.z}\n")

        # Eksportuj normalne
        if mesh.polygons:
            for poly in mesh.polygons:
                rotated_normal = rotation_matrix @ poly.normal
                obj_file.write(f"vn {rotated_normal.x} {rotated_normal.y} {rotated_normal.z}\n")

        # Eksportuj współrzędne UV
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
            obj_file.write(f"usemtl DoorMaterial\n")
            obj_file.write(f"f {' '.join(face_vertices)}\n")

    # Usuń tymczasowe obiekty
    bpy.data.objects.remove(combined_doors)

def read_json(json_path):
    """
    Wczytuje dane z pliku JSON i zwraca wymiary, ilość skrzydeł, układ wypełnienia oraz ścieżkę do tekstury.

    Args:
        json_path (str): Ścieżka do pliku JSON.

    Returns:
        tuple: Wymiary (dict), ilość skrzydeł (str), układ wypełnienia (str), ścieżka do tekstury (str).
    """
    with open(json_path, 'r', encoding='utf-8') as file:
        existing_data = json.load(file)
        # Zachowaj 'Typ bramy' i 'Wymiary'
        if "Wymiary" in existing_data:
            wymiary = existing_data["Wymiary"]
        if "Ilość skrzydeł" in existing_data and existing_data["Ilość skrzydeł"] is not None:
            przetloczenie = existing_data["Ilość skrzydeł"]
        else:
            przetloczenie = "START"
        if "Układ wypełnienia" in existing_data and existing_data["Układ wypełnienia"] is not None:
            uklad_wypelnienia = existing_data["Układ wypełnienia"]
        else:
            uklad_wypelnienia = "START"
        if "Kolor standardowy" in existing_data and existing_data["Kolor standardowy"] is not None:
            name = existing_data["Kolor standardowy"]
            base_path = resources_path + "jpg/Kolor_Standardowy/"
            sanitized_name = name.strip()
            kolor = f"{base_path}{sanitized_name}.png"
        elif "Kolor RAL" in existing_data and existing_data["Kolor RAL"] is not None:
            name = existing_data["Kolor RAL"]
            base_path = resources_path+"jpg/Kolor_RAL/"
            sanitized_name = name.strip()
            kolor = f"{base_path}{sanitized_name}.png"
        else:
            kolor = resources_path+"jpg/Kolor_RAL/7040.png"
        return [wymiary, przetloczenie, kolor, uklad_wypelnienia]


# Uruchom funkcję
dimensions, ilosc_skrzydel, kolor, uklad_wypelnienia = read_json(resources_path+"/resources/selected_options.json")
width = dimensions.get("Szerokość")
height = dimensions.get("Wysokość")
tilt_gate_rozwierana(width, height, ilosc_skrzydel, uklad_wypelnienia)
export_doors_to_obj_with_mtl(kolor)
custom_export_to_obj_without_mtl()










