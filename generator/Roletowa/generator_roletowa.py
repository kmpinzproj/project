import bpy
import os
import math

import bmesh

# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["brama-segmentowa", "szyny-na-brame.001", "brama-segmentowa-z-szynami", "brama-uchylna-z-szynami", "brama-roletowa","szyny"]

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
    available_segments = ["seg1", "seg2"]

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

    try:
        # Pobranie wymiarów bramy od użytkownika
        x_length_cm = float(input("Podaj szerokość bramy w osi X (w cm): "))
        z_height_cm = float(input("Podaj wysokość bramy w osi Z (w cm): "))
        x_length_m = x_length_cm / 100  # Konwersja cm na metry
        z_height_m = z_height_cm / 100  # Konwersja cm na metry

        # Wymiary segmentu
        segment_width = segment.dimensions[0]
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
        print(f"pozostała długość : {remaining_height} , z_height_m {z_height_m}, current_z{current_z}")
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
        joined_gate.name = "brama-roletowa"  # Zmień nazwę obiektu
        bpy.context.view_layer.objects.active = joined_gate
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        # Informacje końcowe
        print(f"Stworzono bramę o wymiarach: {x_length_m} m (X) x {z_height_m} m (Z).")
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

        rail_copy.scale[0] = scale_x  # Dopasowanie szerokości
        rail_copy.scale[2] = scale_z  # Dopasowanie wysokości

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

        print(f"Dodano i dopasowano szyny do obiektu '{gate.name}'.")

        

        final_gate = bpy.context.view_layer.objects.active
        final_gate.name = "szyny"

        print("Połączono bramę i szyny w jeden obiekt.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


# Uruchom funkcję
tilt_gate()

    
#add_cameras_and_render_with_light()







