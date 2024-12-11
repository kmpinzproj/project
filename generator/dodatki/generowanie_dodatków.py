import json
import bpy
import mathutils
import os
import math

object_names = ["klamka-1.001", "klamka-1.002", "drzwi.001"]

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

handle = bpy.data.objects.get("klamka-1")
door = bpy.data.objects.get("drzwi")
vent = bpy.data.objects.get("wentylv2")
window = bpy.data.objects.get("okno1")
glass = bpy.data.objects.get("szyba")
bpy.context.view_layer.objects.active = door
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)



def add_window(window, glass, option):
    """
    Dodaje okna oraz szyby do bramy w oparciu o dane z pliku JSON.

    Argumenty:
    window -- obiekt ramki okna (bpy.types.Object)
    glass -- obiekt szyby (bpy.types.Object)
    option -- opcja ustawienia okna (1 = poziome, 2 = pionowe obrócone o 90 stopni)

    Zwraca:
    Tuple[List[bpy.types.Object], List[bpy.types.Object]] -- Lista ramek, Lista szyb
    """
    try:
        if not window or not glass:
            print("Nie znaleziono obiektu ramki okna lub szyby.")
            return None, None

        # Wczytaj dane bramy z pliku JSON
        with open("../generator/dodatki/gate_data.json", "r") as json_file:
            gate_data = json.load(json_file)

        # Pobranie danych bramy
        gate_location = gate_data["location"]
        gate_dimensions = gate_data["dimensions"]

        # Obliczenia pozycji
        gate_left_edge_x = gate_location[0] - (gate_dimensions[0] / 2)
        gate_right_edge_x = gate_location[0] + (gate_dimensions[0] / 2)
        gate_bottom_z = gate_location[2] - (gate_dimensions[2] / 2)

        # Pozycja Z okna względem dolnej krawędzi bramy
        if gate_dimensions[2] < 2.6:
            window_z = gate_bottom_z + 1.7  # Wysokość 1.7m od dołu
        else:
            window_z = gate_bottom_z + (gate_dimensions[2] / 2)  # Środek bramy

        frame_objects = []  # Lista ramek
        glass_objects = []  # Lista szyb

        # --- LEWA STRONA ---
        window_copy_left = window.copy()
        window_copy_left.data = window.data.copy()
        bpy.context.collection.objects.link(window_copy_left)

        glass_copy_left = glass.copy()
        glass_copy_left.data = glass.data.copy()
        bpy.context.collection.objects.link(glass_copy_left)

        # Pozycja lewego okna
        window_left_x = -gate_dimensions[0] / 2 + 0.1 + 0.93/2
        window_left_y = gate_location[1]  # Głębokość (Y)
        window_left_z = window_z - 0.1  # Wysokość (Z)

        window_copy_left.location = (window_left_x, window_left_y, window_left_z)
        glass_copy_left.location = (window_left_x, window_left_y, window_left_z)

        if option == "Okna pionowe":  # Obrócenie o 90 stopni
            window_copy_left.rotation_euler[1] = math.radians(90)
            glass_copy_left.rotation_euler[1] = math.radians(90)

        frame_objects.append(window_copy_left)
        glass_objects.append(glass_copy_left)

        # --- PRAWA STRONA ---
        window_copy_right = window.copy()
        window_copy_right.data = window.data.copy()
        bpy.context.collection.objects.link(window_copy_right)

        glass_copy_right = glass.copy()
        glass_copy_right.data = glass.data.copy()
        bpy.context.collection.objects.link(glass_copy_right)

        # Pozycja prawego okna
        window_right_x = gate_right_edge_x - 0.2 - (window_copy_right.dimensions[0] / 2)
        window_right_y = gate_location[1]  # Głębokość (Y)
        window_right_z = window_z - 0.1  # Wysokość (Z)

        window_copy_right.location = (window_right_x, window_right_y, window_right_z)
        glass_copy_right.location = (window_right_x, window_right_y, window_right_z)

        if option == "Okna pionowe":  # Obrócenie o 90 stopni
            window_copy_right.rotation_euler[1] = math.radians(90)
            glass_copy_right.rotation_euler[1] = math.radians(90)

        frame_objects.append(window_copy_right)
        glass_objects.append(glass_copy_right)

        # Zastosowanie transformacji do ramek
        for frame in frame_objects:
            bpy.context.view_layer.objects.active = frame
            frame.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Zastosowanie transformacji do szyb
        for glass in glass_objects:
            bpy.context.view_layer.objects.active = glass
            glass.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        print(f"Ramki i szyby zostały dodane. Liczba ramek: {len(frame_objects)}, Liczba szyb: {len(glass_objects)}")
        return frame_objects, glass_objects

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None, None


 # 1 pionowe, 2 poziome działa na 2 obiektach szyby w glass i ramki na okno w window, pozycjonuje to względem szerokości ide spac


