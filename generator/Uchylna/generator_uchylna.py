import bpy
import math
import mathutils
import bmesh
import json

# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["brama-segmentowa", "szyny-na-brame.001", "brama-segmentowa-z-szynami", "brama-uchylna-z-szynami", "szyny"]

for object_name in object_names:
    # Sprawdzenie, czy obiekt istnieje
    obj = bpy.data.objects.get(object_name)
    if obj:
        # Ustawienie obiektu jako aktywnego i zaznaczenie
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Usunięcie obiektu
        bpy.ops.object.delete()
    else:
        print(f"Obiekt '{object_name}' nie istnieje.")


def tilt_gate(width, height, wypelnienie = "Poziome"):

    # Nazwa segmentu bazowego
    segment_name = "Cube.002"
    available_segments = {"Poziome": "Cube.002", "Pionowe": "Cube.003","Jodełka w górę": "Cube.005", "START": "Cube.004"}
    # kopia szyny
    rail_name = "szyny-na-brame"

    # Wybór segmentu
    try:
        segment_name = available_segments[wypelnienie]
    except ValueError:
        print("Podano nieprawidłowy numer. Spróbuj ponownie.")
        return

    # Pobierz segment bazowy
    segment = bpy.data.objects.get(segment_name)
    if not segment:
        print(f"Obiekt o nazwie '{segment_name}' nie został znaleziony.")
        return
    rail = bpy.data.objects.get(rail_name)
    if not rail:
        print(f"Obiekt o nazwie '{rail_name}' nie został znaleziony.")
        return

    try:
        # Pobranie wymiarów bramy od użytkownika
        x_length_cm = width
        z_height_cm = height
        x_length_m = x_length_cm / 1000  # Konwersja cm na metry
        z_height_m = z_height_cm / 1000  # Konwersja cm na metry

        # Wymiary segmentu
        segment_width = segment.dimensions[0]
        segment_height = segment.dimensions[2]
        if wypelnienie == "Jodełka w górę":
            # Skalowanie segmentu do podanych wymiarów
            joined_gate = segment.copy()
            joined_gate.data = segment.data.copy()
            bpy.context.collection.objects.link(joined_gate)
            joined_gate.dimensions = (x_length_m, joined_gate.dimensions[1], z_height_m)
            joined_gate.location = (0, 0, z_height_m / 2)
            # Tworzenie kopii szyn i dopasowanie do bramy
            rail_copy = rail.copy()
            bpy.context.collection.objects.link(rail_copy)  # Dodanie kopii szyn do sceny

            # Skalowanie szyn - ustawienie Dimensions w osiach X i Z takie same jak brama, Y pozostaje oryginalne
            rail_copy.dimensions = (x_length_m, rail_copy.dimensions[1], z_height_m)

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
            final_gate.name = "brama-uchylna"

        else:
            # Tworzenie segmentów w osi X
            current_x = 0
            segment_copies_x = []

            while round(current_x + segment_width, 6) <= x_length_m:
                new_segment = segment.copy()
                new_segment.data = segment.data.copy()
                new_segment.location.x = current_x
                bpy.context.collection.objects.link(new_segment)
                segment_copies_x.append(new_segment)
                current_x += segment_width

            # Przycięcie ostatniego segmentu w osi X
            remaining_width = round(x_length_m - current_x, 6)
            if remaining_width > 0.0001:
                last_segment_x = segment.copy()
                last_segment_x.data = segment.data.copy()
                last_segment_x.location.x = current_x
                bpy.context.collection.objects.link(last_segment_x)

                # Cięcie segmentu w osi X
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

            # Łączenie wszystkich x w jeden obiekt
            for segment in segment_copies_x:
                segment.select_set(True)  # Zaznacz wszystkie kopie
            # Przykład: Zaznaczanie i łączenie obiektów
            objects_to_join = bpy.context.selected_objects  # Pobierz zaznaczone obiekty

            if objects_to_join:  # Sprawdź, czy są obiekty do złączenia
                bpy.context.view_layer.objects.active = objects_to_join[0]  # Ustaw aktywny obiekt
                bpy.ops.object.join()  # Połącz obiekty
            else:
                print("Brak zaznaczonych obiektów do połączenia.")

            joined_gate_x = bpy.context.view_layer.objects.active
            joined_gate_x.name = "brama-uchylna-x"  # Zmień nazwę obiektu

            bpy.context.view_layer.objects.active = joined_gate_x
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            # Pobierz początkowe Z obiektu joined_gate_x
            base_z = joined_gate_x.location.z + (joined_gate_x.dimensions[2] / 2)

            # Ustawienie segmentów w osi Z nad obiektem joined_gate_x
            current_z = base_z
            joined_segments = []
            counter = 1

            # Tworzenie segmentów w osi Z, bez przycinania ostatniego
            while round(current_z + segment_height, 6) <= z_height_m + base_z - segment_height:
                new_segment = joined_gate_x.copy()
                new_segment.location.z = current_z + (segment_height / 2)
                bpy.context.collection.objects.link(new_segment)
                joined_segments.append(new_segment)
                current_z += segment_height
                counter += 1

            remaining_height = round(z_height_m - (counter * segment_height), 6)

            if remaining_height > 0.0001:
                # Kopiowanie ostatniego segmentu
                last_segment_z = joined_gate_x.copy()
                last_segment_z.data = joined_gate_x.data.copy()
                last_segment_z.location.z = current_z + (remaining_height / 2)
                bpy.context.collection.objects.link(last_segment_z)

                # Przycinanie segmentu w osi Z
                bpy.context.view_layer.objects.active = last_segment_z
                bm = bmesh.new()
                bm.from_mesh(last_segment_z.data)
                result = bmesh.ops.bisect_plane(
                    bm,
                    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                    plane_co=(0, 0, -(segment_height / 2) + remaining_height),  # Płaszczyzna cięcia w osi Z
                    plane_no=(0, 0, 1),  # Normalna osi Z (cięcie w pionie)
                    clear_outer=True  # Usuń górną część
                )
                bmesh.ops.contextual_create(bm, geom=result['geom'])
                bm.to_mesh(last_segment_z.data)
                bm.free()
                bpy.context.view_layer.objects.active = last_segment_z
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

                if joined_segments:  # Jeśli istnieją inne segmenty
                    last_segment_z.location.z = joined_segments[-1].location.z + (joined_segments[-1].dimensions[2] / 2) + (
                                remaining_height / 2)
                else:  # Jeśli to pierwszy segment w osi Z
                    last_segment_z.location.z = current_z + (remaining_height / 2)

                joined_segments.append(last_segment_z)  # Dodanie przyciętego segmentu do listy

                for seg in joined_segments:
                    seg.select_set(True)

                # Ustaw pierwszy obiekt jako aktywny
                bpy.context.view_layer.objects.active = joined_segments[0]

                # Połącz wszystkie wybrane obiekty
                bpy.ops.object.join()
                joined_gate = bpy.context.view_layer.objects.active
                joined_gate.name = "brama-uchylna"  # Zmień nazwę obiektu
                bpy.context.view_layer.objects.active = joined_gate
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

            joined_gate.location = (0,0, joined_gate.dimensions[2]/2)
            add_and_align_rails(joined_gate)

    except ValueError:
        print("Podano nieprawidłowe dane. Spróbuj ponownie.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


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

def custom_export_to_obj_with_texture(texture_path, object_name="brama-uchylna", output_obj_path="model.obj", output_mtl_path="model.mtl"):
    """
    Eksportuje obiekt do pliku .obj z rotacją 90 stopni w osi X,
    ukrywając inne obiekty w scenie.
    Tworzy również plik .mtl z odniesieniem do tekstury.
    """
    # Sprawdź, czy obiekt istnieje
    obj = bpy.data.objects.get(object_name)
    if not obj:
        print(f"Obiekt '{object_name}' nie został znaleziony w scenie.")
        return

    # Ścieżki wyjściowe
    output_obj_path = "../generator/" + output_obj_path
    output_mtl_path = "../generator/" + output_mtl_path

    # Rotacja o 90 stopni w osi X
    rotation_matrix = mathutils.Matrix.Rotation(-math.radians(90), 4, 'X')
    transformed_matrix = rotation_matrix @ obj.matrix_world

    # Tworzenie pliku MTL z teksturą
    with open(output_mtl_path, 'w') as mtl_file:
        mtl_file.write(f"# Material file for {object_name}\n")
        mtl_file.write(f"newmtl BramaMaterial\n")
        mtl_file.write(f"Ka 0.2 0.2 0.2\n")  # Ambient color
        mtl_file.write(f"Kd 1.0 1.0 1.0\n")  # Diffuse color (white for full texture)
        mtl_file.write(f"Ks 0.5 0.5 0.5\n")  # Specular color
        mtl_file.write(f"Ns 50.0\n")  # Shininess
        mtl_file.write(f"d 1.0\n")  # Opacity
        mtl_file.write(f"illum 2\n")  # Illumination model
        mtl_file.write(f"map_Kd {texture_path}\n")  # Odniesienie do tekstury

    # Tworzenie pliku OBJ
    with open(output_obj_path, 'w') as obj_file:
        # Dodanie odniesienia do pliku MTL
        obj_file.write(f"mtllib {output_mtl_path}\n")
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
        obj_file.write(f"usemtl BramaMaterial\n")  # Przypisz materiał do powierzchni
        for poly in mesh.polygons:
            face_vertices = []
            for loop_index in poly.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                uv_index = loop_index + 1  # UV index (OBJ numbering starts from 1)
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

        if "Wymiary" in existing_data:
            wymiary = existing_data["Wymiary"]
        if "Układ wypełnienia" in existing_data and existing_data["Układ wypełnienia"] is not None:
            wypelnienie = existing_data["Układ wypełnienia"]
        else:
            wypelnienie = "START"
        if "Kolor standardowy" in existing_data and existing_data["Kolor standardowy"] is not None:
            name = existing_data["Kolor standardowy"]
            print(existing_data)
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
        return [wymiary, wypelnienie, kolor]


dimensions, wypelnienie, kolor = read_json("../resources/selected_options.json")
width = dimensions.get("Szerokość")
height = dimensions.get("Wysokość")

# Uruchom funkcję
tilt_gate(width, height, wypelnienie)
custom_export_to_obj_with_texture(kolor)
custom_export_to_obj_without_mtl()







