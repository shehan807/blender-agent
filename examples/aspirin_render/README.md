# Example Prompts: Static Molecule Renders

Start simple, then layer on complexity. Each prompt below builds on the previous.

## Beginner

```
Render aspirin (SMILES: CC(=O)Oc1ccccc1C(=O)O) as ball-and-stick.
Save the PNG to this directory.
```

```
Render caffeine as ball-and-stick with a dark background and black outlines.
```

## Intermediate

```
Render aspirin with:
- Ball-and-stick style, CPK element colors
- Dark background
- Freestyle silhouette outlines (1.5px black)
- Transparent background for compositing
- 2000x2000, 128 Cycles samples
- Rotate the molecule 30 degrees around X so I can see the ring face
```

```
Load the protein at /path/to/protein.pdb. Show it cartoon style
with each chain a different color. Add depth of field focused on the
center of the structure. Dark background, cinematic lighting.
```

## Advanced

```
Load PDB 8V00 at /path/to/8V00.pdb. I want a publication-quality figure:
- Cartoon representation for chains A, B, C (blue-to-teal gradient)
- Chain D in a contrasting warm color (orange)
- Semi-transparent molecular surface layered over the cartoon
- HDRI studio lighting with soft reflections on the surface
- Depth of field focused on the pore interface between chains
- Freestyle black outlines
- 4K resolution, 256 samples with denoising
```

```
Render ATP (find the SMILES) as space-filling spheres with a glass material —
I want to see Cycles ray-traced caustics and refraction through the molecule.
Place it on a reflective dark surface. Dramatic rim lighting from behind.
```