# ale ten to by pasowało na brame uchylna gdzie drzwi sa blisko szczytu na wyzszy szyt mozna dac okno wyzej jak sie miesci

def position_door_from_file(door):
    """
    Tworzy kopię drzwi i ustawia ją 10 cm od lewej krawędzi bramy na podstawie danych z pliku JSON.

    Argumenty:
    door -- obiekt drzwi (bpy.types.Object)
    """
    try:
        # Odczytaj dane bramy z pliku JSON
        with open("../generator/dodatki/gate_data.json", "r") as json_file:
            gate_data = json.load(json_file)

        # Pobranie danych bramy
        gate_location = gate_data["location"]
        gate_dimensions = gate_data["dimensions"]

        # Sprawdzenie poprawności drzwi
        if not door:
            print("Drzwi nie zostały znalezione!")
            return

        # Ustawienie origin na środku geometrii drzwi
        bpy.context.view_layer.objects.active = door
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)  # Zastosowanie transformacji

        # Tworzenie kopii drzwi
        door_copy = door.copy()
        door_copy.data = door.data.copy()
        bpy.context.collection.objects.link(door_copy)

        # Obliczenie lewej krawędzi bramy
        gate_left_edge_x = gate_location[0] - (gate_dimensions[0] / 2)

        # Pobranie szerokości drzwi
        door_width = door_copy.dimensions[0]

        # Obliczenie nowej pozycji dla kopii drzwi
        new_door_x = gate_left_edge_x + 0.1 + (door_width / 2)  # 10 cm od lewej krawędzi bramy
        new_door_y = gate_location[1]  # Taka sama pozycja w osi Y co brama
        new_door_z = gate_location[2] - (gate_dimensions[2] / 2) + (door_copy.dimensions[2] / 2)  # Pozycja Z

        # Ustawienie nowej lokalizacji kopii drzwi
        door_copy.location = (new_door_x, new_door_y, new_door_z)

        # Zastosowanie transformacji dla obiektu
        bpy.context.view_layer.objects.active = door_copy
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        print(f"Drzwi zostały ustawione na pozycji: {door_copy.location}")

        return door_copy  # Zwrócenie kopii drzwi dla dalszego przetwarzania

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

