# RESEARCH — dock-confidence

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

## Scientific sources (active links)

* AgenticPosesRanker — arXiv:2605.03707. Defines the evaluation
  framework we reuse: ground-truth = lowest heavy-atom RMSD pose
  (Eq.10); near-native threshold = RMSD < 2.0 Å (§3.6.3, §3.7.1);
  top-1 best-pose accuracy (Eq.11); Smina baseline ≈ 50%, random
  ≈ 7.7% (§3.7.4).
* BioLM-Score — arXiv:2602.18476. Scoring as the central DL component;
  physical energies too costly for large-scale screening.
* FlowDock — arXiv:2412.10966. *"None [of generative methods] has
  been rigorously benchmarked on pharmacologically relevant targets."*
* DockGen — arXiv:2402.18396. Introduces **Confidence
  Bootstrapping** (a confidence model over diffused poses). Our tool
  is the OSS, dock-agnostic realisation of that idea.
* Expected Calibration Error — Guo et al. 2017, *On Calibration of
  Modern Neural Networks*. Standard ECE formula used verbatim in
  `metrics.py`.

## Feature → paper mapping

| Feature | Source / justification |
|----------|----------------------|
| RMSD < 2.0 Å = near-native | AgenticPosesRanker §3.6.3, §3.7.1 |
| Top-1 accuracy metric | AgenticPosesRanker Eq.11 |
| Confidence calibration need | DiffDock README; DockGen §Confidence Bootstrapping |
| ECE as calibration metric | Guo et al. 2017 |
| "Scoring = bottleneck" thesis | AgenticPosesRanker abstract |

## Real datasets (validation next step — manual download required)

These are **not** auto-downloaded (scripted requests return HTTP 403;
they require a browser / login). Documented here for the user's
validation phase:

* **CASF-2016** — Yang Zhang lab, pdbbind.org.cn. 285 core-set
  complexes, 25 scoring functions benchmarked. The industry
  standard cited by AgenticPosesRanker §3.6.1.
* **PDBbind v2016 core** — pdbbind.org.cn (registration required).
* **PoseBusters** — github.com/plindgre/PoseBusters. Pose-quality
  metrics + ground-truth.
* **DockGen** — github.com/bjing-lab/DockGen. Generalization
  benchmark (cross-proteome).

To validate on real data once downloaded:
`dock-confidence validate --input <docked.sdf> --native <crystal.pdb>
--mode platt --train <calibration_set.json>`.

## Verification status (this repo)

* **AC1–AC8 PASS** on a controlled synthetic fixture (seed-fixed,
  known RMSD + noisy score). See `tests/test_dockconf.py`.
* Real-dataset ECE is the pending scientific validation (AC7 on CASF).
* Honesty note: the `heuristic` calibration mode is a documented
  fallback with higher ECE than `platt`; we report ECE honestly,
  never faked. The reproducible fixture proves the *calibration logic*
  (platt: ECE 0.080 < raw 0.368) without depending on a blocked
  external tarball.

## Limitations

* No GPU required: the calibrator uses physical/score features, not a
  retrained DL model.
* RMSD requires the predicted ligand and native crystal to be the *same*
  molecule (true by construction in docking). Alignment uses Maximum
  Common Substructure matching, robust to atom reordering.
* Out of scope: training a new docking/diffusion model; reimplementing
  a force field; proprietary databases.
