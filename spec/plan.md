# Plan — dock-confidence

## Arquitectura (módulos, contrato único de dataclass)

```
dockconf/
  __init__.py
  parse.py      # FR1: lee SDF multimodelo / PDBQT / DLG → lista de Pose
  rmsd.py       # FR2: RMSD heavy-atom simétrico a nativa (RDKit)
  calibrate.py   # FR4: score crudo → P(RMSD<2Å) calibrado (Platt/isotónico sobre CASF)
  metrics.py     # FR5/§2: ECE, top-1 accuracy, reliability diagram
  report.py      # FR5/FR6: JSON + PNG + filtro de decoys
  cli.py         # FR3: click/argparse entrypoint
  data/
    fixture.py   # generador de dataset sintético controlado (validación reproducible)
tests/
  test_parse.py, test_rmsd.py, test_calibrate.py, test_metrics.py, test_cli.py
RESEARCH.md     # fundamentación científica + fuentes de datasets reales
```

**Contrato de dataclass (fuente única de verdad) — define en `parse.py`:**
```python
@dataclass
class Pose:
    system_id: str
    pose_id: int
    ligand_mol: object        # RDKit Mol (heavy atoms)
    raw_score: float          # minimizedAffinity (Smina) o confidence (DiffDock)
    score_source: str         # "smina_affinity" | "diffdock_confidence"
    rmsd: float | None = None      # None si no se provee nativa
    near_native: bool | None = None  # rmsd < 2.0
    p_near_native: float | None = None  # calibrado (FR4)
    confidence_band: str | None = None  # "high"|"moderate"|"low"
    is_decoy: bool | None = None
```

## Decisiones técnicas

1. **RMSD:** `rdkit.Chem.rdMolAlign.AlignMol` + `GetBestRMS` (heavy-atom,
   symmetry-corrected) — coincide con la definición de AgenticPosesRanker §3.7.1
   ("heavy-atom symmetry-corrected RMSD"). Si RDKit falla en alineación, fallback a
   `AllChem.AlignMol` con mapa manual de heavy atoms.

2. **Calibrador (FR4):** Dos modos, elegidos por `--calibrate`:
   - `platt`: regresión logística 1-D sobre raw_score (fit en CASF train).
   - `isotonic`: mapeo no-paramétrico (sklearn opcional; si no, implementación
     propia de Pool-Adjacent-Violators). MVP usa Platt (sin sklearn).
   - `heuristic`: mapeo por tramos si no hay dataset de calibración (documentado
     como menos preciso).

3. **ECE (§2.1):** implementación propia en `metrics.py` con numpy. Bins=10
   igualmente espaciados. Fórmula literal del spec. Sin sklearn.

4. **Validación reproducible (sin dataset externo bloqueado):** `data/fixture.py`
   genera N sistemas con poses cuyo RMSD y raw_score se conocen (ruido controlado
   con semilla fija). Permite verificar AC1–AC8 de forma aislada y determinista.
   Dataset REAL (CASF-2016/PDBbind/PoseBusters) queda como `--dataset` opcional
   documentado en RESEARCH.md (requiere descarga manual vía navegador).

5. **CLI:** `argparse` stdlib (evita dependencia click). Subcomandos:
   `parse`, `calibrate`, `validate`, `report`.

## Orden de implementación (→ Tasks)

1. `parse.py` + `Pose` dataclass (FR1, AC1, AC3)
2. `rmsd.py` (FR2, AC2)
3. `metrics.py` ECE + top-1 (§2, AC5)
4. `calibrate.py` Platt heuristic (FR4, AC4)
5. `report.py` JSON + PNG + filtro (FR5/FR6, AC6, AC8)
6. `cli.py` (FR3, AC3)
7. `data/fixture.py` (validación reproducible, AC7, AC8)
8. `tests/` por módulo (cada AC aislado)
9. `RESEARCH.md` + `LICENSE` + `pyproject.toml` + `README.md`

## Riesgos y mitigaciones
- RDKit puede no alinear ligandos con átomos dummy → `rmsd.py` valida conteo de
  heavy atoms antes de alinear; si difere, marca `rmsd=None` (no crashea).
- Descarga de CASF bloqueada por 403 (requiere navegador) → no se asume; fixture
  local cubre AC1–AC8; dataset real es paso opcional documentado.
- ECE alto en MVP heurístico → se reporta honestamente, no se maquilla (regla SDD).
