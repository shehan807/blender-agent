# Example Prompts: MD Trajectory Animations

Start with a basic trajectory render, then push into advanced Blender features.

## Beginner

```
Here is my water box simulation:
- Topology: /path/to/npt_final-9.pdb
- Trajectory: /path/to/md_npt-9.dcd

Make a short movie showing the water dynamics. Ball-and-stick style,
dark background, rotating camera. 720p is fine, keep it fast.
```

## Intermediate

```
Animate my water box trajectory:
- Topology: /path/to/npt_final-9.pdb
- Trajectory: /path/to/md_npt-9.dcd
- Use every 5th frame to keep it manageable
- Ball-and-stick with CPK colors
- Show the periodic box as a thin wireframe cube
- Rotating camera, 10-second video at 24fps
- Dark background, 1080p, 64 samples
```

## Advanced

```
I want a cinematic render of my water box MD simulation:
- Topology: /path/to/npt_final-9.pdb
- Trajectory: /path/to/md_npt-9.dcd
- Make the water molecules glass-like — transparent with refraction (IOR 1.33)
  so you can see Cycles caustics and light bending through the box
- Add volumetric lighting — a spotlight from above casting light shafts
  through the water
- Depth of field: focus on the center of the box, let the edges blur
- Show the simulation cell as a glowing wireframe cube (subtle emission)
- Slow rotating camera with slight vertical oscillation
- Dark environment, 1080p, 128 samples with denoising
- 10 seconds at 24fps
```

## Protein Trajectory (if you have one)

```
Here is my protein simulation:
- Topology: /path/to/protein.psf
- Trajectory: /path/to/protein.dcd

Animate it with:
- Cartoon style for the backbone, colored by secondary structure
- Skip water and ions (selection: "protein")
- Use every 10th frame
- Camera starts zoomed in on the active site, slowly pulls out
  to reveal the full protein, then orbits 360 degrees
- HDRI environment lighting
- 15 seconds at 24fps, 1080p
```
