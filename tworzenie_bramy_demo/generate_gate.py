import subprocess
import os

def generate_render(width, height, depth, output_path):
    """
    Generuje sześcian 3D w Blenderze i renderuje go jako PNG z jasnym tłem oraz niebieskim kolorem.
    """
    # Ścieżka do Blendera
    blender_path = "C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"  # Upewnij się, że ta ścieżka jest poprawna

    # Skrypt do uruchomienia w Blenderze
    blender_script = f"""
import bpy

# Usuwanie wszystkich obiektów w scenie
bpy.ops.wm.read_factory_settings(use_empty=True)

# Tworzenie sześcianu na podstawie podanych wymiarów
width = {width}
height = {height}
depth = {depth}

# Dodanie sześcianu
bpy.ops.mesh.primitive_cube_add(location=(0, 0, height / 2))
cube = bpy.context.object
cube.scale = (width / 2, depth / 2, height / 2)

# Ustawienie niebieskiego koloru dla kostki
mat = bpy.data.materials.new(name="BlueMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)  # Niebieski kolor (RGBA)
cube.data.materials.append(mat)

# Ustawienie kamery (oddalonej)
camera_distance = max(width, height, depth) * 3  # Obliczenie odpowiedniej odległości
bpy.ops.object.camera_add(location=(camera_distance, -camera_distance, camera_distance))
camera = bpy.context.object
bpy.context.scene.camera = camera
camera.rotation_euler = (1.0, 0, 0.785)  # Ustawienie kąta kamery

# Dodanie światła
bpy.ops.object.light_add(type='SUN', location=(0, 0, height * 3))

# Ustawienie jasnego tła (światło środowiskowe)
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new(name="BrightBackground")

bpy.context.scene.world.use_nodes = True
bg_nodes = bpy.context.scene.world.node_tree.nodes
bg_links = bpy.context.scene.world.node_tree.links

# Pobranie węzła Background
if "Background" not in bg_nodes:
    background = bg_nodes.new(type="ShaderNodeBackground")
else:
    background = bg_nodes["Background"]

# Ustawienie białego tła
background.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)  # Jasne białe tło (RGBA)

# Połączenie Background z wyjściem
output = bg_nodes["World Output"]
bg_links.new(background.outputs[0], output.inputs[0])

# Ustawienie silnika renderowania
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64  # Ilość próbek renderowania

# Ścieżka do zapisu
bpy.context.scene.render.filepath = r"{output_path}"
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Renderowanie
bpy.ops.render.render(write_still=True)
    """

    # Zapis skryptu tymczasowego
    temp_script_path = "temp_blender_script.py"
    with open(temp_script_path, "w") as script_file:
        script_file.write(blender_script)

    # Wywołanie Blendera w trybie tła
    subprocess.run([blender_path, "--background", "--python", temp_script_path], check=True)

    # Usunięcie tymczasowego skryptu
    os.remove(temp_script_path)

if __name__ == "__main__":
    # Pobranie danych od użytkownika
    width = float(input("Podaj szerokość sześcianu (w metrach): "))
    height = float(input("Podaj wysokość sześcianu (w metrach): "))
    depth = float(input("Podaj głębokość sześcianu (w metrach): "))

    # Ścieżka do zapisu pliku PNG
    output_file = os.path.abspath("cube_render.png")

    print("Generowanie i renderowanie sześcianu z jasnym tłem i niebieskim kolorem...")
    generate_render(width, height, depth, output_file)

    print(f"Renderowanie zakończone. Obraz zapisano jako {output_file}.")
