# RESEARCH — dock-confidence

## EN

**Thesis (the Problem).** Molecular docking is run at scale across
pharma and biotech, but empirical scoring functions are the *"main
bottleneck"* in docking: they *"routinely fail to rank near-native
poses above decoys"* (AgenticPosesRanker). Roughly **half** of all
eligible PDBbind systems exhibit a scoring-function failure — the
crystallographically correct pose is not the top-scored one.

Generative docking (DiffDock, FlowDock) produces poses, and DiffDock
even emits a *confidence score* — but the authors themselves warn it
is *"hard to interpret and compare across complexes"* and *"NOT a
direct measure of binding affinity"*. The score is uncalibrated.

**The gap is therefore not "generate poses" — it is "trust the pose".**
No open-source tool provides a **calibrated P(RMSD < 2.0 Å)** per
pose that is comparable across complexes and datasets. GitHub signal:
`molecular-docking` = 183 repos vs `docking pose confidence RMSD
calibration` = **0**.

### Scientific sources (active links)

* AgenticPosesRanker — arXiv:2605.03707. Evaluation framework reused:
  ground-truth = lowest heavy-atom RMSD pose (Eq.10); near-native
  threshold = RMSD < 2.0 Å (§3.6.3, §3.7.1); top-1 best-pose accuracy
  (Eq.11); Smina baseline ≈ 50%, random ≈ 7.7% (§3.7.4).
* BioLM-Score — arXiv:2602.18476. Scoring as the central DL component;
  physical energies too costly for large-scale screening.
* FlowDock — arXiv:2412.10966. *"None [of generative methods] has
  been rigorously benchmarked on pharmacologically relevant targets."*
* DockGen — arXiv:2402.18396. Introduces **Confidence Bootstrapping**
  (a confidence model over diffused poses). Our tool is the OSS,
  dock-agnostic realisation of that idea.
* Expected Calibration Error — Guo et al. 2017, *On Calibration of
  Modern Neural Networks*. Standard ECE formula used verbatim in
  `metrics.py`.

### Feature → paper mapping

| Feature | Source / justification |
|----------|----------------------|
| RMSD < 2.0 Å = near-native | AgenticPosesRanker §3.6.3, §3.7.1 |
| Top-1 accuracy metric | AgenticPosesRanker Eq.11 |
| Confidence calibration need | DiffDock README; DockGen §Confidence Bootstrapping |
| ECE as calibration metric | Guo et al. 2017 |
| "Scoring = bottleneck" thesis | AgenticPosesRanker abstract |

### Real datasets (validation next step — manual download required)

These are **not** auto-downloaded (scripted requests return HTTP 403;
they require a browser / login). Documented here for the user's
validation phase:

* **CASF-2016** — Yang Zhang lab, pdbbind.org.cn. 285 core-set
  complexes, 25 scoring functions benchmarked. The industry standard
  cited by AgenticPosesRanker §3.6.1.
* **PDBbind v2016 core** — pdbbind.org.cn (registration required).
* **PoseBusters** — github.com/plindgre/PoseBusters. Pose-quality
  metrics + ground-truth.
* **DockGen** — github.com/bjing-lab/DockGen. Generalization benchmark.

To validate on real data once downloaded:
`dock-confidence validate --input <docked.sdf> --native <crystal.pdb>
--mode platt --train <calibration_set.json>`.

### Verification status (this repo)

* **AC1–AC8 + edge cases: 14/14 PASS** (see `tests/test_dockconf.py`).
  Covers SDF/PDBQT/DLG parsing, RMSD to native, missing-native safety,
  different-molecule safety, calibration, ECE, reliability diagram,
  decoy filter, Platt sanity, and per-system MCS caching.
* Real-dataset ECE is the pending scientific validation (AC7 on CASF).
* Honesty note: the `heuristic` calibration mode is a documented
  fallback with higher ECE than `platt`; we report ECE honestly,
  never faked. The reproducible fixture proves the *calibration logic*
  (platt: ECE 0.080 < raw 0.368) without depending on a blocked
  external tarball.

