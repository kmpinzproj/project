import bpy
import os
import math
import mathutils
import bmesh
from mathutils import Vector
from math import radians

# Lista nazw obiektów do sprawdzenia i ewentualnego usunięcia
object_names = ["szyny", "szyny-na-brame.001", "brama-uchylna-z-szynami", "Right_Door", "Left_Door", "brama-uchylna"]

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

def tilt_gate():
    # Nazwa segmentu bazowego
    segment_name = "Cube.003"
    
   

    
    # Wybór segmentu
    try:
        segment_choice = int(input("Wybierz numer segmentu (1 lewo, 2 prawo, 3 podwójne): "))
        if segment_choice < 1 or segment_choice > 3:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")
            return
        print(f"-----------------dokonany wybór {segment_choice}")
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
        segment_height = segment.dimensions[2]

        # Tworzenie segmentów w osi X lub jodła
        
        
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
                plane_co=(-(segment_width/2)+remaining_width, 0, 0),
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
                plane_co=(0, 0, -(segment_height/2)+remaining_height),  # Płaszczyzna cięcia w osi Z
                plane_no=(0, 0, 1),  # Normalna osi Z (cięcie w pionie)
                clear_outer=True  # Usuń górną część
            )
            bmesh.ops.contextual_create(bm, geom=result['geom'])
            bm.to_mesh(last_segment_z.data)
            bm.free()
            bpy.context.view_layer.objects.active = last_segment_z
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            if joined_segments:  # Jeśli istnieją inne segmenty
                last_segment_z.location.z = joined_segments[-1].location.z + (joined_segments[-1].dimensions[2] / 2) + (remaining_height / 2)
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
        print(f"joined: {joined_gate}")
        
        joined_gate.location.x = 0
        joined_gate.location.y = 0
        add_and_align_rails(joined_gate)
        if segment_choice == 3: #----------------------------------------------------- tu masz na podwójną warunek
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
                plane_no=(1, 0, 0),       # Normalna płaszczyzny cięcia (w kierunku dodatniego X)
                clear_outer=True          # Usuń wszystko na prawo od płaszczyzny
            )

            # Przycinamy prawą część (usuń lewą stronę)
            cut_object(
                right_door,
                plane_co=(0, 0, 0),  # Płaszczyzna cięcia na połowie wymiaru X
                plane_no=(-1, 0, 0),      # Normalna płaszczyzny cięcia (w kierunku ujemnego X)
                clear_outer=True          # Usuń wszystko na lewo od płaszczyzny
            )

            # Nadajemy nazwy
            left_door.name = "Left_Door"
            # Pobierz bounding box obiektu w przestrzeni lokalnej---------------------------------------------------------------
            # Pobierz bounding box obiektu w przestrzeni lokalnej
            dimensions = left_door.dimensions
            bounding_box = [left_door.matrix_world @ Vector(corner) for corner in left_door.bound_box]

            # Znajdź prawą, pionową krawędź z tyłu
            # Maksymalna wartość X (prawo) i maksymalna wartość Y (tył)
            right_back_x = min(v.x for v in bounding_box)  # Maksymalny X
            right_back_y = max(v.y for v in bounding_box)  # Maksymalny Y
            right_back_z = left_door.dimensions[2]/2  # Połowa wysokości Z

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
            #przesuwam pivot prawych drzwi------------------------------------------------------------------------------------------
            # Pobierz bounding box obiektu w przestrzeni lokalnej
            dimensions = right_door.dimensions
            bounding_box = [right_door.matrix_world @ Vector(corner) for corner in right_door.bound_box]

            # Znajdź prawą, pionową krawędź z tyłu
            # Maksymalna wartość X (prawo) i maksymalna wartość Y (tył)
            right_back_x = max(v.x for v in bounding_box)  # Maksymalny X
            right_back_y = max(v.y for v in bounding_box)  # Maksymalny Y
            right_back_z = joined_gate.dimensions[2]/2  # Połowa wysokości Z

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
        else:
            # Przesuwam pivot
            print(bpy.context.view_layer.objects.active)
            
            # Pobierz bounding box obiektu w przestrzeni lokalnej
            dimensions = joined_gate.dimensions
            bounding_box = [joined_gate.matrix_world @ Vector(corner) for corner in joined_gate.bound_box]

            # Znajdź prawą, pionową krawędź z tyłu
            # Maksymalna wartość X (prawo) i maksymalna wartość Y (tył)
            if segment_choice == 1: #--------------------------------------------------------jeśli lewo stronnna
                right_back_x = min(v.x for v in bounding_box)  # Maksymalny X
            elif segment_choice == 2: #--------------------------------------------------------jeśli prawo stronnna
                right_back_x = max(v.x for v in bounding_box)  # Maksymalny X
            right_back_y = max(v.y for v in bounding_box)  # Maksymalny Y
            right_back_z = joined_gate.dimensions[2]/2  # Połowa wysokości Z

            # Utwórz współrzędne punktu
            right_back_corner = Vector((right_back_x, right_back_y, right_back_z))

            # Przenieś 3D Cursor na obliczoną pozycję
            bpy.context.scene.cursor.location = right_back_corner

            # Zaznacz obiekt i ustaw origin
            bpy.ops.object.select_all(action='DESELECT')  # Odznacz wszystkie obiekty
            joined_gate.select_set(True)  # Zaznacz tylko obiekt joined_gate
            bpy.context.view_layer.objects.active = joined_gate  # Ustaw go jako aktywny
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')  # Ustaw origin na kursorze
            if segment_choice == 1: #--------------------------------------------------------jeśli lewo stronnna
                joined_gate.rotation_euler[2] -= radians(10) 
            elif segment_choice == 2: #--------------------------------------------------------jeśli prawo stronnna
                joined_gate.rotation_euler[2] += radians(10) 
        
        
                    
        

        


        

        print(f"Stworzono bramę o wymiarach: {x_length_m}m x {z_height_m}m.")

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









