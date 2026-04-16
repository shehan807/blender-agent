# Molecular Nodes — Python API Reference

Molecular Nodes (MN) is a Blender addon for molecular visualization. Inside Blender,
import it as:

```python
import bl_ext.blender_org.molecularnodes as mn
```

## Scene Setup with Canvas

Always create a Canvas FIRST — it clears the scene and sets up the renderer:

```python
canvas = mn.Canvas(mn.scene.Cycles(samples=128), resolution=(2000, 2000))
```

- `mn.scene.Cycles(samples=N)` — Cycles renderer (high quality)
- `mn.scene.EEVEE()` — EEVEE renderer (fast preview)
- `resolution=(W, H)` — output resolution in pixels

## Loading Molecules

```python
mol = mn.Molecule.load("/absolute/path/to/molecule.pdb")
```

- Accepts: PDB, CIF, SDF, MOL2 files
- The loaded molecule creates a Blender object accessible via `mol._object_name`
- Get the Blender object: `bpy.data.objects.get(mol._object_name)`

### CRITICAL: remove_solvent Default

MN defaults to `remove_solvent=True`, which strips all water (HOH) residues.
**If your system IS water or you need to see water, you must override this:**

```python
mol = mn.Molecule.load("/path/to/file.pdb", remove_solvent=False)
```

If you load a water box with the default setting, you'll get an empty mesh and
likely a crash. Always check whether the user's system contains water they want to see.

### Loading Trajectories

For multi-frame structures (multi-model PDB files):

```python
mol = mn.Molecule.load("/absolute/path/to/trajectory.pdb")
```

MN automatically detects multiple models/frames and creates an animated object.
The Blender timeline will correspond to trajectory frames.

For water/solvent trajectories, use `remove_solvent=False`:
```python
mol = mn.Molecule.load("/path/to/trajectory.pdb", remove_solvent=False)
```

## Styles

Apply a visual style after loading:

```python
mol.add_style(
    mn.StyleBallAndStick(quality=6),
    material=mn.material.AmbientOcclusion()
)
```

### Available Styles

| Style | Usage | Notes |
|---|---|---|
| `mn.StyleBallAndStick(quality=N)` | Small molecules, ligands | `quality` controls sphere smoothness (2=fast, 6=smooth) |
| `mn.StyleCartoon()` | Proteins — secondary structure | Helices, sheets, loops |
| `mn.StyleSurface()` | Molecular surfaces | Solvent-accessible surface |
| `mn.StyleRibbon()` | Protein backbone trace | Simpler than cartoon |
| `mn.StyleSticks()` | Bond-only representation | No atom spheres |
| `mn.StyleSpheres()` | Space-filling / CPK | Van der Waals radii |

### Available Materials

| Material | Effect |
|---|---|
| `mn.material.AmbientOcclusion()` | Soft shadows in crevices — good default |
| `mn.material.Default()` | Basic material |

## Fixing Element Colors (CPK Scheme)

MN's default color scheme randomizes carbon color. To get standard CPK colors:

```python
def fix_element_colors(mol):
    """Fix element colors to match CPK color scheme."""
    tree = mol.node_group

    # Remove random carbon color assignment
    links_to_remove = []
    for link in tree.links:
        if (link.from_node.name == 'Color Attribute Random' and
            link.to_node.name == 'Color Common' and
            link.to_socket.name == 'Carbon'):
            links_to_remove.append(link)
    for link in links_to_remove:
        tree.links.remove(link)

    # Set CPK colors on Color Common node
    cpk_colors = {
        'Carbon': (0.28, 0.28, 0.28, 1.0),       # Grey
        'Phosphorous': (1.0, 0.216, 0.0, 1.0),    # Orange
    }
    for node in tree.nodes:
        if node.name == 'Color Common':
            for element, color in cpk_colors.items():
                inp = node.inputs.get(element)
                if inp:
                    inp.default_value = color

    # Fix Boron color directly on mesh attributes
    mol_obj = bpy.data.objects.get(mol._object_name)
    if mol_obj and mol_obj.data:
        atomic_num_attr = mol_obj.data.attributes.get('atomic_number')
        color_attr = mol_obj.data.attributes.get('Color')
        if atomic_num_attr and color_attr:
            boron_pink = (1.0, 0.462, 0.462, 1.0)
            for i, atom_num in enumerate(atomic_num_attr.data):
                if atom_num.value == 5:  # Boron
                    color_attr.data[i].color = boron_pink
```

## Camera Framing

Auto-frame the molecule in the camera view:

```python
mol_obj = bpy.data.objects.get(mol._object_name)
canvas.frame_object(mol_obj)
```

Always call `bpy.context.view_layer.update()` before framing if you've modified the object
(e.g., applied rotation).

## Freestyle Silhouette Outlines

Add black outlines around molecules for publication-quality renders:

```python
# Enable Freestyle
bpy.context.scene.render.use_freestyle = True
bpy.context.view_layer.use_freestyle = True

# Configure line style
freestyle = bpy.context.view_layer.freestyle_settings
if freestyle.linesets:
    lineset = freestyle.linesets[0]
    lineset.select_silhouette = True
    lineset.select_border = True
    lineset.select_crease = False
    lineset.select_edge_mark = False
    lineset.linestyle.color = (0, 0, 0)  # Black
    lineset.linestyle.thickness = 1.5
```

## Rotation

Rotate molecules to face the camera (useful for planar molecules like rings):

```python
import math

mol_obj = bpy.data.objects.get(mol._object_name)
mol_obj.rotation_euler[0] = math.radians(80)  # Rotate 80 deg around X
bpy.context.view_layer.update()
```

Axis indices: 0=X, 1=Y, 2=Z

## Rendering

```python
# Transparent background
bpy.context.scene.render.film_transparent = True

# Render to file
canvas.snapshot("/absolute/path/to/output.png")
```

## Complete Example: Render a Molecule

```python
import bpy
import math
import bl_ext.blender_org.molecularnodes as mn

# Setup
canvas = mn.Canvas(mn.scene.Cycles(samples=128), resolution=(2000, 2000))

# Load
mol = mn.Molecule.load("/path/to/molecule.pdb")
mol.add_style(
    mn.StyleBallAndStick(quality=6),
    material=mn.material.AmbientOcclusion()
)

# Fix colors
fix_element_colors(mol)  # defined above

# Update scene
bpy.context.view_layer.update()

# Frame
mol_obj = bpy.data.objects.get(mol._object_name)
canvas.frame_object(mol_obj)

# Transparent background
bpy.context.scene.render.film_transparent = True

# Render
canvas.snapshot("/path/to/output.png")
```
