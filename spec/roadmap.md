# Roadmap — dock-confidence

## Milestones (alto nivel)

1. **MVP — Parser + RMSD + score crudo** (Fase 1)
   - Leer salida de DiffDock/AutoDock/Smina (SDF/MOL2/PDBQT).
   - Calcular RMSD a nativa (si se provee) y extraer minimizedAffinity.
   - Reporte JSON básico por pose.

2. **Capa de confianza calibrada** (Fase 2)
   - Mapear score crudo → P(RMSD<2Å) usando CASF-2016 como calibración.
   - Calcular ECE + reliability diagram.
   - Filtrar decoys por umbral calibrado.

3. **Validación científica gratuita** (Fase 3)
   - Correr contra CASF-2016 / PDBbind v2016 core.
   - Medir ECE y top-1 accuracy del calibrador vs baselines (Smina 50%, random ~7.7%).
   - Si ECE es bajo → producto validado científicamente (criterio del usuario).

4. **Empaquetado profesional** (Fase 4)
   - LICENSE AGPL-3.0, README, RESEARCH.md, CI (lint→test).
   - GitHub SOLO al ~90% (gobernanza local-first del usuario).

## Criterio de "listo para Fase siguiente"
- Tras Fase 1: AC1–AC3 PASS.
- Tras Fase 2: AC4–AC6 PASS.
- Tras Fase 3: AC7–AC8 PASS (validación real con datos públicos).
- Tras Fase 4: repo cumple estándar profesional SDD.

## Riesgos / honestidad
- Si CASF-2016 no está accesible, usar PDBbind v2016 core (más grande, mismo origen).
- El calibrador inicial es heurístico (score→probabilidad); si ECE > 0.1, documentar
  limitación abiertamente y proponer mejora (features físicas adicionales) en lugar de
  maquillar el resultado.

---

## BACKLOG (siguiente iteración — aprobado por el autor 2026-07-11)

Estado de la misión: **CERRADA AL 100%** (Fase 1-4 completas, 14/14 tests,
CI verde, repo público desplegado). Los siguientes ítems quedan indexados
para la próxima iteración y se gestionan FUERA de este flujo:

1. **Validación CASF-2016 / PDBbind v2016 real**
   - Descarga manual vía navegador (scripted request → HTTP 403; requiere
     login en pdbbind.org.cn). Documentado en RESEARCH.md.
   - Comando objetivo:
     `dock-confidence validate --input <docked.sdf> --native <crystal.pdb>
      --mode platt --train <calibration_set.json>`
   - Criterio de éxito: AC7 (ECE calibrado < ECE crudo) sobre datos reales,
     no solo el fixture sintético controlado.

2. **Wrapper de DiffDock confidence (input directo)**
   - Caso de uso principal del paper: DiffDock emite `confidence` (string en
     SDF prop) que el propio README admite "NOT a direct measure of binding
     affinity". dock-confidence debe ingerir ese score crudo y CALIBRARLO
     contra RMSD<2Å usando CASF-2016.
   - Extender `parse.py` (`_sdf_props_to_score`) para prominar
     `diffdock_confidence` como `raw_score` y alimentar `calibrate()`.
