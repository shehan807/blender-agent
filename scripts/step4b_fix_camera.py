"""Step 4b: Fix camera positioning using actual atom positions."""
import bpy
import mathutils
import math

mol_obj = bpy.data.objects.get("8V00")
if not mol_obj:
    raise RuntimeError("Could not find molecule object '8V00'")

mesh = mol_obj.data

# Calculate extent from actual vertex positions
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

print(f"Atom positions - min: ({min_co.x:.1f}, {min_co.y:.1f}, {min_co.z:.1f})")
print(f"Atom positions - max: ({max_co.x:.1f}, {max_co.y:.1f}, {max_co.z:.1f})")
print(f"Center: ({center.x:.1f}, {center.y:.1f}, {center.z:.1f})")
print(f"Extent: ({extent.x:.1f}, {extent.y:.1f}, {extent.z:.1f})")
print(f"Max dimension: {max_dim:.1f}")

# ─── Reposition orbit pivot to molecule center ───
pivot = bpy.data.objects.get("CameraOrbitPivot")
if pivot:
    pivot.location = center
    print(f"Pivot moved to {center}")

# ─── Reposition camera at good framing distance ───
camera = bpy.data.objects.get("Camera")
if camera:
    # For 85mm lens at 1080p, distance ~2x max dimension gives good framing
    cam_distance = max_dim * 2.0
    # Place camera to the front-right, slightly elevated
    camera.location = (0, -cam_distance, max_dim * 0.25)
    print(f"Camera at distance {cam_distance:.1f}")

# ─── Move light target to molecule center ───
light_target = bpy.data.objects.get("LightTarget")
if light_target:
    light_target.location = center

# ─── Reposition lights relative to molecule center and size ───
scale = max_dim * 0.8

key = bpy.data.objects.get("KeyLight")
if key:
    key.location = (center.x + scale, center.y - scale * 0.8, center.z + scale * 0.8)

fill = bpy.data.objects.get("FillLight")
if fill:
    fill.location = (center.x - scale * 0.9, center.y - scale * 0.6, center.z + scale * 0.4)

rim = bpy.data.objects.get("RimLight")
if rim:
    rim.location = (center.x + scale * 0.1, center.y + scale, center.z + scale * 0.6)

bpy.context.view_layer.update()
bpy.context.scene.frame_set(1)
print("Camera and lights repositioned to molecule extent")
