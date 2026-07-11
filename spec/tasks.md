# Tasks — dock-confidence

Cada task es atómica y verificable contra su AC. Formato: `[ID] módulo — verificación`.

## Fase 1 — Parser + RMSD + dataclass (FR1, FR2, AC1, AC2, AC3)
- [T1] `parse.py`: dataclass `Pose` (contrato único). Verif: import sin error.
- [T2] `parse.py`: `read_sdf_multimodel(path)` → lista de `Pose` con `raw_score` (prop `minimizedAffinity` o `confidence`) + `score_source`. Verif AC1: `parse sample.sdf` lista N poses.
- [T3] `parse.py`: `read_pdbqt(path)` y `read_dlg(path)` (AutoDock) → `Pose`. Verif: lee un pdbqt de ejemplo.
- [T4] `rmsd.py`: `rmsd_to_native(pose_mol, native_mol)` heavy-atom simétrico (RDKit AlignMol/GetBestRMS). Verif AC2: RMSD conocido en fixture.
- [T5] `parse.py`/cli: flag `--native` computa `rmsd` + `near_native = rmsd<2.0`. Verif AC2.

## Fase 2 — Calibrador + métricas (FR4, FR5, §2, AC4, AC5, AC6)
- [T6] `metrics.py`: `ecc()` fórmula §2.1 (B=10 bins, numpy). Verif AC5: escalar en [0,1] sobre fixture.
- [T7] `metrics.py`: `top1_accuracy(poses)` Eq.11 + `reliability_diagram(poses, path)`. Verif AC6: PNG >1KB.
- [T8] `calibrate.py`: `fit_platt(scores_train, labels)` + `predict_p(scores)`. Verif AC4: `p_near_native` en JSON.
- [T9] `calibrate.py`: modo `heuristic` por tramos si no hay train. Documentado como menos preciso.

## Fase 3 — Reporte + CLI + validación (FR3, FR5, FR6, AC3, AC7, AC8)
- [T10] `report.py`: `write_json(poses, out)` + `filter_decoys(poses, thr)` marca `is_decoy`. Verif AC8.
- [T11] `cli.py`: subcomandos `parse/calibrate/validate/report`, flags `--native --format --out --threshold --dataset`. Verif AC3: `json.tool` válido.
- [T12] `data/fixture.py`: genera dataset sintético controlado (semilla fija) con RMSD+score conocidos. Verif AC7/AC8.
- [T13] `validate` sobre fixture: ECE_calibrado < ECE_crudo (AC7) y ≥1 decoy marcado (AC8).

## Fase 4 — Empaquetado profesional (SDD packaging)
- [T14] `LICENSE` AGPL-3.0-or-later (año 2026, autor Pedro Sordo Martínez).
- [T15] `pyproject.toml` (package-mode=false) + `README.md` (badges, quick-start, autoría).
- [T16] `RESEARCH.md`: tesis del problema + links a arXiv:2605.03707, 2412.10966, 2402.18396 + mapeo AC→papers + fuentes de datasets reales (CASF-2016, PDBbind v2016, PoseBusters, DockGen) con nota de descarga manual.
- [T17] `tests/` por módulo (AC aislado). `pytest` en venv.
- [T18] CI local (lint→test) antes de cualquier GitHub (gobernanza local-first).

## Criterio de cierre por fase
- Fase 1 → AC1, AC2, AC3 PASS.
- Fase 2 → AC4, AC5, AC6 PASS.
- Fase 3 → AC7, AC8 PASS (validación real con fixture).
- Fase 4 → repo cumple estándar SDD; GitHub SOLO al ~90%.
