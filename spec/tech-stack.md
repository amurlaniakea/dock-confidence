# Tech Stack — dock-confidence

| Componente | Elección | Justificación |
|-------------|-----------|----------------|
| Lenguaje | Python 3.12 | Estándar de bioinformática; rdkit/numpy nativos |
| CLI | `click` o `argparse` stdlib | MVP sin deps pesadas; click si se complica |
| Parser de poses | `rdkit` (RDKit) + `openbabel` | Lectura de SDF/MOL2/PDBQT de DiffDock/AutoDock/Smina. RDKit extrae minimizedAffinity del SDF (como hace AgenticPosesRanker) |
| Cómputo de RMSD | `rdkit.Chem.rdMolAlign` (RMSD simétrico heavy-atom) | Ground-truth definido por RMSD<2.0Å en la literatura (AgenticPosesRanker Eq.10) |
| Calibración | `numpy` (ECE propio, sin sklearn) | ECE = Expected Calibration Error (Guo et al. 2017). Implementación propia evita sklearn pesado; fórmula estándar |
| Reporte | `json` stdlib + `matplotlib` (reliability diagram) | Salida machine-readable + gráfico para papers |
| Datasets de validación | CASF-2016 (gratuito, U. Michigan) + PDBbind v2016 core | Benchmarks estándar de la industria citados en AgenticPosesRanker §3.6.1 y DockGen |
| Testing | `pytest` | AC verificables por criterio aislado |
| Empaquetado | `pyproject.toml` (package-mode=false) | Tool/app, no librería. Cumple SDD packaging |

**Restricciones de hardware (documentadas en RESEARCH.md):**
- Sin GPU requerida: el calibrador usa features físicas deterministas (energías, contactos),
  NO un modelo DL que haya que entrenar. Esto es el punto clave de abordabilidad.
- RDKit es la única dependencia "pesada"; se instala vía pip en el venv del proyecto.

**Decisión de arquitectura (capa, no modelo):**
El proyecto NO entrena un diffusión/docking. Consume la salida de docks existentes y:
1. Parsea cada pose → features físicas + score crudo del dock.
2. Aplica un calibrador ligero (Platt scaling / isotónico sobre features, o mapeo de
   score→P(RMSD<2Å) vía historia de CASF).
3. Emite P(near-native) calibrada + banda + reporte ECE.