def add_handle(handle,typ = "Klamka 1",  door=None):
    """
    Dodaje kopię klamki zarówno do drzwi, jak i do bramy.

    Jeśli istnieją drzwi, klamka jest dodawana 10 cm od lewej krawędzi drzwi na wysokości 90 cm.
    Jeśli istnieje brama, klamka jest dodawana na środku bramy.

    Argumenty:
    handle -- obiekt klamki (bpy.types.Object)
    door -- obiekt drzwi (bpy.types.Object) (opcjonalny)
    """
    try:
        if not handle:
            print("Nie znaleziono obiektu klamki.")
            return None

        # Wczytaj dane bramy z pliku JSON
        with open("../generator/dodatki/gate_data.json", "r") as json_file:
            gate_data = json.load(json_file)

        # Pobranie danych bramy
        gate_location = gate_data["location"]
        gate_dimensions = gate_data["dimensions"]

        # Ustawienie origin na środku obiektu klamki
        bpy.context.view_layer.objects.active = handle
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        if door:  # Pozycjonowanie klamki na drzwiach
            # Tworzenie kopii klamki dla drzwi
            door_handle_copy = handle.copy()
            door_handle_copy.data = handle.data.copy()
            bpy.context.collection.objects.link(door_handle_copy)

            # Ustawienie origin na środku geometrii drzwi
            bpy.context.view_layer.objects.active = door
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

            # Obliczenie pozycji klamki dla drzwi
            door_left_edge_x = door.location[0]   # Lewa krawędź drzwi
            handle_x = door_left_edge_x + 0.1 + (door_handle_copy.dimensions[0] / 2)  # 10 cm od lewej krawędzi drzwi
            handle_y = door.location[1] - 0.03  # Taka sama pozycja w osi Y co drzwi
            handle_z = door.location[2] - (door.dimensions[2] / 2) + 0.9  # 90 cm od dolnej krawędzi drzwi

            # Ustawienie pozycji klamki dla drzwi
            door_handle_copy.location = (handle_x, handle_y, handle_z)
            print(f"Klamka została dodana do drzwi na pozycji: {door_handle_copy.location}")
            bpy.context.view_layer.objects.active = door_handle_copy
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            return door_handle_copy

        else:  # Pozycjonowanie klamki na bramie
            if typ == "Klamka 2":
                handle = bpy.data.objects.get("klamka-2")
            elif typ == "Klamka 3":
                handle = bpy.data.objects.get("klamka-3")
            elif typ == "Klamka 4":
                handle = bpy.data.objects.get("klamka-4")

            # Tworzenie kopii klamki
            handle_copy = handle.copy()
            handle_copy.data = handle.data.copy()
            bpy.context.collection.objects.link(handle_copy)

            # Obliczenie pozycji klamki względem bramy
            handle_x = gate_location[0]  # Środek bramy
            handle_y = gate_location[1] - 0.03  # Ta sama głębokość (Y) co brama, cofnięcie o 0.03
            gate_bottom_z = gate_location[2] - (gate_dimensions[2] / 2)  # Dolna krawędź bramy
            handle_z = gate_bottom_z + 0.7  # Klamka umieszczona 70 cm nad dolną krawędzią bramy

            # Ustawienie lokalizacji klamki
            handle_copy.location = (handle_x, handle_y, handle_z)

            # Zastosowanie transformacji dla obiektu
            bpy.context.view_layer.objects.active = handle_copy
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            print(f"Klamka została dodana na bramie na pozycji {handle_copy.location}")
            return handle_copy

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None

def position_vent_from_file(vent, option):
    """
    Tworzy kopię kratki wentylacyjnej i ustawia ją w odpowiednim miejscu na podstawie danych z pliku JSON.
    Wszystkie kratki łączy w jeden obiekt i zwraca ten obiekt.

    Argumenty:
    vent -- obiekt kratki wentylacyjnej (bpy.types.Object)
    option -- str, opcja "Lewa", "Prawa" lub "Obustronna"

    Zwraca:
    bpy.types.Object -- Połączony obiekt kratki wentylacyjnej
    """
    try:
        # Odczytaj dane bramy z pliku JSON
        with open("../generator/dodatki/gate_data.json", "r") as json_file:
            gate_data = json.load(json_file)

        # Pobranie danych bramy
        gate_location = gate_data["location"]
        gate_dimensions = gate_data["dimensions"]

        # Sprawdzenie poprawności kratki
        if not vent:
            print("Kratka wentylacyjna nie została znaleziona!")
            return None

        # Ustawienie origin na środku geometrii kratki
        bpy.context.view_layer.objects.active = vent
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

        # Tworzenie kopii kratki
        vent_copies = []

        if option in ["Lewa", "Obustronna"]:
            vent_copy = vent.copy()
            vent_copy.data = vent.data.copy()
            bpy.context.collection.objects.link(vent_copy)

            # Obliczenie lewej pozycji kratki
            vent_x = gate_location[0] - (gate_dimensions[0] / 2) + 0.1 + (vent_copy.dimensions[0] / 2)  # Lewa krawędź
            vent_y = gate_location[1] - 0.03# Ta sama pozycja w osi Y co brama
            vent_z = gate_location[2] - (gate_dimensions[2] / 2) + 0.2  # Wysokość nad dolną krawędzią bramy

            # Ustawienie lokalizacji
            vent_copy.location = (vent_x, vent_y, vent_z)
            vent_copies.append(vent_copy)

        if option in ["Prawa", "Obustronna"]:
            vent_copy = vent.copy()
            vent_copy.data = vent.data.copy()
            bpy.context.collection.objects.link(vent_copy)

            # Obliczenie prawej pozycji kratki
            vent_x = gate_location[0] + (gate_dimensions[0] / 2) - 0.1 - (vent_copy.dimensions[0] / 2)  # Prawa krawędź
            vent_y = gate_location[1] - 0.05# Ta sama pozycja w osi Y co brama
            vent_z = gate_location[2] - (gate_dimensions[2] / 2) + 0.2  # Wysokość nad dolną krawędzią bramy

            # Ustawienie lokalizacji
            vent_copy.location = (vent_x, vent_y, vent_z)
            vent_copies.append(vent_copy)

        # Sprawdzenie, czy są jakiekolwiek kopie kratki do połączenia
        if len(vent_copies) == 0:
            print("Nie dodano żadnej kratki wentylacyjnej.")
            return None

        # Połącz wszystkie kratki w jeden obiekt
        bpy.context.view_layer.objects.active = vent_copies[0]
        for vent_copy in vent_copies:
            vent_copy.select_set(True)

        bpy.ops.object.join()  # Łączymy wszystkie zaznaczone obiekty w jeden
        merged_vent = bpy.context.view_layer.objects.active  # To jest nasz nowy obiekt kratki

        print(f"Kratki wentylacyjne zostały połączone w jeden obiekt: {merged_vent.name}")
        return merged_vent

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None

