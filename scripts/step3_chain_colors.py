"""Step 3: Apply per-chain coloring to the protein.

Chain mapping (integer IDs from MN):
  0 (A) → Steel Blue    (0.274, 0.510, 0.706)
  1 (B) → Teal          (0.0,   0.502, 0.502)
  2 (C) → Cyan          (0.251, 0.749, 0.827)
  3 (D) → Amber/Orange  (1.0,   0.6,   0.15)
"""
import bpy

mol_obj = bpy.data.objects.get("8V00")
if not mol_obj:
    raise RuntimeError("Could not find molecule object '8V00'")

mesh = mol_obj.data

# ─── Get chain_id and Color attributes ───
chain_attr = mesh.attributes.get('chain_id')
color_attr = mesh.attributes.get('Color')

if not chain_attr or not color_attr:
    raise RuntimeError(f"Missing attributes. chain_id={chain_attr}, Color={color_attr}")

# Per-chain color palette (linear sRGB approximations)
# Using slightly desaturated, rich colors for cinematic look
CHAIN_COLORS = {
    0: (0.055, 0.220, 0.450, 1.0),   # Steel Blue (chain A)
    1: (0.0,   0.215, 0.215, 1.0),   # Teal (chain B)
    2: (0.050, 0.520, 0.650, 1.0),   # Cyan (chain C)
    3: (1.0,   0.318, 0.023, 1.0),   # Amber/Orange (chain D)
}

# Fallback for any unexpected chain IDs
DEFAULT_COLOR = (0.5, 0.5, 0.5, 1.0)

n_verts = len(mesh.vertices)
print(f"Coloring {n_verts} atoms by chain...")

# Count per chain
chain_counts = {}
for i in range(n_verts):
    cid = chain_attr.data[i].value
    chain_counts[cid] = chain_counts.get(cid, 0) + 1
    color_attr.data[i].color = CHAIN_COLORS.get(cid, DEFAULT_COLOR)

for cid in sorted(chain_counts):
    print(f"  Chain {cid}: {chain_counts[cid]} atoms → color {CHAIN_COLORS.get(cid, DEFAULT_COLOR)[:3]}")

# ─── Modify geometry node tree to stop overriding our colors ───
# Find the MN modifier's node group
for mod in mol_obj.modifiers:
    if mod.type == 'NODES' and mod.node_group:
        tree = mod.node_group
        print(f"Node group: {tree.name}")
        print(f"Nodes: {[n.name for n in tree.nodes]}")

        # Remove links FROM Color Common and Color Attribute Random
        # so our per-chain colors on the mesh are preserved
        links_to_remove = []
        for link in tree.links:
            from_name = link.from_node.name
            if 'Color Common' in from_name or 'Color Attribute Random' in from_name:
                links_to_remove.append(link)
                print(f"  Removing link: {from_name}[{link.from_socket.name}] → {link.to_node.name}[{link.to_socket.name}]")

        for link in links_to_remove:
            tree.links.remove(link)

        print(f"  Removed {len(links_to_remove)} color override links")

bpy.context.view_layer.update()
print("Per-chain coloring applied successfully")
