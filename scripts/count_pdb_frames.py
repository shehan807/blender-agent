#!/usr/bin/env python3
"""
Count the number of MODEL records in a multi-model PDB file.

Lightweight utility — no MDAnalysis or RDKit required. Uses only stdlib.

Usage:
    python count_pdb_frames.py trajectory.pdb
    python count_pdb_frames.py trajectory.pdb --json
"""

import argparse
import json
import os


def count_frames(pdb_path: str) -> dict:
    """
    Count MODEL records in a PDB file.

    Returns
    -------
    dict
        n_frames: int, n_atoms_first_frame: int, file_size_mb: float
    """
    n_models = 0
    n_atoms_first = 0
    in_first_model = True

    with open(pdb_path, 'r') as f:
        for line in f:
            if line.startswith("MODEL"):
                n_models += 1
                if n_models > 1:
                    in_first_model = False
            elif in_first_model and (line.startswith("ATOM") or line.startswith("HETATM")):
                n_atoms_first += 1

    # If no MODEL records, the whole file is one frame
    if n_models == 0:
        n_models = 1

    file_size_mb = os.path.getsize(pdb_path) / (1024 * 1024)

    return {
        "n_frames": n_models,
        "n_atoms": n_atoms_first,
        "file_size_mb": round(file_size_mb, 2),
        "path": os.path.abspath(pdb_path),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count frames in a multi-model PDB file')
    parser.add_argument('pdb', help='Path to PDB file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()
    result = count_frames(args.pdb)

    if args.json:
        print(json.dumps(result))
    else:
        print(f"Frames: {result['n_frames']}")
        print(f"Atoms per frame: {result['n_atoms']}")
        print(f"File size: {result['file_size_mb']} MB")
        print(f"Path: {result['path']}")
