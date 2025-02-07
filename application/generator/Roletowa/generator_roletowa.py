import bpy
import math
import mathutils
import json
import bmesh
import sys
# Pobierz argumenty przekazane po "--"
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # Wszystkie argumenty po "--"

# Pierwszy argument to ścieżka do zasobów
resources_path = argv[0]
# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["brama-segmentowa", "szyny-na-brame.001", "brama-segmentowa-z-szynami", "brama-uchylna-z-szynami", "brama-roletowa","szyny", "brama-koniec"]

for object_name in object_names:
    # Sprawdzenie, czy obiekt istnieje
    obj = bpy.data.objects.get(object_name)
    if obj:
        # Ustawienie obiektu jako aktywnego i zaznaczenie
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Usunięcie obiektu
        bpy.ops.object.delete()


def tilt_gate(width, height, wysokosc_profilu):
    """
    Generuje model bramy roletowej na podstawie szerokości, wysokości i wysokości profilu.

    Args:
        width (float): Szerokość bramy w milimetrach.
        height (float): Wysokość bramy w milimetrach.
        wysokosc_profilu (str): Typ profilu ("77 mm", "100 mm").
    """
    # Nazwa segmentu bazowego
    segment_name = "Cube.002"
    available_segments = ["seg1", "seg2"]

    # Wyświetlenie dostępnych segmentów
    available_segments = {"77 mm": "seg1", "100 mm": "seg2", "START": "seg0"}

    # Wybór segmentu
    segment_name = available_segments[wysokosc_profilu]

    # Pobierz segment bazowy
    segment = bpy.data.objects.get(segment_name)
    if not segment:
        print(f"Obiekt o nazwie '{segment_name}' nie został znaleziony.")
        return

    try:
        # Pobranie wymiarów bramy od użytkownika
        x_length_m = width / 1000  # Konwersja cm na metry
        z_height_m = height / 1000  # Konwersja cm na metry

        # Wymiary segmentu
        segment_height = round(segment.dimensions[2], 3)

        # Tworzenie głównego segmentu w osi X
        joined_gate_x = segment.copy()
        joined_gate_x.data = segment.data.copy()

        joined_gate_x.location = (0, 0, segment_height / 2)  # Umieszczamy główny segment na dolnej krawędzi

        bpy.context.collection.objects.link(joined_gate_x)
        joined_gate_x.dimensions[0] = x_length_m
        joined_gate_x.name = "brama-segmentowa-x"

        # Ustawienie origin na środek obiektu
        bpy.context.view_layer.objects.active = joined_gate_x
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        # Tworzenie segmentów w osi Z
        current_z = segment_height  # Górna krawędź głównego segmentu
        joined_segments = [joined_gate_x]

        while round(current_z + segment_height, 6) <= z_height_m:  # Dodajemy pełne segmenty
            new_segment = joined_gate_x.copy()
            new_segment.location.z = current_z + segment_height / 2  # Umieszczanie nad poprzednim segmentem
            bpy.context.collection.objects.link(new_segment)
            joined_segments.append(new_segment)
            current_z += segment_height

        # Sprawdzenie, czy pozostała reszta do uzupełnienia
        remaining_height = round(z_height_m - current_z, 3)
        if remaining_height > 0:
            last_segment_z = joined_gate_x.copy()
            last_segment_z.data = joined_gate_x.data.copy()
            last_segment_z.location.z = current_z + last_segment_z.dimensions[2]/2  # Dopasowanie ostatniego segmentu
            bpy.context.collection.objects.link(last_segment_z)

            # Przycinanie ostatniego segmentu w osi Z
            bpy.context.view_layer.objects.active = last_segment_z
            bm = bmesh.new()
            bm.from_mesh(last_segment_z.data)
            if segment.name == "seg2":
                result = bmesh.ops.bisect_plane(
                    bm,
                    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                    plane_co=(0, 0, -1 + (remaining_height*10*2)),
                    plane_no=(0, 0, 1),
                    clear_outer=True
                )
            else:
                result = bmesh.ops.bisect_plane(
                    bm,
                    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                    plane_co=(0, 0, -1 + remaining_height*10*2.597),
                    plane_no=(0, 0, 1),
                    clear_outer=True
                )
                
                
            bmesh.ops.contextual_create(bm, geom=result['geom'])
            bm.to_mesh(last_segment_z.data)
            bm.free()
            bpy.context.view_layer.objects.active = last_segment_z

            joined_segments.append(last_segment_z)
        for seg in joined_segments:
            seg.select_set(True)
        # Ustaw pierwszy obiekt jako aktywny
        bpy.context.view_layer.objects.active = joined_segments[0]

        # Połącz wszystkie wybrane obiekty
        bpy.ops.object.join()
        joined_gate = bpy.context.view_layer.objects.active
        joined_gate.name = "brama-koniec" # Zmień nazwę obiektu
        bpy.context.view_layer.objects.active = joined_gate
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        # Informacje końcowe
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
            with open(resources_path + "application/generator/dodatki/gate_data.json", "w") as json_file:
                json.dump(gate_data, json_file)
        else:
            print("Nie znaleziono obiektu bramy.")

        return joined_gate

    except ValueError:
        print("Podano nieprawidłowe dane. Spróbuj ponownie.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        
def add_and_align_rails(gate):
    """
    Dodaje szyny do bramy roletowej i dopasowuje je do wymiarów bramy.

    Args:
        gate (Object): Obiekt bramy roletowej, do którego dodawane są szyny.
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

# Uruchom funkcję
def custom_export_to_obj_with_texture(texture_path, object_name="brama-koniec",
                                      output_obj_path="model.obj", output_mtl_path1="model.mtl"):
    """
    Eksportuje obiekt do pliku .obj z teksturą i plikiem .mtl.

    Args:
        texture_path (str): Ścieżka do tekstury.
        object_name (str): Nazwa eksportowanego obiektu w Blenderze.
        output_obj_path (str): Ścieżka do pliku .obj.
        output_mtl_path (str): Ścieżka do pliku .mtl.
    """
    obj = bpy.data.objects.get(object_name)
    if not obj:
        print(f"Obiekt '{object_name}' nie został znaleziony w scenie.")
        return

    output_obj_path = resources_path +"application/generator/" + output_obj_path
    output_mtl_path = resources_path +"application/generator/" + output_mtl_path1

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
        obj_file.write(f"mtllib {output_mtl_path1}\n")
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
    """
    Eksportuje obiekt do pliku .obj bez pliku .mtl.

    Args:
        object_name (str): Nazwa eksportowanego obiektu w Blenderze.
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

def read_json(json_path):
    """
    Wczytuje dane z pliku JSON i zwraca wymiary, wysokość profili oraz ścieżkę do tekstury.

    Args:
        json_path (str): Ścieżka do pliku JSON.

    Returns:
        tuple: Wymiary (dict), wysokość profili (str), ścieżka do tekstury (str).
    """
    with open(json_path, 'r', encoding='utf-8') as file:
        existing_data = json.load(file)
        # Zachowaj 'Typ bramy' i 'Wymiary'
        if "Wymiary" in existing_data:
            wymiary = existing_data["Wymiary"]
        if "Wysokość profili" in existing_data and existing_data["Wysokość profili"] is not None:
            przetloczenie = existing_data["Wysokość profili"]
        else:
            przetloczenie = "START"
        if "Kolor standardowy" in existing_data and existing_data["Kolor standardowy"] is not None:
            name = existing_data["Kolor standardowy"]
            base_path = resources_path + "jpg/Kolor_Standardowy/"
            sanitized_name = name.strip()
            kolor = f"{base_path}{sanitized_name}.png"
        elif "Kolor RAL" in existing_data and existing_data["Kolor RAL"] is not None:
            name = existing_data["Kolor RAL"]
            base_path = resources_path + "jpg/Kolor_RAL/"
            sanitized_name = name.strip()
            kolor = f"{base_path}{sanitized_name}.png"
        else:
            kolor = resources_path + "jpg/Kolor_RAL/7040.png"
        return [wymiary, przetloczenie, kolor]

# Uruchom funkcję
dimensions, wysokosc_profilu, kolor = read_json(resources_path+"/resources/selected_options.json")
width = dimensions.get("Szerokość")
height = dimensions.get("Wysokość")

tilt_gate(width, height, wysokosc_profilu)
custom_export_to_obj_with_texture(kolor)
custom_export_to_obj_without_mtl()