def export_multiple_objects_to_obj_custom(objects, output_path):
    """
    Eksportuje wiele obiektów do jednego pliku .obj bez użycia operatora Blendera, z obrotem o -90 stopni w osi X.

    Args:
        objects (list of bpy.types.Object): Lista obiektów do eksportu.
        output_path (str): Ścieżka do pliku wyjściowego.
    """
    try:
        # Utwórz macierz obrotu o -90 stopni wokół osi X
        rotation_matrix = mathutils.Matrix.Rotation(-math.radians(90), 4, 'X')

        with open(output_path, 'w') as obj_file:
            obj_file.write("# Exported multiple objects with rotation -90 degrees on X-axis\n")
            vertex_offset = 0  # Offset dla indeksów wierzchołków

            for obj in objects:
                if obj.type != 'MESH':
                    continue

                # Przekształć wierzchołki na globalne współrzędne z obrotem
                mesh = obj.data
                matrix_world = obj.matrix_world

                # Zapisz nazwę obiektu
                obj_file.write(f"o {obj.name}\n")

                # Eksportuj wierzchołki z obrotem
                for vertex in mesh.vertices:
                    world_coord = rotation_matrix @ (matrix_world @ vertex.co)
                    obj_file.write(f"v {world_coord.x:.6f} {world_coord.y:.6f} {world_coord.z:.6f}\n")

                # Eksportuj normalne z obrotem
                for vertex in mesh.vertices:
                    normal = rotation_matrix @ vertex.normal
                    obj_file.write(f"vn {normal.x:.6f} {normal.y:.6f} {normal.z:.6f}\n")

                # Eksportuj współrzędne UV (jeśli istnieją)
                if mesh.uv_layers.active:
                    uv_layer = mesh.uv_layers.active.data
                    for loop in mesh.loops:
                        uv = uv_layer[loop.index].uv
                        obj_file.write(f"vt {uv.x:.6f} {uv.y:.6f}\n")

                # Eksportuj twarze
                for poly in mesh.polygons:
                    face = []
                    for loop_index in poly.loop_indices:
                        vertex_index = mesh.loops[loop_index].vertex_index + 1 + vertex_offset
                        uv_index = loop_index + 1 + vertex_offset
                        normal_index = vertex_index
                        face.append(f"{vertex_index}/{uv_index}/{normal_index}")
                    obj_file.write(f"f {' '.join(face)}\n")

                # Zwiększ offset wierzchołków
                vertex_offset += len(mesh.vertices)

        print(f"Wyeksportowano obiekty do {output_path}")

    except Exception as e:
        print(f"Wystąpił błąd podczas eksportu: {e}")

