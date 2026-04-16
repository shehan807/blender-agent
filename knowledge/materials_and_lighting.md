# Materials, Lighting & Rendering

## Cycles Render Settings

```python
scene = bpy.context.scene
scene.render.engine = 'CYCLES'

# Quality
scene.cycles.samples = 128          # Higher = less noise (64 draft, 256 final)
scene.cycles.use_denoising = True   # AI denoiser — dramatically reduces needed samples
scene.cycles.denoiser = 'OPENIMAGEDENOISE'  # Best quality denoiser

# Resolution
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Transparent background (for compositing)
scene.render.film_transparent = True

# GPU rendering (macOS)
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.get_devices()
for device in prefs.devices:
    device.use = True
scene.cycles.device = 'GPU'
```

### Samples Guide

| Use case | Samples | Denoising | Notes |
|---|---|---|---|
| Quick preview | 16-32 | Yes | Fast iteration |
| Draft render | 64 | Yes | Good enough to evaluate composition |
| Final still | 128-256 | Yes | Publication quality |
| Animation frames | 64-128 | Yes | Balance speed vs quality |

## Three-Point Lighting Rig

Classic lighting setup for molecular visualization:

```python
import bpy
import math

def add_three_point_lights(target_location=(0, 0, 0), distance=10, energy=1000):
    """Add key, fill, and rim lights around a target point."""

    # Key light — main illumination, slightly above and to the right
    bpy.ops.object.light_add(
        type='AREA', location=(distance * 0.7, -distance * 0.7, distance * 0.5)
    )
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = energy
    key.data.size = 5

    # Fill light — softer, opposite side, less intense
    bpy.ops.object.light_add(
        type='AREA', location=(-distance * 0.7, -distance * 0.5, distance * 0.3)
    )
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = energy * 0.4
    fill.data.size = 8

    # Rim/back light — behind subject, creates edge highlights
    bpy.ops.object.light_add(
        type='AREA', location=(0, distance * 0.8, distance * 0.6)
    )
    rim = bpy.context.active_object
    rim.name = "RimLight"
    rim.data.energy = energy * 0.6
    rim.data.size = 3

    # Point all lights at target
    for light_obj in [key, fill, rim]:
        constraint = light_obj.constraints.new(type='TRACK_TO')
        constraint.target = bpy.data.objects.new("LightTarget", None)
        bpy.context.collection.objects.link(constraint.target)
        constraint.target.location = target_location
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
```

## HDRI Environment Lighting

Use an HDRI for realistic ambient lighting. If PolyHaven is enabled in BlenderMCP,
use `download_polyhaven_asset` to get HDRIs. Otherwise, set up manually:

```python
world = bpy.data.worlds.get("World")
if world is None:
    world = bpy.data.worlds.new("World")
bpy.context.scene.world = world

world.use_nodes = True
tree = world.node_tree
tree.nodes.clear()

# Background node
bg = tree.nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 1.0

# Environment texture
env_tex = tree.nodes.new('ShaderNodeTexEnvironment')
env_tex.image = bpy.data.images.load("/path/to/environment.hdr")

# Output
output = tree.nodes.new('ShaderNodeOutputWorld')

# Link
tree.links.new(env_tex.outputs['Color'], bg.inputs['Color'])
tree.links.new(bg.outputs['Background'], output.inputs['Surface'])
```

## Solid Color Backgrounds

```python
world = bpy.context.scene.world
world.use_nodes = True
tree = world.node_tree

bg_node = tree.nodes.get("Background")
if bg_node:
    # Dark background
    bg_node.inputs['Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    bg_node.inputs['Strength'].default_value = 1.0

    # White background
    # bg_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
```

## Principled BSDF Material

For custom materials on non-molecular objects:

```python
mat = bpy.data.materials.new(name="CustomMaterial")
mat.use_nodes = True
tree = mat.node_tree

principled = tree.nodes.get("Principled BSDF")
principled.inputs['Base Color'].default_value = (0.8, 0.2, 0.2, 1.0)  # Red
principled.inputs['Roughness'].default_value = 0.3
principled.inputs['Metallic'].default_value = 0.0

# Assign to object
obj.data.materials.clear()
obj.data.materials.append(mat)
```

## Glass Material

```python
principled.inputs['Base Color'].default_value = (0.95, 0.95, 1.0, 1.0)
principled.inputs['Roughness'].default_value = 0.0
principled.inputs['Transmission Weight'].default_value = 1.0
principled.inputs['IOR'].default_value = 1.45
```

## Emission (Glowing)

```python
principled.inputs['Emission Color'].default_value = (0.0, 0.5, 1.0, 1.0)
principled.inputs['Emission Strength'].default_value = 5.0
```

## Freestyle Outlines

Publication-quality black outlines (works well with molecular renders):

```python
scene = bpy.context.scene
scene.render.use_freestyle = True
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
```

## Depth of Field

Focus on a specific object with background blur:

```python
camera = bpy.data.objects.get("Camera")
camera.data.dof.use_dof = True
camera.data.dof.focus_object = bpy.data.objects.get("MoleculeObject")
camera.data.dof.aperture_fstop = 2.8  # Lower = more blur
```
