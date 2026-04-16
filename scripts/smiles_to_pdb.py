#!/usr/bin/env python3
"""
Convert SMILES strings to 3D PDB files using RDKit ETKDG algorithm.

Usage:
    python smiles_to_pdb.py "CCO" -o ethanol.pdb
    python smiles_to_pdb.py "CC(=O)Oc1ccccc1C(=O)O" -o aspirin.pdb --optimize
    python smiles_to_pdb.py "c1ccccc1" -o benzene.pdb --name benzene
"""

import os
import urllib.request
import urllib.error
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem


PUBCHEM_3D_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{}/SDF?record_type=3d"


def fetch_pubchem_3d(smiles: str) -> Chem.Mol | None:
    """
    Try to fetch a 3D structure from PubChem by SMILES.
    Returns RDKit Mol with 3D coords, or None if unavailable.
    """
    encoded_smiles = urllib.request.quote(smiles, safe='')
    url = PUBCHEM_3D_URL.format(encoded_smiles)

    try:
        response = urllib.request.urlopen(url, timeout=10)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

    sdf_data = response.read().decode('utf-8')
    mol = Chem.MolFromMolBlock(sdf_data, removeHs=False)
    return mol


def smiles_to_mol(smiles: str) -> Chem.Mol:
    """Parse SMILES string into RDKit molecule."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Failed to parse SMILES: {smiles}")
    return mol


def generate_3d_coords(mol: Chem.Mol, optimize: bool = False) -> Chem.Mol:
    """
    Generate 3D coordinates using ETKDG algorithm.

    Parameters
    ----------
    mol : Chem.Mol
        RDKit molecule (2D)
    optimize : bool
        If True, generate 10 conformers and select lowest energy (MMFF94).
        If False, generate single clean conformer.
    """
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42

    if optimize:
        cids = AllChem.EmbedMultipleConfs(mol, numConfs=10, params=params)
        if len(cids) == 0:
            raise RuntimeError("Failed to generate conformers")
        results = AllChem.MMFFOptimizeMoleculeConfs(mol, maxIters=500)
        energies = [r[1] if r[0] == 0 else float('inf') for r in results]
        best_conf = mol.GetConformer(cids[int(np.argmin(energies))])
        mol_out = Chem.Mol(mol)
        mol_out.RemoveAllConformers()
        mol_out.AddConformer(best_conf, assignId=True)
        return mol_out

    status = AllChem.EmbedMolecule(mol, params)
    if status == -1:
        raise RuntimeError("Failed to embed molecule — try --optimize for difficult structures")
    return mol


def smiles_to_pdb(smiles: str, output_path: str, optimize: bool = False,
                  try_pubchem: bool = True) -> str:
    """
    Convert a SMILES string to a 3D PDB file.

    Parameters
    ----------
    smiles : str
        SMILES string
    output_path : str
        Path to write PDB file
    optimize : bool
        Use MMFF94 optimization
    try_pubchem : bool
        Try fetching from PubChem first

    Returns
    -------
    str
        Absolute path to the written PDB file
    """
    mol_3d = None

    if try_pubchem:
        mol_3d = fetch_pubchem_3d(smiles)
        if mol_3d is not None:
            print(f"Fetched 3D structure from PubChem")

    if mol_3d is None:
        mol = smiles_to_mol(smiles)
        mol_3d = generate_3d_coords(mol, optimize=optimize)
        print(f"Generated 3D structure locally via ETKDG")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    Chem.MolToPDBFile(mol_3d, output_path)
    abs_path = os.path.abspath(output_path)
    print(f"Saved PDB: {abs_path}")
    return abs_path


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Convert SMILES to 3D PDB file')
    parser.add_argument('smiles', help='SMILES string (quote it)')
    parser.add_argument('-o', '--output', default='molecule.pdb', help='Output PDB path')
    parser.add_argument('--optimize', action='store_true',
                        help='Optimize geometry with MMFF94 (slower, more realistic)')
    parser.add_argument('--no-pubchem', action='store_true',
                        help='Skip PubChem lookup, generate locally')

    args = parser.parse_args()
    smiles_to_pdb(args.smiles, args.output, optimize=args.optimize,
                  try_pubchem=not args.no_pubchem)
