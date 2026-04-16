"""
Template: Batch Render Animation Frames

Renders a subset of frames to avoid BlenderMCP's 180-second timeout.
Call this template multiple times with different FRAME_START/FRAME_END values
to render the full animation in chunks.

Usage pattern (agent sends via execute_blender_code):
  1. First call: set up scene, molecule, camera, etc. (use trajectory_animation.py)
     but SKIP the bpy.ops.render.render(animation=True) at the end.
  2. Then call this template repeatedly for each batch:
     - Batch 1: FRAME_START=1,   FRAME_END=50
     - Batch 2: FRAME_START=51,  FRAME_END=100
     - Batch 3: FRAME_START=101, FRAME_END=150
     - ...
  3. After all batches, combine PNGs to MP4 locally with ffmpeg.

Parameters to customize:
- OUTPUT_DIR: absolute path to directory for PNG sequence (must match scene setup)
- FRAME_START: first frame to render in this batch
- FRAME_END: last frame to render in this batch
"""

import bpy

# === CUSTOMIZE THESE ===
OUTPUT_DIR = "/absolute/path/to/frames/"
FRAME_START = 1
FRAME_END = 50
# ========================

scene = bpy.context.scene
scene.frame_start = FRAME_START
scene.frame_end = FRAME_END
scene.render.filepath = OUTPUT_DIR
scene.render.image_settings.file_format = 'PNG'

bpy.ops.render.render(animation=True)

print(f"Batch rendered frames {FRAME_START}-{FRAME_END} to {OUTPUT_DIR}")
