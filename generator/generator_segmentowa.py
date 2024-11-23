import bpy
import os
import math


def scale_stack_and_align_rails():
    # Nazwy obiektów
    segment_name = "Cube.002"
    rail_name = "szyny-na-brame"
    # Lista dostępnych segmentów
    available_segments = ["Cube", "Cube.001", "Cube.002"]

    # Wyświetlenie dostępnych segmentów
    print("Dostępne segmenty:")
    for i, segment_name in enumerate(available_segments):
        print(f"{i + 1}. {segment_name}")
    # Pobranie wyboru użytkownika
    try:
        segment_choice = int(input("Wybierz numer segmentu (1, 2, 3): "))
        if segment_choice < 1 or segment_choice > len(available_segments):
            print("Nieprawidłowy wybór. Spróbuj ponownie.")
            return
        segment_name = available_segments[segment_choice - 1]
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
        x_length_cm = float(input("Podaj długość segmentu w osi X (w cm): "))
        x_length_m = x_length_cm / 100  # Konwersja cm na metry
        segment_count = int(input("Podaj liczbę segmentów w pionie: "))

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

        print(f"Dodano i dopasowano szyny do obiektu 'brama-segmentowa'.")

    except ValueError:
        print("Podano nieprawidłowe dane. Spróbuj ponownie.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


def add_cameras_and_render_with_light():
    # Pobierz obiekt bramy
    gate = bpy.data.objects.get("brama-segmentowa")
    if not gate:
        print("Obiekt 'brama-segmentowa' nie został znaleziony.")
        return

    # Pozycja bramy
    gate_location = gate.location

    # Ustawienia kamer
    camera_distance = 5  # Promień w metrach (większy promień)
    camera_height = 1  # Wysokość w osi Z
    num_cameras = 6  # Liczba kamer
    output_dir = os.path.join(bpy.path.abspath("//"), "renders")  # Folder na rendery

    # Usuń istniejące kamery i światła (opcjonalne)
    for obj in bpy.data.objects:
        if obj.type in {'CAMERA', 'LIGHT'}:
            bpy.data.objects.remove(obj)

    # Dodaj światło na -1m w osi Y
    bpy.ops.object.light_add(type='AREA', location=(gate_location.x, gate_location.y - 5, gate_location.z + 1))
    light = bpy.context.object
    light.data.energy = 200  # U
    light.data.size = 5  # Rozmiar światła

    # Tworzenie kamer
    cameras = []
    angle_offset = math.pi / num_cameras  # Pominięcie kamery na X=0
    for i in range(num_cameras):
        angle = (2 * math.pi / num_cameras) * i + angle_offset  # Przesunięcie kąta
        x = gate_location.x + camera_distance * math.cos(angle)
        y = gate_location.y + camera_distance * math.sin(angle)
        z = gate_location.z + camera_height

        # Dodaj kamerę
        bpy.ops.object.camera_add(location=(x, y, z))
        cam = bpy.context.object
        cam.name = f"Camera_{i + 1}"
        cameras.append(cam)

        # Skieruj kamerę na bramę
        cam_constraint = cam.constraints.new(type='TRACK_TO')
        cam_constraint.target = gate
        cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        cam_constraint.up_axis = 'UP_Y'

    # Tworzenie folderu na rendery, jeśli nie istnieje
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Renderuj scenę z każdej kamery
    for i, cam in enumerate(cameras):
        # Ustaw aktywną kamerę
        bpy.context.scene.camera = cam

        # Ustaw ścieżkę pliku wyjściowego
        bpy.context.scene.render.filepath = os.path.join(output_dir, f"Camera_{i + 1}.png")

        # Wykonaj render
        bpy.ops.render.render(write_still=True)

    print(f"Renderowanie zakończone. Pliki zapisano w folderze: {output_dir}")


# Uruchom funkcję
scale_stack_and_align_rails()
add_cameras_and_render_with_light()







