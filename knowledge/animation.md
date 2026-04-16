# Animation & Trajectory Playback in Blender

## Keyframe Basics

Insert keyframes on any animatable property:

```python
obj = bpy.data.objects.get("MyObject")

# Set value at a specific frame
bpy.context.scene.frame_set(1)
obj.location = (0, 0, 0)
obj.keyframe_insert(data_path="location", frame=1)

bpy.context.scene.frame_set(100)
obj.location = (5, 0, 0)
obj.keyframe_insert(data_path="location", frame=100)
```

Common `data_path` values:
- `"location"` — XYZ position
- `"rotation_euler"` — XYZ rotation (radians)
- `"scale"` — XYZ scale

## Frame Range

Set the animation frame range:

```python
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 250
scene.frame_current = 1
```

## Camera Orbit Animation

Create a rotating camera that orbits around a subject:

```python
import bpy
import math

# Create an empty at the center of the scene (or at molecule center)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
pivot = bpy.context.active_object
pivot.name = "CameraOrbitPivot"

# Get camera and parent it to the pivot
camera = bpy.data.objects.get("Camera")
if camera is None:
    bpy.ops.object.camera_add(location=(10, 0, 2))
    camera = bpy.context.active_object
    camera.name = "Camera"

camera.parent = pivot

# Point camera at center
constraint = camera.constraints.new(type='TRACK_TO')
constraint.target = pivot
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# Animate: full 360 rotation over frame range
scene = bpy.context.scene
total_frames = scene.frame_end - scene.frame_start + 1

scene.frame_set(scene.frame_start)
pivot.rotation_euler = (0, 0, 0)
pivot.keyframe_insert(data_path="rotation_euler", frame=scene.frame_start)

scene.frame_set(scene.frame_end)
pivot.rotation_euler = (0, 0, math.radians(360))
pivot.keyframe_insert(data_path="rotation_euler", frame=scene.frame_end)

# Set linear interpolation (no ease in/out for smooth continuous rotation)
# NOTE: Blender 5.0+ uses layered Actions API. Try both patterns:
action = pivot.animation_data.action
try:
    # Blender 5.0+ (layered actions)
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fcurve in cb.fcurves:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'LINEAR'
except AttributeError:
    # Blender 4.x (legacy)
    for fcurve in action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
```

### Blender 5.0 Action API Change

Blender 5.0 changed keyframe/fcurve access from `action.fcurves` to a layered system:
- **Blender 4.x:** `action.fcurves[i].keyframe_points`
- **Blender 5.0+:** `action.layers[].strips[].channelbags[].fcurves[].keyframe_points`

Always use a try/except to support both versions (see example above).

## MD Trajectory Animation Pipeline

### Overview

1. **Locally (Bash):** Convert DCD + topology to multi-model PDB using `scripts/convert_trajectory.py`
2. **In Blender:** Load the multi-model PDB via Molecular Nodes — MN handles frame interpolation
3. **In Blender:** Set up camera, lighting, render settings
4. **In Blender:** Render PNG sequence
5. **Locally (Bash):** Combine PNGs to MP4 with ffmpeg

### Step 1: Convert Trajectory (Local)

```bash
conda run -n blender-agent python scripts/convert_trajectory.py \
    topology.psf trajectory.dcd \
    -o trajectory_frames.pdb \
    --stride 10 \
    --selection "protein"
```

### Step 2: Load in Blender

```python
import bl_ext.blender_org.molecularnodes as mn

canvas = mn.Canvas(mn.scene.Cycles(samples=64), resolution=(1920, 1080))
mol = mn.Molecule.load("/absolute/path/to/trajectory_frames.pdb")
mol.add_style(
    mn.StyleBallAndStick(quality=4),
    material=mn.material.AmbientOcclusion()
)
bpy.context.view_layer.update()
```

### Step 3: Set Frame Range

Match the Blender timeline to the number of trajectory frames:

```python
# The number of frames depends on how many models are in the PDB
# MN maps model index to Blender frame
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = N_FRAMES  # replace with actual frame count
```

### Step 4: Camera and Framing

```python
mol_obj = bpy.data.objects.get(mol._object_name)
canvas.frame_object(mol_obj)

# Add camera orbit (see above) or keep static
```

### Step 5: Render Animation

```python
scene = bpy.context.scene
scene.render.filepath = "/absolute/path/to/frames/"
scene.render.image_settings.file_format = 'PNG'

# Render all frames
bpy.ops.render.render(animation=True)
```

**Warning:** `bpy.ops.render.render(animation=True)` can take a long time and may exceed
the BlenderMCP 180-second timeout. For long animations:
- Use lower samples (32-64) for drafts
- Reduce resolution for previews
- Consider rendering frame subsets

### Step 6: Combine to Video (Local)

```bash
ffmpeg -framerate 24 -i /path/to/frames/%04d.png \
    -c:v libx264 -pix_fmt yuv420p -crf 18 \
    /path/to/output.mp4
```

Frame rate guidance:
- 24 fps — cinematic look
- 30 fps — smooth standard
- 10-15 fps — acceptable for trajectory playback where motion is discrete

## Render Output Settings

```python
scene = bpy.context.scene

# PNG sequence (recommended for animation — resumable if interrupted)
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "/path/to/frames/"

# Direct MP4 (convenient but not resumable)
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.filepath = "/path/to/output.mp4"
```

## Shape Keys (Morph Targets)

For morphing between conformations:

```python
# Add shape keys to mesh
obj.shape_key_add(name="Basis")  # Reference shape
obj.shape_key_add(name="Conformation2")

# Modify vertex positions in the shape key
key_block = obj.data.shape_keys.key_blocks["Conformation2"]
for i, vert in enumerate(key_block.data):
    vert.co = new_positions[i]

# Animate shape key influence
key_block.value = 0.0
key_block.keyframe_insert(data_path="value", frame=1)
key_block.value = 1.0
key_block.keyframe_insert(data_path="value", frame=100)
```
