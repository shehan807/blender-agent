"""
Template: Ball-and-Stick Molecular Render

Adapt this template and send via execute_blender_code.
Loads a PDB file, applies ball-and-stick style with CPK colors, renders to PNG.

Parameters to customize:
- PDB_PATH: absolute path to PDB file
- OUTPUT_PATH: absolute path for output PNG
- RESOLUTION: output resolution
- SAMPLES: Cycles render samples
- SPHERE_QUALITY: sphere smoothness (2=fast, 6=smooth)
- ROTATION: optional (angle_degrees, axis_index) e.g. (80, 0) for 80 deg around X
- USE_OUTLINES: enable Freestyle silhouette outlines
- TRANSPARENT_BG: transparent background for compositing
"""

import bpy
import math
import bl_ext.blender_org.molecularnodes as mn

# === CUSTOMIZE THESE ===
PDB_PATH = "/absolute/path/to/molecule.pdb"
OUTPUT_PATH = "/absolute/path/to/output.png"
RESOLUTION = (2000, 2000)
SAMPLES = 128
SPHERE_QUALITY = 6
ROTATION = None  # e.g. (80, 0) for 80 deg around X axis
USE_OUTLINES = True
TRANSPARENT_BG = True
# ========================


def fix_element_colors(mol):
    """Fix element colors to standard CPK scheme."""
    tree = mol.node_group

    # Remove random carbon color
    links_to_remove = []
    for link in tree.links:
        if (link.from_node.name == 'Color Attribute Random' and
            link.to_node.name == 'Color Common' and
            link.to_socket.name == 'Carbon'):
            links_to_remove.append(link)
    for link in links_to_remove:
        tree.links.remove(link)

    # Set CPK colors
    cpk_colors = {
        'Carbon': (0.28, 0.28, 0.28, 1.0),
        'Phosphorous': (1.0, 0.216, 0.0, 1.0),
    }
    for node in tree.nodes:
        if node.name == 'Color Common':
            for element, color in cpk_colors.items():
                inp = node.inputs.get(element)
                if inp:
                    inp.default_value = color

    # Fix Boron
    mol_obj = bpy.data.objects.get(mol._object_name)
    if mol_obj and mol_obj.data:
        atomic_num_attr = mol_obj.data.attributes.get('atomic_number')
        color_attr = mol_obj.data.attributes.get('Color')
        if atomic_num_attr and color_attr:
            boron_pink = (1.0, 0.462, 0.462, 1.0)
            for i, atom_num in enumerate(atomic_num_attr.data):
                if atom_num.value == 5:
                    color_attr.data[i].color = boron_pink


# --- Setup ---
canvas = mn.Canvas(mn.scene.Cycles(samples=SAMPLES), resolution=RESOLUTION)

# --- Load molecule ---
mol = mn.Molecule.load(PDB_PATH)
mol.add_style(
    mn.StyleBallAndStick(quality=SPHERE_QUALITY),
    material=mn.material.AmbientOcclusion()
)

# --- Fix colors ---
fix_element_colors(mol)

# --- Scene update ---
bpy.context.view_layer.update()

# --- Rotation (optional) ---
mol_obj = bpy.data.objects.get(mol._object_name)
if ROTATION and mol_obj:
    angle_deg, axis_idx = ROTATION
    mol_obj.rotation_euler[axis_idx] = math.radians(angle_deg)
    bpy.context.view_layer.update()

# --- Frame molecule ---
if mol_obj:
    canvas.frame_object(mol_obj)

# --- Background ---
bpy.context.scene.render.film_transparent = TRANSPARENT_BG

# --- Outlines ---
if USE_OUTLINES:
    bpy.context.scene.render.use_freestyle = True
    bpy.context.view_layer.use_freestyle = True
    freestyle = bpy.context.view_layer.freestyle_settings
    if freestyle.linesets:
        lineset = freestyle.linesets[0]
        lineset.select_silhouette = True
        lineset.select_border = True
        lineset.select_crease = False
        lineset.select_edge_mark = False
        lineset.linestyle.color = (0, 0, 0)
        lineset.linestyle.thickness = 1.5

# --- Render ---
canvas.snapshot(OUTPUT_PATH)
print(f"Rendered: {OUTPUT_PATH}")
