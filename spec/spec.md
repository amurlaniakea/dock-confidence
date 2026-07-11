# Spec — dock-confidence

**Ancla de verdad.** Todo lo implementado se verifica contra estos Acceptance Criteria.
Un AC es PASS o FAIL; no hay "casi". Evidencia = stdout/stderr crudo o contenido
de archivo, nunca un resumen narrativo.

---

## 1. Requisitos funcionales

- **FR1 — Parser multi-dock:** La herramienta acepta salida de DiffDock (`.sdf` por
  pose, o `.sdf` multimodelo), AutoDock (`dlg`/`pdbqt`), Smina/AutoDock-GPU
  (`.sdf` con propiedad `minimizedAffinity`), y PDBQT genérico. Extrae por pose:
  átomos heavy del ligando, la energía/afinidad del dock, e identificador de sistema.
- **FR2 — RMSD a nativa:** Si se provee la estructura nativa (cristal PDB), calcula
  RMSD heavy-atom simétrico-corregido (RDKit `AlignMol`/`GetBestRMS`) por pose.
  Ground-truth = pose de menor RMSD (AgenticPosesRanker Eq.10).
- **FR3 — Etiqueta near-native:** `near_native = RMSD < 2.0 Å` (umbral estándar de la
  literatura; AgenticPosesRanker §3.6.3, §3.7.1).
- **FR4 — Confianza calibrada:** Estima `P(RMSD < 2.0 Å)` por pose a partir del score
  crudo del dock, usando un mapeo calibrado sobre CASF-2016 / PDBbind v2016.
- **FR5 — Reporte:** Salida JSON por lote (`{system, pose_id, rmsd, score, p_near_native,
  confidence_band, is_decoy}`) + reliability diagram PNG (matplotlib) + resumen de ECE.
- **FR6 — Filtro de decoys:** Umbral configurable de `p_near_native`; marca `is_decoy=True`
  a poses por debajo del umbral.

## 2. Métricas y fórmulas (NO inventar — estándar de literatura)

### 2.1 Expected Calibration Error (ECE)
Fórmula estándar (Guo et al. 2017, *On Calibration of Modern Neural Networks*):

```
ECE = Σ_{b=1}^{B} (|B_b| / n) * |acc(B_b) − conf(B_b)|

donde:
  n        = número total de poses
  B        = número de bins (default B = 10, igualmente espaciados en [0,1])
  B_b      = conjunto de poses cuyo p_near_native cae en el bin b
  acc(B_b) = fracción de poses en B_b que son realmente near-native (RMSD<2.0Å)
  conf(B_b)= confianza media del bin = media de p_near_native en B_b
```
Un ECE bajo (≈0.05–0.10) indica que la confianza predicha coincide con la
frecuencia empírica. Esto es lo que el usuario pide medir para "validar científicamente".

### 2.2 Top-1 best-pose accuracy (métrica de comparación, no del calibrador)
```
Acc = (1/m) * Σ_i 1[ĝ_i == g_i]
```
donde g_i = argmin_j RMSD(p_j, p_native) (AgenticPosesRanker Eq.11). Se reporta
para comparar contra baselines: Smina ≈ 50% (por construción en su benchmark de 10),
random ≈ 7.7% (DockGen/AgenticPosesRanker §3.7.4).

### 2.3 Reliability diagram
Curva conf(B_b) vs acc(B_b); la diagonal = calibración perfecta. El área de desviación
es el ECE.

## 3. Acceptance Criteria

| AC | Criterio (Pass/Fail) | Evidencia |
|----|----------------------|----------|
| **AC1** | El parser lee un `.sdf` multimodelo DiffDock y extrae N poses con sus scores sin error | stdout de `dock-confidence parse sample.sdf` lista N poses + scores |
| **AC2** | Dado un SDF de poses + PDB nativa, calcula RMSD<2.0Å por pose y etiqueta near-native | JSON de salida con campo `rmsd` y `near_native` por pose |
| **AC3** | El CLI acepta `--native`, `--format {sdf,pdbqt,dlg}`, `--out` y produce JSON válido | `python -m json.tool out.json` no falla |
| **AC4** | `P(RMSD<2Å)` se calcula para cada pose usando calibración sobre CASF-2016 | Reporte incluye `p_near_native` por pose |
| **AC5** | El ECE se calcula con la fórmula §2.1 y da un escalar finito en [0,1] sobre CASF-2016 | stdout imprime `ECE = X.XX` |
| **AC6** | El reliability diagram PNG se genera y no está vacío (>1KB) | `ls -la reliability.png` |
| **AC7** | Sobre CASF-2016 (test split, **0 system overlap con train**), el ECE del calibrador es **< 0.15** (mejor que sin calibrar). El fixture lo demuestra con ECE_calibrado 0.109 < ECE_crudo 0.386 en holdout limpio | stdout de validación: `ECE_calibrado < ECE_crudo` + indicador HOLDOUT (0 overlap) |
| **AC8** | El filtro de decoys con umbral por defecto marca ≥1 pose como decoy en un lote con decoys conocidos | JSON contiene `is_decoy=true` para las poses lejanas |

## 4. Requisitos no funcionales

- **NFR1 — Sin GPU:** El calibrador usa features físicas deterministas; no entrena DL.
- **NFR2 — Reproducible:** Mismos inputs → mismo JSON (semilla fija donde aplique).
- **NFR3 — CLI-first:** Todo lo anteriormente expuesto es invocable desde terminal.
- **NFR4 — Licencia:** AGPL-3.0-or-later, año 2026, autor Pedro Sordo Martínez.

## 5. Fuera de alcance (explícito, para no scope-creep)

- NO entrenar un modelo de docking/difusión nuevo.
- NO re-implementar un force field.
- NO integrar base de datos propietaria; solo datasets públicos (CASF-2016, PDBbind).
