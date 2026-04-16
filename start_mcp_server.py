"""
Auto-start script for BlenderMCP.
Loads the full BlenderMCP addon (if not already loaded) and starts the socket server.
Run via: blender --python start_mcp_server.py
"""
import bpy
import os

# Check if addon is already registered (e.g. installed via Blender preferences)
addon_already_loaded = hasattr(bpy.types.Scene, 'blendermcp_port')

if not addon_already_loaded:
    # Load the vendored addon
    addon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "blendermcp_addon.py")
    if os.path.exists(addon_path):
        with open(addon_path) as f:
            code = compile(f.read(), addon_path, 'exec')
            namespace = {}
            exec(code, namespace)
            namespace['register']()
            # Keep BlenderMCPServer class accessible
            BlenderMCPServer = namespace['BlenderMCPServer']
    else:
        print(f"ERROR: Addon not found at {addon_path}")
        raise SystemExit(1)
else:
    print("BlenderMCP addon already registered, skipping load")
    # Import the server class from the already-loaded addon module
    # The addon.py stores it in the global scope when executed
    addon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "blendermcp_addon.py")
    with open(addon_path) as f:
        code = compile(f.read(), addon_path, 'exec')
        namespace = {}
        exec(code, namespace)
        BlenderMCPServer = namespace['BlenderMCPServer']

# Auto-start the MCP server on port 9876
if not (hasattr(bpy.types, 'blendermcp_server') and bpy.types.blendermcp_server and bpy.types.blendermcp_server.running):
    bpy.types.blendermcp_server = BlenderMCPServer(port=9876)
    bpy.types.blendermcp_server.start()
    try:
        bpy.context.scene.blendermcp_server_running = True
    except Exception:
        pass
    print("BlenderMCP server auto-started on port 9876")
else:
    print("BlenderMCP server already running")
