"""Step 4: Camera orbit (360°, 480 frames at 24fps = 20s) + depth of field."""
import bpy
import math
import mathutils

# ─── Get molecule object ───
mol_obj = bpy.data.objects.get("8V00")
if not mol_obj:
    raise RuntimeError("Could not find molecule object '8V00'")

# Calculate molecule bounding box center and size
depsgraph = bpy.context.evaluated_depsgraph_get()
eval_obj = mol_obj.evaluated_get(depsgraph)

# Get world-space bounding box
bbox_corners = [mol_obj.matrix_world @ mathutils.Vector(corner) for corner in eval_obj.bound_box]
center = sum(bbox_corners, mathutils.Vector((0, 0, 0))) / 8
dimensions = eval_obj.dimensions
max_dim = max(dimensions)

print(f"Molecule center: {center}")
print(f"Dimensions: {dimensions}")
print(f"Max dimension: {max_dim}")

# ─── Frame range: 480 frames (20s at 24fps) ───
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 480
scene.frame_current = 1
scene.render.fps = 24

# ─── Create orbit pivot at molecule center ───
bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
pivot = bpy.context.active_object
pivot.name = "CameraOrbitPivot"

# ─── Position camera ───
camera = bpy.data.objects.get("Camera")
if not camera:
    raise RuntimeError("Camera not found")

# Set camera distance based on molecule size (1.8x max dimension for nice framing)
cam_distance = max_dim * 1.8
camera.location = (center.x, center.y - cam_distance, center.z + max_dim * 0.3)
camera.parent = pivot

# Track the pivot (molecule center)
for c in camera.constraints:
    camera.constraints.remove(c)
track = camera.constraints.new(type='TRACK_TO')
track.target = pivot
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# ─── Depth of field: f/2.8 focused on molecule center ───
camera.data.dof.use_dof = True
camera.data.dof.focus_object = pivot  # Focus on the center empty
camera.data.dof.aperture_fstop = 2.8

# ─── Animate 360° rotation ───
scene.frame_set(1)
pivot.rotation_euler = (0, 0, 0)
pivot.keyframe_insert(data_path="rotation_euler", frame=1)

scene.frame_set(480)
pivot.rotation_euler = (0, 0, math.radians(360))
pivot.keyframe_insert(data_path="rotation_euler", frame=480)

# Set linear interpolation for smooth continuous rotation
action = pivot.animation_data.action
try:
    # Blender 5.0+ (layered actions)
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fcurve in cb.fcurves:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'LINEAR'
    print("Set linear interpolation (Blender 5.0+ layered API)")
except AttributeError:
    # Blender 4.x (legacy)
    for fcurve in action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
    print("Set linear interpolation (Blender 4.x API)")

# ─── Move light target to molecule center ───
light_target = bpy.data.objects.get("LightTarget")
if light_target:
    light_target.location = center

# ─── Render output settings ───
scene.render.filepath = "/Users/shehanparmar/Desktop/dev/work/IDEAS/static_protein/frames/"
scene.render.image_settings.file_format = 'PNG'

bpy.context.view_layer.update()
scene.frame_set(1)

print(f"Camera orbit: {cam_distance:.1f} units distance, 360° over 480 frames")
print(f"DOF: f/2.8 focused on molecule center")
print(f"Output: /Users/shehanparmar/Desktop/dev/work/IDEAS/static_protein/frames/")
print("Camera and animation setup complete")
