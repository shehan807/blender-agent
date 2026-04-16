"""Step 5b: Adjust framing, refine chain colors, and tune lighting."""
import bpy
import mathutils
import math

mol_obj = bpy.data.objects.get("8V00")
mesh = mol_obj.data

# ─── Recalculate molecule bounds ───
min_co = mathutils.Vector((float('inf'), float('inf'), float('inf')))
max_co = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))
for vert in mesh.vertices:
    co = mol_obj.matrix_world @ vert.co
    min_co.x = min(min_co.x, co.x)
    min_co.y = min(min_co.y, co.y)
    min_co.z = min(min_co.z, co.z)
    max_co.x = max(max_co.x, co.x)
    max_co.y = max(max_co.y, co.y)
    max_co.z = max(max_co.z, co.z)

center = (min_co + max_co) / 2
extent = max_co - min_co
max_dim = max(extent.x, extent.y, extent.z)
print(f"Molecule extent: {extent.x:.2f} x {extent.y:.2f} x {extent.z:.2f}")
print(f"Center: {center}")

# ─── Refine per-chain colors — make the three cool tones more distinct ───
chain_attr = mesh.attributes.get('chain_id')
color_attr = mesh.attributes.get('Color')

# More distinguished cool palette + warm accent
CHAIN_COLORS = {
    0: (0.035, 0.165, 0.420, 1.0),   # Steel Blue (deep, darker)
    1: (0.015, 0.310, 0.310, 1.0),   # Teal (rich mid-tone)
    2: (0.100, 0.580, 0.720, 1.0),   # Sky Cyan (lighter, brighter)
    3: (0.950, 0.400, 0.030, 1.0),   # Amber/Orange (warm accent)
}

for i in range(len(mesh.vertices)):
    cid = chain_attr.data[i].value
    color_attr.data[i].color = CHAIN_COLORS.get(cid, (0.5, 0.5, 0.5, 1.0))

print("Updated chain colors for better distinction")

# ─── Adjust camera for better framing ───
camera = bpy.data.objects.get("Camera")
pivot = bpy.data.objects.get("CameraOrbitPivot")

# Pull camera back more (2.8x max dimension for full molecule + padding)
cam_distance = max_dim * 2.8
camera.location = (0, -cam_distance, max_dim * 0.2)
camera.data.lens = 85  # Keep cinematic focal length

# Pivot at molecule center
pivot.location = center

# ─── Adjust lights for the actual scale ───
light_target = bpy.data.objects.get("LightTarget")
if light_target:
    light_target.location = center

d = max_dim * 1.5  # Light distance factor

key = bpy.data.objects.get("KeyLight")
if key:
    key.location = (center.x + d, center.y - d * 0.8, center.z + d * 0.8)
    key.data.energy = 3000  # Scale for small molecule
    key.data.size = d * 0.8

fill = bpy.data.objects.get("FillLight")
if fill:
    fill.location = (center.x - d * 0.9, center.y - d * 0.6, center.z + d * 0.3)
    fill.data.energy = 1200
    fill.data.size = d * 1.2

rim = bpy.data.objects.get("RimLight")
if rim:
    rim.location = (center.x + d * 0.1, center.y + d, center.z + d * 0.5)
    rim.data.energy = 1800
    rim.data.size = d * 0.5

bpy.context.view_layer.update()
bpy.context.scene.frame_set(1)
print("Framing, colors, and lighting adjusted")
