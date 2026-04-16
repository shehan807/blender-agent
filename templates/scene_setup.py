"""
Template: Clean Scene Setup

Adapt this template and send via execute_blender_code.
Sets up a clean scene with camera, lights, and Cycles renderer.

Parameters to customize:
- RESOLUTION: output resolution (width, height)
- SAMPLES: Cycles render samples
- BACKGROUND: "dark", "white", or "transparent"
- USE_GPU: enable GPU rendering
"""

import bpy
import math

# === CUSTOMIZE THESE ===
RESOLUTION = (1920, 1080)
SAMPLES = 128
BACKGROUND = "dark"  # "dark", "white", "transparent"
USE_GPU = True
# ========================

# Clear the scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# --- Renderer ---
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.render.resolution_x = RESOLUTION[0]
scene.render.resolution_y = RESOLUTION[1]

# GPU rendering
if USE_GPU:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'  # Change to 'CUDA' or 'OPTIX' for NVIDIA
    prefs.get_devices()
    for device in prefs.devices:
        device.use = True
    scene.cycles.device = 'GPU'

# --- Background ---
if BACKGROUND == "transparent":
    scene.render.film_transparent = True
else:
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if BACKGROUND == "dark":
        bg_node.inputs['Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    elif BACKGROUND == "white":
        bg_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)

# --- Camera ---
bpy.ops.object.camera_add(location=(8, -8, 5))
camera = bpy.context.active_object
camera.name = "Camera"
scene.camera = camera

# Point camera at origin
constraint = camera.constraints.new(type='TRACK_TO')
empty = bpy.data.objects.new("CameraTarget", None)
bpy.context.collection.objects.link(empty)
empty.location = (0, 0, 0)
constraint.target = empty
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# --- Three-Point Lighting ---
# Key light
bpy.ops.object.light_add(type='AREA', location=(7, -5, 8))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 1000
key.data.size = 5

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-6, -4, 4))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 400
fill.data.size = 8

# Rim light
bpy.ops.object.light_add(type='AREA', location=(0, 8, 6))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 600
rim.data.size = 3

# Point lights at origin
for light_name in ["KeyLight", "FillLight", "RimLight"]:
    light_obj = bpy.data.objects.get(light_name)
    c = light_obj.constraints.new(type='TRACK_TO')
    c.target = empty
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'

bpy.context.view_layer.update()
print("Scene setup complete")
