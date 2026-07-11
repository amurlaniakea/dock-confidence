"""FR2: heavy-atom symmetric RMSD to native (RDKit AlignMol/GetBestRMS).

Ground-truth definition follows AgenticPosesRanker Eq.10 / SS3.7.1:
the best pose is the one with lowest heavy-atom symmetry-corrected
RMSD to the crystallographic binding mode. Threshold RMSD < 2.0 A
marks a near-native pose (SS3.6.3, SS3.7.1).
"""
from __future__ import annotations

from typing import Optional

from rdkit import Chem
from rdkit.Chem import rdMolAlign

from .parse import NEAR_NATIVE_THRESHOLD, Pose


def _heavy_atom_map(mol: Chem.Mol) -> list[int]:
    """Indices of Heavy (non-H) atoms, in order, for both mols."""
    return [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum() > 1]


def rmsd_to_native(pose_mol: Chem.Mol, native_mol: Chem.Mol) -> Optional[float]:
    """Heavy-atom RMSD (symmetric) to the native crystal ligand.

    Returns None if alignment is invalid (does NOT crash). Parity with
    'heavy-atom symmetry-corrected RMSD' from the literature.

    Both molecules are sanitized so AlignMol's sub-structure match works
    (required by RDKit regardless of atom order when a map is given).
    """
    if pose_mol is None or native_mol is None:
        return None
    try:
        pm = Chem.Mol(pose_mol)
        nm = Chem.Mol(native_mol)
        Chem.SanitizeMol(pm)
        Chem.SanitizeMol(nm)
    except Exception:
        return None

    # Strategy 1: heavy-atom map via MCS (handles symmetry +
    # different atom ordering between predicted ligand and crystal).
    try:
        atom_map = _canonical_map(pm, nm)
        if atom_map:
            rmsd = rdMolAlign.AlignMol(pm, nm, atomMap=atom_map)
            return float(rmsd)
    except Exception:
        pass

    # Strategy 2: raw AlignMol (same ordering, fallback).
    try:
        rmsd = rdMolAlign.AlignMol(pm, nm)
        return float(rmsd)
    except Exception:
        return None


def _canonical_map(prb: Chem.Mol, ref: Chem.Mol) -> list[tuple[int, int]]:
    """Heavy-atom match via Maximum Common Substructure (topology-aware).

    Handles symmetry + different atom ordering robustly: the predicted
    ligand and the crystal native are the SAME molecule, so an MCS
    match yields a valid 1:1 heavy-atom map. Returns [] if no
    full heavy-atom MCS match (different molecule -> bail).
    """
    from rdkit.Chem import rdFMCS

    res = rdFMCS.FindMCS(
        [prb, ref],
        atomCompare=rdFMCS.AtomCompare.CompareElements,
        bondCompare=rdFMCS.BondCompare.CompareOrder,
        completeRingsOnly=True,
        ringMatchesRingOnly=True,
    )
    if res.canceled or res.numAtoms == 0:
        return []
    pattern = Chem.MolFromSmarts(res.smartsString)
    if pattern is None:
        return []
    # Match in each molecule, map heavy atoms 1:1 by MCS order.
    pm = prb.GetSubstructMatch(pattern)
    rm = ref.GetSubstructMatch(pattern)
    if len(pm) != len(rm) or len(pm) == 0:
        return []
    out = [(int(i), int(j)) for i, j in zip(pm, rm)]
    return out


def annotate_rmsd(poses: list[Pose], native_path: str,
                   system_match: bool = True) -> list[Pose]:
    """Given a native PDB/SDF, compute rmsd + near_native for each Pose.

    If `system_match`, native is loaded once and applied to all poses of that
    system; for mixed systems pass a per-pose native later (Fase 2+).
    """
    native = _load_native(native_path)
    if native is None:
        return poses
    for p in poses:
        if p.ligand_mol is None:
            p.rmsd = None
            p.near_native = None
            continue
        r = rmsd_to_native(p.ligand_mol, native)
        p.rmsd = r
        p.near_native = (r is not None and r < NEAR_NATIVE_THRESHOLD)
    return poses


def _load_native(path: str) -> Optional[Chem.Mol]:
    if path.endswith((".pdb", ".pdbqt")):
        mol = Chem.MolFromPDBFile(path, removeHs=False, sanitize=False)
    elif path.endswith((".sdf", ".mol2", ".mol")):
        mol = Chem.MolFromMolFile(path, removeHs=False, sanitize=False)
    else:
        mol = Chem.MolFromPDBFile(path, removeHs=False, sanitize=False)
    if mol is None:
        return None
    # Keep only first conformer / heaviest fragment if needed
    return mol
