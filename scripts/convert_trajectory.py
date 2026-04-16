#!/usr/bin/env python3
"""
Convert MD trajectory (DCD + topology) to multi-model PDB for Molecular Nodes.

Molecular Nodes can load multi-model PDB files and treat each MODEL as an animation
frame. This script reads a trajectory with MDAnalysis and writes it out in that format.

Usage:
    python convert_trajectory.py topology.psf trajectory.dcd -o trajectory.pdb
    python convert_trajectory.py topology.pdb trajectory.dcd -o trajectory.pdb --stride 10
    python convert_trajectory.py topology.psf trajectory.dcd -o trajectory.pdb --selection "protein" --stride 5
    python convert_trajectory.py topology.pdb trajectory.xtc -o trajectory.pdb --max-frames 200
"""

import os
import json
import argparse
import MDAnalysis as mda


def convert_trajectory(topology: str, trajectory: str, output: str,
                       stride: int = 1, selection: str = "all",
                       max_frames: int = None) -> dict:
    """
    Convert an MD trajectory to a multi-model PDB file.

    Parameters
    ----------
    topology : str
        Path to topology file (PSF, PDB, GRO, PARM7, etc.)
    trajectory : str
        Path to trajectory file (DCD, XTC, TRR, etc.)
    output : str
        Path to write multi-model PDB
    stride : int
        Take every Nth frame (default: 1 = all frames)
    selection : str
        MDAnalysis atom selection string (default: "all")
        Examples: "protein", "not resname WAT", "backbone", "protein and not type H"
    max_frames : int or None
        Maximum number of frames to write (None = no limit)

    Returns
    -------
    dict
        Info about the conversion: n_frames, n_atoms, output_path
    """
    u = mda.Universe(topology, trajectory)
    atoms = u.select_atoms(selection)

    print(f"Topology: {topology}")
    print(f"Trajectory: {trajectory}")
    print(f"Total frames: {len(u.trajectory)}")
    print(f"Selection '{selection}': {len(atoms)} atoms (of {len(u.atoms)} total)")
    print(f"Stride: {stride}")

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)

    n_written = 0
    with mda.Writer(output, multiframe=True, n_atoms=len(atoms)) as writer:
        for i, ts in enumerate(u.trajectory[::stride]):
            writer.write(atoms)
            n_written += 1
            if n_written % 50 == 0:
                print(f"  Written {n_written} frames...")
            if max_frames is not None and n_written >= max_frames:
                print(f"  Reached max_frames={max_frames}, stopping.")
                break

    abs_path = os.path.abspath(output)
    print(f"\nDone! Wrote {n_written} frames ({len(atoms)} atoms each) to {abs_path}")

    return {
        "n_frames": n_written,
        "n_atoms": len(atoms),
        "output_path": abs_path,
        "total_trajectory_frames": len(u.trajectory),
        "stride": stride,
        "selection": selection,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert MD trajectory to multi-model PDB for Molecular Nodes'
    )
    parser.add_argument('topology', help='Topology file (PSF, PDB, GRO, etc.)')
    parser.add_argument('trajectory', help='Trajectory file (DCD, XTC, TRR, etc.)')
    parser.add_argument('-o', '--output', default='trajectory.pdb',
                        help='Output multi-model PDB path')
    parser.add_argument('--stride', type=int, default=1,
                        help='Take every Nth frame (default: 1)')
    parser.add_argument('--selection', default='all',
                        help='MDAnalysis selection string (default: "all")')
    parser.add_argument('--max-frames', type=int, default=None,
                        help='Maximum number of frames to write')

    args = parser.parse_args()
    result = convert_trajectory(args.topology, args.trajectory, args.output,
                                stride=args.stride, selection=args.selection,
                                max_frames=args.max_frames)

    # Print machine-readable JSON summary on last line for agent parsing
    print(f"JSON_METADATA:{json.dumps(result)}")
