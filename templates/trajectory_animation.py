"""
Template: Trajectory Animation

Adapt this template and send via execute_blender_code.
Loads a multi-model PDB (from convert_trajectory.py), sets up animation with
a rotating camera, and renders a PNG sequence.

After rendering, combine to video locally:
    ffmpeg -framerate 24 -i /path/to/frames/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 output.mp4

Parameters to customize:
- PDB_PATH: absolute path to multi-model PDB file
- OUTPUT_DIR: absolute path to directory for PNG sequence
- N_FRAMES: number of frames in the trajectory (from convert_trajectory.py output)
- RESOLUTION: output resolution
- SAMPLES: Cycles render samples (lower = faster for animation)
- STYLE: "ball_and_stick", "cartoon", "surface", "ribbon", "spheres"
- CAMERA_ORBIT: whether camera rotates around molecule
- BACKGROUND: "dark", "white", or "transparent"
"""

import bpy
import math
import bl_ext.blender_org.molecularnodes as mn

# === CUSTOMIZE THESE ===
PDB_PATH = "/absolute/path/to/trajectory.pdb"
OUTPUT_DIR = "/absolute/path/to/frames/"
N_FRAMES = 100
RESOLUTION = (1920, 1080)
SAMPLES = 64
STYLE = "ball_and_stick"
CAMERA_ORBIT = True
BACKGROUND = "dark"
# ========================

# --- Setup ---
canvas = mn.Canvas(mn.scene.Cycles(samples=SAMPLES), resolution=RESOLUTION)

# --- Load trajectory ---
mol = mn.Molecule.load(PDB_PATH)

# --- Apply style ---
style_map = {
    "ball_and_stick": mn.StyleBallAndStick(quality=4),
    "cartoon": mn.StyleCartoon(),
    "surface": mn.StyleSurface(),
    "ribbon": mn.StyleRibbon(),
    "spheres": mn.StyleSpheres(),
}
mol.add_style(
    style_map.get(STYLE, mn.StyleBallAndStick(quality=4)),
    material=mn.material.AmbientOcclusion()
)

bpy.context.view_layer.update()

# --- Frame range ---
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = N_FRAMES

# --- Frame molecule ---
mol_obj = bpy.data.objects.get(mol._object_name)
if mol_obj:
    canvas.frame_object(mol_obj)

# --- Background ---
if BACKGROUND == "transparent":
    scene.render.film_transparent = True
else:
    scene.render.film_transparent = False
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        if BACKGROUND == "dark":
            bg_node.inputs['Color'].default_value = (0.02, 0.02, 0.02, 1.0)
        elif BACKGROUND == "white":
            bg_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)

# --- Camera orbit ---
if CAMERA_ORBIT:
    camera = bpy.data.objects.get("Camera")
    if camera is None:
        # Canvas should have created one, find it
        for obj in bpy.data.objects:
            if obj.type == 'CAMERA':
                camera = obj
                break

    if camera:
        # Create orbit pivot at molecule center
        mol_center = mol_obj.location if mol_obj else (0, 0, 0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=mol_center)
        pivot = bpy.context.active_object
        pivot.name = "CameraOrbitPivot"

        camera.parent = pivot

        # Track molecule
        for c in camera.constraints:
            camera.constraints.remove(c)
        track = camera.constraints.new(type='TRACK_TO')
        track.target = pivot
        track.track_axis = 'TRACK_NEGATIVE_Z'
        track.up_axis = 'UP_Y'

        # Animate rotation
        scene.frame_set(scene.frame_start)
        pivot.rotation_euler = (0, 0, 0)
        pivot.keyframe_insert(data_path="rotation_euler", frame=scene.frame_start)

        scene.frame_set(scene.frame_end)
        pivot.rotation_euler = (0, 0, math.radians(360))
        pivot.keyframe_insert(data_path="rotation_euler", frame=scene.frame_end)

        # Linear interpolation for smooth rotation
        if pivot.animation_data and pivot.animation_data.action:
            for fcurve in pivot.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'LINEAR'

# --- GPU rendering ---
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = True
    scene.cycles.device = 'GPU'
except Exception:
    pass  # Fall back to CPU

# --- Denoising ---
scene.cycles.use_denoising = True

# --- Render settings ---
scene.render.filepath = OUTPUT_DIR
scene.render.image_settings.file_format = 'PNG'

# --- Render animation ---
bpy.ops.render.render(animation=True)
print(f"Animation rendered to {OUTPUT_DIR}")
