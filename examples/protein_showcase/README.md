# Example Prompts: Protein Showcase (Static 360)

A 360-degree rotating render of a static protein structure — no trajectory needed.
These prompts showcase Blender features that are impossible in PyMOL/ChimeraX.

## Beginner

```
Load the protein at /path/to/8V00.pdb. Show it cartoon style with each
chain a different color. Rotating camera, 10-second video, dark background.
```

## Intermediate

```
Load PDB 8V00 at /path/to/8V00.pdb. This is a 4-chain membrane odorant receptor.
- Chains A, B, C are ORCO (co-receptor) — color them in shades of blue/teal
- Chain D is OR10 (tuning receptor) — color it orange
- Cartoon representation
- Three-point lighting rig with warm key light
- Slow 360-degree camera orbit, 15 seconds at 24fps
- 1080p, 128 samples with denoising
- Dark background
```

## Advanced — Multi-Representation

```
Load PDB 8V00 at /path/to/8V00.pdb. I want a showcase render:
- Cartoon backbone for all chains
- Overlay a semi-transparent molecular surface (30% opacity) on top
  of the cartoon so you can see the backbone through the surface
- Per-chain coloring: A=blue, B=teal, C=cyan, D=orange
- HDRI studio environment for realistic reflections on the surface
- Depth of field: f/2.8, focused on the pore at the center of the tetramer
- Freestyle black contour outlines (1px)
- Slow 360 camera orbit with slight up-down oscillation
- 4K resolution, 256 samples, denoising on
- 20 seconds at 24fps
```

## Advanced — Artistic

```
Load PDB 8V00. I want something dramatic:
- Surface representation only, colored by electrostatic potential
  (or just color by chain if electrostatics isn't available)
- Black background with volumetric fog
- Single strong backlight creating a silhouette rim-light effect
- The protein slowly emerges from darkness as a fill light fades in
  over the first 3 seconds, then the camera orbits
- Depth of field with shallow focus
- Film grain in compositing
- 1080p cinematic (2.35:1 aspect ratio), 30 seconds
```

## Ideas to Try

- Color by B-factor or residue type
- Highlight specific residues with emission (glow)
- Split the surface to show a cross-section
- Add a membrane slab (flat plane with lipid-like texture)
- Render multiple viewpoints as a contact sheet
