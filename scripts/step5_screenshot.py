"""Step 5: Take a viewport screenshot and a quick test render."""
import bpy

scene = bpy.context.scene
scene.frame_set(1)

# Quick low-res test render to verify everything
scene.render.filepath = "/Users/shehanparmar/Desktop/dev/work/IDEAS/static_protein/test_render.png"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.cycles.samples = 16
scene.render.resolution_percentage = 100

bpy.ops.render.render(write_still=True)
print(f"Test render saved to {scene.render.filepath}")

# Restore render settings
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.cycles.samples = 64