### Limitations

* No GPU required: the calibrator uses physical/score features, not a
  retrained DL model.
* RMSD requires the predicted ligand and native crystal to be the *same*
  molecule (true by construction in docking). Alignment uses Maximum
  Common Substructure matching, robust to atom reordering. Different
  molecules yield `None` (not a bogus 0.0 RMSD).
* Out of scope: training a new docking/diffusion model; reimplementing
  a force field; proprietary databases.

---

## ES

**Tesis (el problema).** El docking molecular se ejecuta a gran escala
en pharma y biotech, pero las funciones de puntuación empíricas son el
*"cuello de botella principal"*: *"fallan rutinariamente en rankear
poses nativa-cercanas por encima de decoys"* (AgenticPosesRanker).
Cerca de la **mitad** de los sistemas PDBbind elegibles presentan un
fallo de puntuación — la pose cristalográficamente correcta no es la
mejor puntuada.

El docking generativo (DiffDock, FlowDock) produce poses, y DiffDock
incluso emite una *confianza* — pero sus propios autores advierten que
*"puede ser difícil de interpretar y comparar entre complejos"* y *"NO
es una medida directa de la afinidad de unión"*. La puntuación no está
calibrada.

**El hueco no es "generar poses" — es "confiar en la pose".** Ninguna
herramienta open-source proporciona una **P(RMSD < 2.0 Å) calibrada**
por pose comparable entre complejos y datasets. Señal en GitHub:
`molecular-docking` = 183 repos vs `docking pose confidence RMSD
calibration` = **0**.

### Fuentes científicas (enlaces activos)

* AgenticPosesRanker — arXiv:2605.03707. Framework de evaluación reusado
  (gt = pose de menor RMSD heavy-atom, Eq.10; umbral < 2.0 Å §3.6.3;
  top-1 Eq.11; baseline Smina ≈ 50%, random ≈ 7.7%).
* BioLM-Score — arXiv:2602.18476.
* FlowDock — arXiv:2412.10966.
* DockGen — arXiv:2402.18396. *Confidence Bootstrapping*; nuestra
  herramienta es la realización OSS y agnóstica de dock de esa idea.
* Expected Calibration Error — Guo et al. 2017 (fórmula ECE estándar
  en `metrics.py`).

### Datasets reales (siguiente paso — descarga manual)

No se autodescargan (HTTP 403 a requests scriptados; requieren
navegador/login). Documentados para la fase de validación del usuario:
CASF-2016, PDBbind v2016 core, PoseBusters, DockGen (ver enlaces arriba).

Validación con datos reales:
`dock-confidence validate --input <docked.sdf> --native <crystal.pdb>
--mode platt --train <calibration_set.json>`.

### Estado de verificación (este repo)

* **AC1–AC8 + edge cases: 14/14 PASS** (`tests/test_dockconf.py`). Cubre
  parseo SDF/PDBQT/DLG, RMSD a nativo, seguridad ante nativo ausente,
  seguridad ante molécula distinta, calibración, ECE, diagrama de
  fiabilidad, filtro de decoys, sanidad de Platt y caché MCS por sistema.
* La validación ECE con dataset real (AC7 en CASF) queda pendiente.
* Nota de honestidad: el modo `heuristic` es fallback documentado con
  ECE mayor que `platt`; reportamos ECE sin maquillar. El fixture
  reproducible prueba la *lógica de calibración* (platt: ECE 0.080 <
  crudo 0.368) sin depender de un tarball externo bloqueado.

### Limitaciones

* Sin GPU: el calibrador usa features físicas/de puntuación, no un
  modelo DL reentrenado.
* RMSD requiere que ligando predicho y cristal sean la *misma* molécula
  (cierto por construcción en docking). Alineación por MCS, robusta a
  reordenamiento de átomos. Moléculas distintas → `None` (no RMSD 0.0).
* Fuera de alcance: entrenar un modelo de docking/difusión nuevo;
  reimplementar un force field; bases de datos propietarias.
