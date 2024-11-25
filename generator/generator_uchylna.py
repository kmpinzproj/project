import bpy
import os
import math
import mathutils
import bmesh

# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["brama-segmentowa", "szyny-na-brame.001", "brama-segmentowa-z-szynami", "brama-uchylna-z-szynami"]

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


def tilt_gate():
    # Nazwa segmentu bazowego
    segment_name = "Cube.002"
    available_segments = ["Cube.002", "Cube.003"]
    # kopia szyny
    rail_name = "szyny-na-brame"

    # Wyświetlenie dostępnych segmentów
    print("Dostępne segmenty:")
    for i, seg_name in enumerate(available_segments):
        print(f"{i + 1}. {seg_name}")

    # Wybór segmentu
    try:
        segment_choice = int(input("Wybierz numer segmentu (1, 2): "))
        if segment_choice < 1 or segment_choice > len(available_segments):
            print("Nieprawidłowy wybór. Spróbuj ponownie.")
            return
        segment_name = available_segments[segment_choice - 1]
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
        x_length_cm = float(input("Podaj szerokość bramy w osi X (w cm): "))
        z_height_cm = float(input("Podaj wysokość bramy w osi Z (w cm): "))
        x_length_m = x_length_cm / 100  # Konwersja cm na metry
        z_height_m = z_height_cm / 100  # Konwersja cm na metry

        # Wymiary segmentu
        segment_width = segment.dimensions[0]
        segment_height = segment.dimensions[2]

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
        print(f"pozostala szerokosc {remaining_width}")
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
        print(segment_copies_x)
        for segment in segment_copies_x:
            segment.select_set(True)  # Zaznacz wszystkie kopie
        # Przykład: Zaznaczanie i łączenie obiektów
        objects_to_join = bpy.context.selected_objects  # Pobierz zaznaczone obiekty

        if objects_to_join:  # Sprawdź, czy są obiekty do złączenia
            bpy.context.view_layer.objects.active = objects_to_join[0]  # Ustaw aktywny obiekt
            bpy.ops.object.join()  # Połącz obiekty
            print("Obiekty zostały połączone.")
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
        print(counter)
        print(segment_height)
        remaining_height = round(z_height_m - (counter * segment_height), 6)
        print(remaining_height)
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
            print(f"Dodano segment o wysokości {remaining_height}m na górę.")
            print(joined_segments)
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
            final_gate.name = "brama-uchylna-z-szynami"

        print(f"Stworzono bramę o wymiarach: {x_length_m}m x {z_height_m}m.")

    except ValueError:
        print("Podano nieprawidłowe dane. Spróbuj ponownie.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


def custom_export_to_obj(object_name="brama-uchylna-z-szynami"):
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
    output_path = "./model.obj"

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
tilt_gate()
custom_export_to_obj()








