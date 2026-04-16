"""Step 3b: Fix per-chain coloring by properly modifying the geometry node tree.

The issue: after removing Color Common links, the Set Color node still exists
with a default green color. We need to either remove it or feed our chain-based
Color attribute into it.
"""
import bpy

mol_obj = bpy.data.objects.get("8V00")
if not mol_obj:
    raise RuntimeError("Could not find molecule object '8V00'")

# ─── Inspect the node tree in detail ───
for mod in mol_obj.modifiers:
    if mod.type == 'NODES' and mod.node_group:
        tree = mod.node_group

        print("=== Node Tree Detail ===")
        for node in tree.nodes:
            print(f"\nNode: '{node.name}' (type: {node.type})")
            for i, inp in enumerate(node.inputs):
                if hasattr(inp, 'default_value'):
                    try:
                        print(f"  Input[{i}] '{inp.name}': {inp.default_value}")
                    except:
                        print(f"  Input[{i}] '{inp.name}': (complex type)")
                else:
                    print(f"  Input[{i}] '{inp.name}': (no default)")
            for i, out in enumerate(node.outputs):
                print(f"  Output[{i}] '{out.name}'")

        print("\n=== Links ===")
        for link in tree.links:
            print(f"  {link.from_node.name}[{link.from_socket.name}] → {link.to_node.name}[{link.to_socket.name}]")

        # ─── Strategy: Remove the Set Color node and let the mesh Color attribute
        # pass through naturally. The StyleSpheres node should pick up the Color
        # attribute from the mesh. ───

        # Find the Set Color node
        set_color_node = tree.nodes.get("Set Color")
        if set_color_node:
            # Find what Set Color connects to (downstream)
            downstream_links = []
            upstream_links = []
            for link in tree.links:
                if link.from_node == set_color_node:
                    downstream_links.append((link.to_node, link.to_socket))
                if link.to_node == set_color_node:
                    upstream_links.append((link.from_node, link.from_socket, link.to_socket))

            print(f"\nSet Color upstream: {[(l[0].name, l[1].name, l[2].name) for l in upstream_links]}")
            print(f"Set Color downstream: {[(l[0].name, l[1].name) for l in downstream_links]}")

            # Find the geometry input to Set Color (what feeds geometry into it)
            geo_source = None
            geo_source_socket = None
            for link in tree.links:
                if link.to_node == set_color_node and link.to_socket.name == "Geometry":
                    geo_source = link.from_node
                    geo_source_socket = link.from_socket
                    break

            # Remove Set Color node and reconnect geometry flow
            if geo_source and downstream_links:
                # Remove the Set Color node
                tree.nodes.remove(set_color_node)
                print("Removed Set Color node")

                # Reconnect: geo_source → downstream
                for to_node, to_socket in downstream_links:
                    tree.links.new(geo_source_socket, to_socket)
                    print(f"Reconnected: {geo_source.name}[{geo_source_socket.name}] → {to_node.name}[{to_socket.name}]")
            else:
                print("Could not find geometry connections to rewire")
        else:
            print("No 'Set Color' node found")

        # Also remove Color Common and Color Attribute Random nodes (cleanup)
        for name in ['Color Common', 'Color Attribute Random']:
            node = tree.nodes.get(name)
            if node:
                tree.nodes.remove(node)
                print(f"Removed orphan node: {name}")

bpy.context.view_layer.update()
print("\nNode tree modified - chain colors should now show through")
