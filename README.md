# dock-confidence

[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL_3.0-or_later-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Tests](https://img.shields.io/badge/tests-14%2F14%20passing-brightgreen.svg)
![CI](https://github.com/amurlaniakea/dock-confidence/actions/workflows/ci.yml/badge.svg)

**Calibrated confidence for protein–ligand docking poses.**

`dock-confidence` is a layer of *verification and calibration* over **any**
docking engine (DiffDock, AutoDock, Smina, FlowDock). It does **not**
generate poses — it verifies and calibrates them.

Given a docked pose, it estimates a **calibrated probability
P(RMSD < 2.0 Å)** that the pose is near-native, produces an
uncertainty band, filters decoys, and emits a calibration report
(ECE + reliability diagram) ready for scientific / regulatory validation.

---

## Why this exists (the gap)

Scoring functions are *"the main bottleneck"* in molecular docking:
they *"routinely fail to rank near-native poses above decoys"*
(AgenticPosesRanker, arXiv:2605.03707). ~49.4% of 8,597
PDBbind systems show **scoring-function failures** (the lowest-RMSD
pose does not receive the best score).

Meanwhile, DiffDock *does* emit a confidence score — but its own
README states it *"can be hard to interpret and compare... [it] is
NOT a direct measure of binding affinity"*. The score is **not calibrated**
and **not comparable across complexes**.

**The gap, quantified (GitHub):** `molecular-docking` → **183 repos**,
but `docking pose confidence RMSD calibration` → **0 repos**.
Zero open-source tools solve the calibrated-confidence layer.

`dock-confidence` democratises what DockGen (arXiv:2402.18396)
calls *Confidence Bootstrapping* — but as a reusable OSS tool that
wraps **any** dock, without retraining a diffusion model.

## Install

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```bash
# 1. Parse a DiffDock / Smina SDF, compute RMSD to a native crystal,
#    and calibrate confidence (heuristic fallback).
dock-confidence parse --input poses.sdf --native crystal.pdb \
    --calibrate-mode heuristic --out poses.json

# 2. Validate on a dataset (built-in synthetic fixture, or your CASF-2016).
dock-confidence validate --fixture --seed 42 --n-systems 20
dock-confidence validate --fixture --mode platt --seed 42

# 3. Filter decoys + reliability diagram.
dock-confidence report --input poses.json --threshold 0.5
```

### Output (JSON per pose)

```json
[
  {"system_id":"1A46", "pose_id":0, "raw_score":-9.5,
   "score_source":"smina_affinity", "rmsd":0.36, "near_native":true,
   "p_near_native":0.54, "confidence_band":"moderate", "is_decoy":false}
]
```

## Metrics

* **ECE** — Expected Calibration Error (Guo et al. 2017),
  `ECE = Σ_b (|B_b|/n)·|acc(B_b) − conf(B_b)|`.
  Lower is better; the tool reports `ECE(calibrated) < ECE(raw score)`.
* **Top-1 accuracy** — fraction of systems whose highest-P pose is
  truly near-native (AgenticPosesRanker Eq.11).
* **Reliability diagram** — conf(B_b) vs acc(B_b); diagonal = perfect.

## Status

MVP complete: parser (SDF/PDBQT/DLG) → RMSD (heavy-atom,
MCS-aligned, cached per system) → calibration (Platt / heuristic) →
ECE + report. **14/14 tests pass.** Validated on a controlled synthetic
fixture (AC7: `ECE_calibrated 0.080 < ECE_raw 0.368`). Real-dataset
validation (CASF-2016, PDBbind v2016, PoseBusters, DockGen) is a
documented next step requiring manual browser download — see `RESEARCH.md`.

## License

AGPL-3.0-or-later © 2026 Pedro Sordo Martínez
(amurlaniakea@gmail.com).

---

# dock-confidence (Español)

**Confianza calibrada para poses de docking proteína–ligando.**

`dock-confidence` es una capa de *verificación y calibración* sobre
**cualquier** motor de docking (DiffDock, AutoDock, Smina, FlowDock).
**No** genera poses — las *verifica y calibra*.

Dada una pose dockada, estima una **probabilidad calibrada
P(RMSD < 2.0 Å)** de que la pose sea nativa-cercana, produce una banda
de incertidumbre, filtra decoys y emite un informe de calibración
(ECE + diagrama de fiabilidad) listo para validación científica/regulatoria.

## Por qué existe (el hueco)

Las funciones de puntuación son el *"cuello de botella principal"* del
docking: *"fallan rutinariamente en rankear poses nativa-cercanas por
encima de decoys"* (AgenticPosesRanker, arXiv:2605.03707). ~49.4% de
los 8.597 sistemas PDBbind presentan **fallos de puntuación**.

DiffDock *sí* emite una confianza — pero su propio README dice que
*"puede ser difícil de interpretar y comparar... [no] es una medida
directa de la afinidad de unión"*. La puntuación **no está calibrada**
ni es **comparable entre complejos**.

**El hueco, cuantificado (GitHub):** `molecular-docking` → **183 repos**,
pero `docking pose confidence RMSD calibration` → **0 repos**.
Cero herramientas open-source resuelven la capa de confianza calibrada.

`dock-confidence` democratiza lo que DockGen (arXiv:2402.18396) llama
*Confidence Bootstrapping* — como herramienta OSS reutilizable que
envuelve **cualquier** dock, sin reentrenar un modelo de difusión.

## Instalación

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

## Inicio rápido

```bash
# 1. Parsea un SDF de DiffDock/Smina, calcula RMSD a un cristal nativo
#    y calibra la confianza (fallback heurístico).
dock-confidence parse --input poses.sdf --native crystal.pdb \
    --calibrate-mode heuristic --out poses.json

# 2. Valida en un dataset (fixture sintético integrado, o tu CASF-2016).
dock-confidence validate --fixture --seed 42 --n-systems 20
dock-confidence validate --fixture --mode platt --seed 42

# 3. Filtra decoys + diagrama de fiabilidad.
dock-confidence report --input poses.json --threshold 0.5
```

## Métricas

* **ECE** — Error de Calibración Esperado (Guo et al. 2017). Menor es
  mejor; la herramienta reporta `ECE(calibrado) < ECE(score crudo)`.
* **Top-1 accuracy** — fracción de sistemas cuya pose de mayor-P es
  realmente nativa-cercana (AgenticPosesRanker Eq.11).
* **Diagrama de fiabilidad** — conf(B_b) vs acc(B_b); diagonal = perfecto.

## Estado

MVP completo: parser (SDF/PDBQT/DLG) → RMSD (heavy-atom, MCS-align,
cacheado por sistema) → calibración (Platt / heurístico) → ECE + informe.
**14/14 tests pasan.** Validado en fixture sintético controlado
(AC7: `ECE_calibrado 0.080 < ECE_crudo 0.368`). La validación con
dataset real (CASF-2016, PDBbind v2016, PoseBusters, DockGen) queda
como siguiente paso documentado (requiere descarga manual vía navegador)
— ver `RESEARCH.md`.

## Licencia

AGPL-3.0-or-later © 2026 Pedro Sordo Martínez
(amurlaniakea@gmail.com).
