# Blender Python API Pitfalls

Critical gotchas when scripting Blender via BlenderMCP's `execute_blender_code`.

## Common Import Mistakes

`mathutils` is a **standalone** Blender module, NOT under `bpy`:

```python
# WRONG — will crash
bpy.mathutils.Vector(...)

# RIGHT
import mathutils
mathutils.Vector(...)
```

Same applies to `bmesh`, `bpy_extras`, `gpu`, `bl_math` — they are all top-level imports.

## Context and Object Access

**Never rely on `bpy.context.object` or `bpy.context.active_object`.**
In MCP execution, context may not have an active object. Always access objects by name:

```python
# WRONG — may be None
obj = bpy.context.active_object

# RIGHT — reliable
obj = bpy.data.objects.get("MyObject")
```

**Set active object explicitly before using operators:**

```python
obj = bpy.data.objects.get("MyObject")
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
```

## Scene Updates

**Always call `bpy.context.view_layer.update()` after modifying objects.**
Without this, changes to position, rotation, scale, or mesh data may not propagate:

```python
obj.location = (1, 2, 3)
obj.rotation_euler[0] = math.radians(45)
bpy.context.view_layer.update()  # REQUIRED
```

## Operators vs Direct Data

Many `bpy.ops.*` operators require specific context (edit mode, correct selection, active object).
Prefer direct data manipulation when possible:

```python
# FRAGILE — needs correct context
bpy.ops.object.shade_smooth()

# ROBUST — direct data access
for face in obj.data.polygons:
    face.use_smooth = True
```

## Render Engine

Set explicitly — don't assume the current engine:

```python
# Cycles (ray tracing, high quality)
bpy.context.scene.render.engine = 'CYCLES'

# EEVEE (rasterization, fast)
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
```

## BlenderMCP Timeout

BlenderMCP has a **180-second timeout** per `execute_blender_code` call. If your script
takes longer, it will fail silently. Break long operations into separate calls:

1. **Call 1:** Scene setup (clear, camera, lights)
2. **Call 2:** Load molecule, apply style
3. **Call 3:** Set render settings, render

## Absolute Paths

Blender runs as a separate process. Relative paths resolve relative to Blender's working
directory, not yours. Always use absolute paths:

```python
# WRONG
mol = mn.Molecule.load("molecule.pdb")

# RIGHT
mol = mn.Molecule.load("/Users/name/project/molecule.pdb")
```

## Clearing the Scene

**DO NOT** call `bpy.ops.wm.read_factory_settings(use_empty=True)` or `mn.Canvas()`.
Both reset the entire Blender session and **kill the MCP socket server**, disconnecting
the agent permanently. Instead, selectively delete objects:

```python
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
```

Then set up camera, lights, and render settings manually.

## Mode Switching

Some operations require specific modes. Always switch explicitly:

```python
# Switch to object mode (safe default)
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
```

## Common Error: "Poll Failed"

This means an operator was called in the wrong context. Usually caused by:
- Wrong mode (edit vs object)
- No active object
- Wrong object type selected

Fix: set the active object and mode explicitly before calling the operator.

## Node Tree Manipulation

When modifying shader or geometry node trees:

```python
# Get the node tree
tree = obj.modifiers["GeometryNodes"].node_group

# Access nodes by name
node = tree.nodes.get("NodeName")

# Create links between sockets
tree.links.new(source_node.outputs[0], target_node.inputs[0])

# Remove links
for link in tree.links:
    if some_condition:
        tree.links.remove(link)
```

Node positions are set via `node.location = (x, y)` — purely cosmetic but helps with
debugging in the Blender UI.

## GPU Rendering

To use GPU for Cycles (faster renders):

```python
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'  # macOS
# prefs.compute_device_type = 'CUDA'  # NVIDIA
# prefs.compute_device_type = 'OPTIX'  # NVIDIA RTX
prefs.get_devices()
for device in prefs.devices:
    device.use = True
bpy.context.scene.cycles.device = 'GPU'
```
