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

handle = bpy.data.objects.get("klamka-1")
door = bpy.data.objects.get("drzwi")
vent = bpy.data.objects.get("wentylv2")
window = bpy.data.objects.get("okno1")
glass = bpy.data.objects.get("szyba")
bpy.context.view_layer.objects.active = door
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def add_window_rolling(window, glass, segment):
    """
    Dodaje okna do bramy roletowej, rozmieszczając je na środku każdego segmentu, z wyjątkiem ostatniego segmentu.
    Dane szerokości, wysokości bramy i wysokości segmentu są pobierane z pliku JSON.

    Argumenty:
    window -- obiekt ramki okna (bpy.types.Object)
    glass -- obiekt szyby (bpy.types.Object)
    segment_height -- wysokość pojedynczego segmentu (float)

    Zwraca:
    Tuple[List[bpy.types.Object], List[bpy.types.Object]] -- Lista ramek, lista szyb.
    """
    try:
        # --- 1. Wczytaj dane bramy z pliku JSON ---
        with open("../generator/dodatki/gate_data.json", "r") as json_file:
            gate_data = json.load(json_file)

        # Pobranie szerokości i wysokości bramy z JSON
        width = gate_data["dimensions"][0]
        height = gate_data["dimensions"][2]
        segment_height = 0
        if segment == "100 mm":
            segment_height = 0.1
        else:
            segment_height = 0.077

        if not window or not glass:
            print("Nie znaleziono obiektu ramki okna lub szyby.")
            return [], []

            # Ustawienie origin na środku obiektu okna i szyby
        bpy.context.view_layer.objects.active = window
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        bpy.context.view_layer.objects.active = glass
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        frame_objects = []  # Lista ramek
        glass_objects = []  # Lista szyb

        # --- 2. Obliczenia dla segmentów ---
        segment_count = max(1, int(height // segment_height))

        # Dolna krawędź bramy
        bottom_z = (height / 2)

        print(f"Liczba segmentów: {segment_count}, Wysokość segmentu: {segment_height}, Dolna krawędź Z: {bottom_z}")

        # --- 3. Dodanie okien do każdego segmentu (poza ostatnim) ---
        current_z = (segment_count - 6) * segment_height - segment_height / 2
        for i in range(3):
            # --- Tworzenie kopii ramki ---
            window_copy = window.copy()
            window_copy.data = window.data.copy()
            bpy.context.collection.objects.link(window_copy)

            # Ustawienie origin i zastosowanie transformacji
            bpy.context.view_layer.objects.active = window_copy

            # --- Skalowanie ramki ---
            original_width = window_copy.dimensions[0]
            original_height = window_copy.dimensions[2]

            scale_x = (width * 0.9) / original_width  # Skalowanie szerokości
            scale_z = (segment_height * 0.9) / original_height  # Skalowanie wysokości
            window_copy.scale[0] *= scale_x  # Ustaw skalę X
            window_copy.scale[2] *= scale_z  # Ustaw skalę Z


            # Pozycjonowanie ramki
            window_copy.location.x = gate_data["location"][0]  # Środek bramy w osi X
            window_copy.location.y = -0.01  # Nieznaczne odsunięcie w osi Y
            window_copy.location.z = current_z  # Pozycja Z (środek segmentu)

            frame_objects.append(window_copy)  # Dodaj ramkę do listy

            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)  # Zastosowanie skalowania
            # --- Tworzenie kopii szyby ---
            glass_copy = glass.copy()
            glass_copy.data = glass.data.copy()
            bpy.context.collection.objects.link(glass_copy)

            # Ustawienie origin i zastosowanie transformacji
            bpy.context.view_layer.objects.active = glass_copy
            # bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

            # --- Skalowanie szyby ---
            frame_width = window_copy.dimensions[0]
            frame_height = window_copy.dimensions[2]

            original_glass_width = glass_copy.dimensions[0]
            original_glass_height = glass_copy.dimensions[2]

            scale_x = (frame_width * 0.99) / original_glass_width  # Szyba o 95% szerokości ramki
            scale_z = (frame_height * 0.95) / original_glass_height  # Szyba o 95% wysokości ramki
            glass_copy.scale[0] *= scale_x  # Ustaw skalę X
            glass_copy.scale[2] *= scale_z  # Ustaw skalę Z

            # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)  # Zastosowanie skalowania

            # Pozycjonowanie szyby
            glass_copy.location.x = gate_data["location"][0]  # Środek bramy w osi X
            glass_copy.location.y = 0  # Odsunięcie względem okna w osi Y
            glass_copy.location.z = current_z  # Pozycja Z (środek segmentu)

            glass_objects.append(glass_copy)  # Dodaj szybę do listy

            # Przejście do kolejnego segmentu
            current_z += segment_height
        # --- 4. Zastosowanie transformacji do ramek ---
        for frame in frame_objects:
            bpy.context.view_layer.objects.active = frame
            frame.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # --- 5. Zastosowanie transformacji do szyb ---
        for glass in glass_objects:
            bpy.context.view_layer.objects.active = glass
            glass.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        print(f"Ramki i szyby zostały dodane. Liczba ramek: {len(frame_objects)}, Liczba szyb: {len(glass_objects)}")
        return frame_objects, glass_objects

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return [], []

def add_window_segment(glass, pattern, przetloczenie):
    """
    Dodaje segmenty okien do bramy na podstawie wzoru (pattern) i danych z JSON.

    Argumenty:
    pattern -- wzór układu okien (np. 1, 2, 3)
    glass -- obiekt szyby (bpy.types.Object)

    Zwraca:
    Tuple[List[bpy.types.Object], List[bpy.types.Object]] -- Lista ramek, lista szyb.
    """
    try:
        # --- 1. Wczytaj dane bramy z pliku JSON ---
        with open("../generator/dodatki/gate_data.json", "r") as json_file:
            gate_data = json.load(json_file)

        # Pobranie szerokości i wysokości bramy z JSON
        width = gate_data["dimensions"][0]
        height = gate_data["dimensions"][2]

        # --- 2. Wybór wzoru okien na podstawie patternu ---
        if pattern == "Wzór 1":
            windows = ["okno1", "okno1", "okno1"]
        elif pattern == "Wzór 2":
            windows = ["okno4", "okno4", "okno4"]
        elif pattern == "Wzór 3":
            windows = ["okno3", "okno4", "okno2"]
        else:
            print(f"Nieprawidłowy pattern: {pattern}")
            return [], []

        frame_objects = []  # Lista ramek
        glass_objects = []  # Lista szyb

        # --- 3. Obliczenia dla pozycji okien ---
        segment_height = 0.4001  # Wysokość pojedynczego segmentu
        segment_count_z = max(1, int(height // segment_height))
        if przetloczenie == "Kasetony":
            segment_height_per_unit = height / segment_count_z

        else:
            segment_height_per_unit = 0.4001

        if height >= 2.89:
            window_position = segment_count_z - 1  # Okno na przedostatnim segmencie
        else:
            window_position = 4  # Domyślna pozycja, gdy wysokość < 2.89m

        glass_z = segment_height_per_unit * window_position - segment_height_per_unit / 2
        glass_y = 0  # Głębokość (stała)

        # --- 4. Dodanie okien na lewą stronę ---
        window_left = bpy.data.objects.get(windows[0])
        if window_left:
            window_copy_left = window_left.copy()
            window_copy_left.data = window_left.data.copy()
            bpy.context.collection.objects.link(window_copy_left)

            glass_copy_left = glass.copy()
            glass_copy_left.data = glass.data.copy()
            bpy.context.collection.objects.link(glass_copy_left)

            glass_x = -(width / 2) + 0.10 + 0.93 / 2  # Lewa strona
            window_copy_left.location = (glass_x, glass_y, glass_z)
            glass_copy_left.location = (glass_x, glass_y, glass_z)

            frame_objects.append(window_copy_left)
            glass_objects.append(glass_copy_left)

        # --- 5. Dodanie okien na prawą stronę ---
        window_right = bpy.data.objects.get(windows[2])
        if window_right:
            window_copy_right = window_right.copy()
            window_copy_right.data = window_right.data.copy()
            bpy.context.collection.objects.link(window_copy_right)

            glass_copy_right = glass.copy()
            glass_copy_right.data = glass.data.copy()
            bpy.context.collection.objects.link(glass_copy_right)

            glass_x = (width / 2) - 0.10 - 0.93 / 2  # Prawa strona
            window_copy_right.location = (glass_x, glass_y, glass_z)
            glass_copy_right.location = (glass_x, glass_y, glass_z)

            frame_objects.append(window_copy_right)
            glass_objects.append(glass_copy_right)

        # --- 6. Dodanie środkowego okna (jeśli szerokość na to pozwala) ---
        if width >= 2.46:
            window_center = bpy.data.objects.get(windows[1])
            if window_center:
                window_copy_center = window_center.copy()
                window_copy_center.data = window_center.data.copy()
                bpy.context.collection.objects.link(window_copy_center)

                glass_copy_center = glass.copy()
                glass_copy_center.data = glass.data.copy()
                bpy.context.collection.objects.link(glass_copy_center)

                window_copy_center.location = (0, glass_y, glass_z)  # Środek
                glass_copy_center.location = (0, glass_y, glass_z)  # Środek

                frame_objects.append(window_copy_center)
                glass_objects.append(glass_copy_center)

        # --- 7. Zastosowanie transformacji do ramek ---
        for frame in frame_objects:
            bpy.context.view_layer.objects.active = frame
            frame.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # --- 8. Zastosowanie transformacji do szyb ---
        for glass in glass_objects:
            bpy.context.view_layer.objects.active = glass
            glass.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return frame_objects, glass_objects

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return [], []

def add_window_rotation(window, glass, option, ilosc_skrzydel):
    try:
        if not window or not glass:
            print("Nie znaleziono obiektu ramki okna lub szyby.")
            return None, None

        # Wczytaj dane bramy
        with open("../generator/dodatki/gate_data.json", "r") as json_file:
            gate_data = json.load(json_file)

        gate_location = gate_data["location"]
        gate_dimensions = gate_data["dimensions"]
        gate_width = gate_dimensions[0]
        gate_height = gate_dimensions[2]

        frame_objects = []
        glass_objects = []

        # Obliczenia pozycji
        gate_left_edge_x = gate_location[0] - (gate_width / 2)
        gate_right_edge_x = gate_location[0] + (gate_width / 2)
        gate_bottom_z = gate_location[2] - (gate_height / 2)
        window_z = gate_bottom_z + 1.7 if gate_height < 2.6 else gate_bottom_z + (gate_height / 2)

        window_positions = [
            ("Left", gate_left_edge_x + 0.1 + 0.93 / 2),
            ("Right", gate_right_edge_x - 0.1 - 0.93 / 2),
        ]

        # Tworzenie kopii ramek i szyb
        for side, x_pos in window_positions:
            window_copy = window.copy()
            window_copy.data = window.data.copy()
            bpy.context.collection.objects.link(window_copy)
            window_copy.location = (x_pos, gate_location[1], window_z)
            frame_objects.append(window_copy)

            glass_copy = glass.copy()
            glass_copy.data = glass.data.copy()
            bpy.context.collection.objects.link(glass_copy)
            glass_copy.location = (x_pos, gate_location[1], window_z)
            glass_objects.append(glass_copy)

        if ilosc_skrzydel == "Jednoskrzydłowe lewe":
            pivot_x = gate_left_edge_x
            rotation_angle = -math.radians(10)
        elif ilosc_skrzydel == "Jednoskrzydłowe prawe":
            pivot_x = gate_right_edge_x
            rotation_angle = math.radians(10)
        else:
            pivot_x_left = gate_left_edge_x
            pivot_x_right = gate_right_edge_x
            rotation_angle_left = -math.radians(5)
            rotation_angle_right = math.radians(10)

        for i, (window_copy, glass_copy) in enumerate(zip(frame_objects, glass_objects)):
            if ilosc_skrzydel == "Dwuskrzydłowe":
                if i == 0:  # Left
                    pivot_x = pivot_x_left
                    rotation_angle = rotation_angle_left
                else:  # Right
                    pivot_x = pivot_x_right
                    rotation_angle = rotation_angle_right

            pivot = (pivot_x, gate_location[1], gate_location[2])

            for obj in [window_copy, glass_copy]:
                # Dodanie obrotu w osi Y dla opcji "Pionowe"
                if option == "Okna pionowe":
                    obj.rotation_euler[1] += math.radians(90)
                bpy.context.scene.cursor.location = pivot
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


                # Rotacja w osi Z
                obj.rotation_euler[2] += rotation_angle

                # Korekta pozycji Y - dynamiczna
                distance = abs(obj.location[0] - pivot_x)
                if ilosc_skrzydel == "Jednoskrzydłowe lewe":
                    offset_y = distance * (1 - math.cos(rotation_angle)) + gate_width / 12.3
                    obj.location[1] -= offset_y
                elif ilosc_skrzydel == "Jednoskrzydłowe prawe":
                    offset_y = distance * (1 - math.cos(rotation_angle)) + gate_width / 12.3
                    obj.location[1] -= offset_y
                elif ilosc_skrzydel == "Dwuskrzydłowe":
                    if i == 0:  # Left
                        offset_y = distance * (1 - math.cos(rotation_angle_left)) + gate_width / 23.5
                        obj.location[1] -= offset_y
                    else:  # Right
                        offset_y = distance * (1 - math.cos(rotation_angle_right)) + gate_width / 12.3
                        obj.location[1] -= offset_y

            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return frame_objects, glass_objects

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None, None

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

        return frame_objects, glass_objects

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None, None

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
            handle_x = door_left_edge_x - 0.40 + (door_handle_copy.dimensions[0] / 2)  # 10 cm od lewej krawędzi drzwi
            handle_y = door.location[1] - 0.03  # Taka sama pozycja w osi Y co drzwi
            handle_z = door.location[2] - (door.dimensions[2] / 2) + 0.9  # 90 cm od dolnej krawędzi drzwi

            # Ustawienie pozycji klamki dla drzwi
            door_handle_copy.location = (handle_x, handle_y, handle_z)
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
            vent_x = -gate_dimensions[0] / 2 + 0.1 + 0.93/2
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
            vent_x = gate_dimensions[0] / 2 - 0.1 - 0.93/2
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

        return merged_vent

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None

def add_vent_rotation(vent, option, ilosc_skrzydel):
    """
    Tworzy kopię kratki wentylacyjnej i ustawia ją w odpowiednim miejscu na bramie rozwieranej,
    z uwzględnieniem obrotu względem tylnej krawędzi bramy. Wszystkie kratki są łączone w jeden obiekt.

    Argumenty:
    vent -- obiekt kratki wentylacyjnej (bpy.types.Object)
    option -- str, opcja "Lewa", "Prawa" lub "Obustronna"
    ilosc_skrzydel -- str, liczba skrzydeł: "Jednoskrzydłowe lewe", "Jednoskrzydłowe prawe", "Dwuskrzydłowe"

    Zwraca:
    bpy.types.Object -- Połączony obiekt kratki wentylacyjnej
    """
    try:
        if not vent:
            print("Nie znaleziono obiektu kratki wentylacyjnej.")
            return None

        # Wczytaj dane bramy
        with open("../generator/dodatki/gate_data.json", "r") as json_file:
            gate_data = json.load(json_file)

        gate_location = gate_data["location"]
        gate_dimensions = gate_data["dimensions"]
        gate_width = gate_dimensions[0]
        gate_height = gate_dimensions[2]

        vent_copies = []

        # Pozycje X i Z dla lewej i prawej kratki
        gate_left_edge_x = gate_location[0] - (gate_width / 2)
        gate_right_edge_x = gate_location[0] + (gate_width / 2)
        gate_bottom_z = gate_location[2] - (gate_height / 2)
        vent_z = gate_bottom_z + 0.2  # Stała wysokość nad dolną krawędzią bramy

        positions = []
        if option in ["Lewa", "Obustronna"]:
            positions.append(("Left", gate_left_edge_x + 0.1 + 0.93 / 2))
        if option in ["Prawa", "Obustronna"]:
            positions.append(("Right", gate_right_edge_x - 0.1 - 0.93 / 2))

        # Wybór punktu obrotu
        if ilosc_skrzydel == "Jednoskrzydłowe lewe":
            pivot_x = gate_left_edge_x
            rotation_angle = -math.radians(10)
        elif ilosc_skrzydel == "Jednoskrzydłowe prawe":
            pivot_x = gate_right_edge_x
            rotation_angle = math.radians(10)
        else:  # Dwuskrzydłowe
            pivot_x_left = gate_left_edge_x
            pivot_x_right = gate_right_edge_x
            rotation_angle_left = -math.radians(5)
            rotation_angle_right = math.radians(10)

        # Tworzenie kopii kratek
        for i, (side, x_pos) in enumerate(positions):
            vent_copy = vent.copy()
            vent_copy.data = vent.data.copy()
            bpy.context.collection.objects.link(vent_copy)
            vent_copy.location = (x_pos, gate_location[1], vent_z)

            # Obrót kratki względem odpowiedniego punktu
            if ilosc_skrzydel == "Dwuskrzydłowe":
                pivot_x = pivot_x_left if side == "Left" else pivot_x_right
                rotation_angle = rotation_angle_left if side == "Left" else rotation_angle_right
            elif ilosc_skrzydel == "Jednoskrzydłowe lewe" or ilosc_skrzydel == "Jednoskrzydłowe prawe":
                # Dla jednoskrzydłowych używamy tego samego pivot_x i kąta dla obu stron
                rotation_angle = -math.radians(10) if ilosc_skrzydel == "Jednoskrzydłowe lewe" else math.radians(10)

            pivot = (pivot_x, gate_location[1], gate_location[2])
            bpy.context.scene.cursor.location = pivot
            bpy.context.view_layer.objects.active = vent_copy
            vent_copy.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            vent_copy.rotation_euler[2] += rotation_angle

            # Korekta pozycji Y
            distance = abs(vent_copy.location[0] - pivot_x)
            offset_y = distance * (1 - math.cos(rotation_angle))
            vent_copy.location[1] -= offset_y

            # Zastosowanie transformacji
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            vent_copies.append(vent_copy)

        # Łączenie wszystkich kratek w jeden obiekt
        if vent_copies:
            bpy.context.view_layer.objects.active = vent_copies[0]
            for vent_copy in vent_copies:
                vent_copy.select_set(True)
            bpy.ops.object.join()
            merged_vent = bpy.context.view_layer.objects.active
            merged_vent.name = "vent_combined"
            return merged_vent
        else:
            print("Nie utworzono żadnych kopii kratki wentylacyjnej.")
            return None

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
            handle_door_copy = add_handle(handle, door=door_copy)
            if handle_door_copy:
                handle_door_copy.name = "klamka_do_drzwi"
                objects_to_export.append(handle_door_copy)

    # Kratka wentylacyjna
    if 'kratka' in dodatki:
        if dodatki["typ"] == "Brama Rozwierana" and dodatki["ilosc_skrzydel"] != "START":
            vent_copy = add_vent_rotation(vent,dodatki["kratka"], dodatki["ilosc_skrzydel"])
        else:
            vent_copy = position_vent_from_file(vent, dodatki["kratka"])
        if vent_copy:
            vent_copy.name = "kratka_wentylacyjna"
            objects_to_export.append(vent_copy)

    if 'klamka' in dodatki:
        handle_copy = add_handle(handle, dodatki["klamka"])
        if handle_copy:
            objects_to_export.append(handle_copy)

    if dodatki["typ"] == "Brama Segmentowa":
        if 'okno' in dodatki:
            window_copies, glass_copies = add_window_segment(glass, dodatki["okno"], dodatki["przetloczenie"])
            if window_copies:
                for idx, frame in enumerate(window_copies, start=1):
                    frame.name = f"ramka_okna_{idx}"
                    objects_to_export.append(frame)
            if glass_copies:
                for idx, glass2 in enumerate(glass_copies, start=1):
                    glass2.name = f"szyba_okna_{idx}"
                    objects_to_export.append(glass2)
    elif dodatki["typ"] == "Brama Roletowa":
        if 'okno' in dodatki:
            window2 = bpy.data.objects.get("okno-roletowev2")
            window_copies, glass_copies = add_window_rolling(window2, glass, dodatki["segment"])
            if window_copies:
                for idx, frame in enumerate(window_copies, start=1):
                    frame.name = f"ramka_okna_{idx}"
                    objects_to_export.append(frame)
            if glass_copies:
                for idx, glass2 in enumerate(glass_copies, start=1):
                    glass2.name = f"szyba_okna_{idx}"
                    objects_to_export.append(glass2)
    elif dodatki["typ"] == "Brama Rozwierana":
        if 'okno' in dodatki:
            if dodatki["ilosc_skrzydel"]=="START":
                window_copies, glass_copies = add_window(window, glass, dodatki["okno"])
            else:
                window_copies, glass_copies = add_window_rotation(window, glass, dodatki["okno"], dodatki["ilosc_skrzydel"])
            if window_copies:
                for idx, frame in enumerate(window_copies, start=1):
                    frame.name = f"ramka_okna_{idx}"
                    objects_to_export.append(frame)
            if glass_copies:
                for idx, glass2 in enumerate(glass_copies, start=1):
                    glass2.name = f"szyba_okna_{idx}"
                    objects_to_export.append(glass2)
    else:
        if 'okno' in dodatki:
            window_copies, glass_copies = add_window(window, glass, dodatki["okno"])
            if window_copies:
                for idx, frame in enumerate(window_copies, start=1):
                    frame.name = f"ramka_okna_{idx}"
                    objects_to_export.append(frame)
            if glass_copies:
                for idx, glass2 in enumerate(glass_copies, start=1):
                    glass2.name = f"szyba_okna_{idx}"
                    objects_to_export.append(glass2)

    # Eksportuj tylko jeśli mamy jakieś obiekty do eksportu
    if objects_to_export:
        export_multiple_objects_to_obj_custom(objects_to_export, output_path)
    else:
        print("Brak obiektów do eksportu.")

import json

def read_json(json_path):
    result = {}

    with open(json_path, 'r', encoding='utf-8') as file:
        existing_data = json.load(file)

        if "Typ bramy" in existing_data:
            result['typ'] = existing_data["Typ bramy"]
            if result["typ"] == "Brama Roletowa":
                if "Wysokość profili" in existing_data:
                    result["segment"] = existing_data["Wysokość profili"]
                else:
                    result["segment"] = None
            elif result["typ"] == "Brama Segmentowa":
                if "Rodzaj przetłoczenia" in existing_data:
                    result["przetloczenie"] = existing_data['Rodzaj przetłoczenia']
                else:
                    result["przetloczenie"] = "Bez przetłoczeia"
            elif result["typ"] == "Brama Rozwierana":
                if "Ilość skrzydeł" in existing_data:
                    result["ilosc_skrzydel"] = existing_data["Ilość skrzydeł"]
                else:
                    result["ilosc_skrzydel"] = "START"

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
print()
export_selected_objects(dodatki)