def export_selected_objects(dodatki, output_path="../generator/dodatki/combined_addons.obj"):
    """
    Eksportuje wybrane obiekty (drzwi, kratka wentylacyjna) do jednego pliku .obj.

    Args:
        dodatki (dict): Wybrane opcje z pliku JSON.
        szerokosc (float): Szerokość bramy.
        door (bpy.types.Object): Obiekt drzwi.
        vent (bpy.types.Object): Obiekt kratki wentylacyjnej.
        output_path (str): Ścieżka do pliku wyjściowego.
    """
    objects_to_export = []

    # Drzwi w bramie
    if "Drzwi w bramie" in dodatki:
        door_copy = position_door_from_file(door)
        if door_copy:
            door_copy.name = "drzwi_w_bramie"
            objects_to_export.append(door_copy)
            print("Dodano drzwi do eksportu.")
            handle_door_copy = add_handle(handle, door=door_copy)
            if handle_door_copy:
                handle_door_copy.name = "klamka_do_drzwi"
                objects_to_export.append(handle_door_copy)
                print("Dodano klamkę od drzwi do eksportu.")

    # Kratka wentylacyjna
    if 'kratka' in dodatki:
        vent_copy = position_vent_from_file(vent, dodatki["kratka"])
        if vent_copy:
            vent_copy.name = "kratka_wentylacyjna"
            objects_to_export.append(vent_copy)
            print("Dodano kratkę wentylacyjną do eksportu.")

    if 'klamka' in dodatki:
        handle_copy = add_handle(handle, dodatki["klamka"])
        if handle_copy:
            handle_copy.name = "klamka_do_bramy"
            objects_to_export.append(handle_copy)
            print("Dodano klamkę do eksportu.")

    if 'okno' in dodatki:
        print("TEST OKNA")
        window_copies, glass_copies = add_window(window, glass, dodatki["okno"])
        if window_copies:
            for idx, frame in enumerate(window_copies, start=1):
                frame.name = f"ramka_okna_{idx}"
                objects_to_export.append(frame)
            print(f"Dodano ramki okienne do eksportu: {[obj.name for obj in window_copies]}")
        if glass_copies:
            for idx, glass2 in enumerate(glass_copies, start=1):
                glass2.name = f"szyba_okna_{idx}"
                objects_to_export.append(glass2)
            print(f"Dodano szyby okienne do eksportu: {[obj.name for obj in glass_copies]}")

    # Eksportuj tylko jeśli mamy jakieś obiekty do eksportu
    if objects_to_export:
        export_multiple_objects_to_obj_custom(objects_to_export, output_path)
        print(f"Wyeksportowano {len(objects_to_export)} obiektów do pliku {output_path}.")
    else:
        print("Brak obiektów do eksportu.")

import json

def read_json(json_path):
    result = {}

    with open(json_path, 'r', encoding='utf-8') as file:
        existing_data = json.load(file)

        if "Wymiary" in existing_data:
            result['wymiary'] = existing_data["Wymiary"]

        if "Przeszklenia" in existing_data and existing_data["Przeszklenia"] is not None:
            result['okno'] = existing_data["Przeszklenia"]

        if "Klamka do bramy" in existing_data and existing_data["Klamka do bramy"] is not None:
            result['klamka'] = existing_data["Klamka do bramy"]

        if "Kratka wentylacyjna" in existing_data and existing_data["Kratka wentylacyjna"] is not None:
            result['kratka'] = existing_data["Kratka wentylacyjna"]

        if "Opcje dodatkowe" in existing_data and existing_data["Opcje dodatkowe"] is not None:
            dodatki = existing_data["Opcje dodatkowe"]
            if "Drzwi w bramie" in dodatki:
                result['Drzwi w bramie'] = True  # Zmieniam na True, bo w poprzednim kodzie 'Drzwi w bramie' nie miały sensu jako wartość

    return result


dodatki = read_json("../resources/selected_options.json")
szerokość = dodatki["wymiary"]["Szerokość"]
print(dodatki)

export_selected_objects(dodatki)