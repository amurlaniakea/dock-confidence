# Mission — dock-confidence

**Qué es:** Herramienta open-source (Python + CLI, AGPL-3.0-or-later) que, dada una pose
proteína-ligando predicha por CUALQUIER dock (DiffDock, AutoDock, Smina, FlowDock,
equiv.), estima una **confianza calibrada** de que la pose es near-native (RMSD < 2.0 Å),
produce una banda de incertidumbre por pose, filtra decoys y emite un reporte de
calibración (ECE, reliability diagram) listo para validación científica y regulatoria.

**Por qué existe (el problema):**
La industria farmacéutica corre docking a escala, pero el *scoring* empírico es el
"cuello de botella principal" (AgenticPosesRanker, arXiv:2605.03707): falla rutinariamente
al rankear poses near-native sobre decoys. ~49.4% de los 8,597 sistemas elegibles en
PDBbind muestran *scoring-function failures* (la pose de menor RMSD NO recibe el mejor score).
Ningún método generativo (DiffDock, FlowDock) está "rigurosamente benchmarked en targets
farmacológicamente relevantes" (FlowDock, arXiv:2412.10966). Y **0 repos OSS** resuelven
la capa de confianza calibrada por pose (señal GitHub: `molecular-docking`=183 repos vs
`docking pose confidence RMSD calibration`=0).

**Por qué ahora:** El modelo generativo ya existe (AlphaFold3, RFdiffusion, DiffDock, DockGen).
Lo que falta es la "capa de confianza" reusable que las empresas necesitan para USAR esos
modelos en decisiones reales. DockGen (arXiv:2402.18396) introduce *Confidence Bootstrapping*
pero como parte de entrenar DiffDock (requiere GPU/entrenamiento). `dock-confidence` lo
democratiza: un calibrador OSS que envuelve cualquier dock sin re-entrenar.

**Diferenciador:** No genera poses (eso ya lo hacen otros). *Verifica y calibra* la fiabilidad
de las poses. Eso lo hace abordable (sin cluster GPU) y monetizable (la empresa paga por
confianza antes de gastar síntesis/cristalografía caras).

**Referencia de altura (AlphaFold):** Este proyecto apunta a la "mitad de la altura de
AlphaFold" en el sub-dominio de validación de docking — el eslabón que falta entre
"generamos miles de poses" y "sabemos cuál es fiable".
