"""Step 1: Scene setup — clear, Cycles GPU, dark background, three-point cinematic lighting."""
import bpy
import math

# ─── Clear scene (DO NOT use factory_settings — kills MCP server) ───
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Also clear orphan data
for block in bpy.data.meshes:
    bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    bpy.data.materials.remove(block)
for block in bpy.data.lights:
    bpy.data.lights.remove(block)
for block in bpy.data.cameras:
    bpy.data.cameras.remove(block)

# ─── Render engine: Cycles GPU ───
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = False

# GPU rendering (Metal on macOS)
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.get_devices()
for device in prefs.devices:
    device.use = True
scene.cycles.device = 'GPU'

# ─── Dark background #0a0a0a = (10/255, 10/255, 10/255) ≈ (0.039, 0.039, 0.039) ───
# But we need linear color space: sRGB 0.039 → linear ≈ 0.003
world = bpy.data.worlds.get("World")
if world is None:
    world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
tree = world.node_tree
tree.nodes.clear()

bg_node = tree.nodes.new('ShaderNodeBackground')
bg_node.inputs['Color'].default_value = (0.003, 0.003, 0.003, 1.0)
bg_node.inputs['Strength'].default_value = 1.0

output_node = tree.nodes.new('ShaderNodeOutputWorld')
tree.links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

# ─── Camera (will be repositioned after molecule loads) ───
bpy.ops.object.camera_add(location=(0, -80, 30))
camera = bpy.context.active_object
camera.name = "Camera"
scene.camera = camera
# Set focal length for cinematic look
camera.data.lens = 85

# ─── Three-point cinematic lighting ───
# All lights track a central target empty
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
light_target = bpy.context.active_object
light_target.name = "LightTarget"

# KEY light — warm (slightly orange), upper right, strong
bpy.ops.object.light_add(type='AREA', location=(60, -50, 50))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 80000
key.data.size = 15
key.data.color = (1.0, 0.92, 0.82)  # Warm white
c = key.constraints.new(type='TRACK_TO')
c.target = light_target
c.track_axis = 'TRACK_NEGATIVE_Z'
c.up_axis = 'UP_Y'

# FILL light — cool (blue tint), from left, softer
bpy.ops.object.light_add(type='AREA', location=(-55, -35, 25))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 30000
fill.data.size = 20
fill.data.color = (0.78, 0.88, 1.0)  # Cool blue
c = fill.constraints.new(type='TRACK_TO')
c.target = light_target
c.track_axis = 'TRACK_NEGATIVE_Z'
c.up_axis = 'UP_Y'

# RIM light — subtle, from behind, defines silhouette
bpy.ops.object.light_add(type='AREA', location=(5, 65, 40))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 45000
rim.data.size = 10
rim.data.color = (0.9, 0.92, 1.0)  # Neutral cool
c = rim.constraints.new(type='TRACK_TO')
c.target = light_target
c.track_axis = 'TRACK_NEGATIVE_Z'
c.up_axis = 'UP_Y'

bpy.context.view_layer.update()
print("Scene setup complete: Cycles GPU, dark bg, 3-point lighting, camera ready")
