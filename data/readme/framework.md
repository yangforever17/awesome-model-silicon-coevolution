<a id="the-framework"></a>

## The Framework: Layers, Levels, Signals <sub><a href="#readme-top">↑ top</a></sub>

**Three layers.** A computing system that hosts a language model is abstracted into the model layer $M$ (architecture, attention and expert routing, numeric formats, training recipe), the software-stack layer $S$ (compilation, kernels, parallel partitioning, serving) and the hardware layer $H$ (microarchitecture, memory hierarchy, interconnect, RTL, layout). The system pursues a joint objective $J(M, S, H)$ under cost, power and area constraints $C$, for example effective tokens per second per watt.

<div align="center">
  <img src="./assets/tower.png" width="82%" alt="The model, software-stack and silicon tower drawn as three stacked slabs. Silicon at the base, with chips and a wafer, iterates in years; the software stack in the middle, with a compiler terminal and CUDA kernels, iterates in hours; the model on top, a neural network, iterates in months. A robot, the model as designer and workload, stands on top under a halo. On the left, paper planes fly along dotted paths from the robot, one tagged kernels landing on the stack and one tagged RTL landing on the silicon. On the right, people work pulley hoists on the tower's ledges, hauling crates labelled HBM and FLOPs and FP8 and 2:4 up one level at a time; a small drone carrying a crate on a dashed path shows AI starting to carry constraints too.">
  <br>
  <em><b>Figure 2.</b> The model–stack–silicon tower. Design flows down with AI as the designer; constraints flow up, so far hauled almost entirely by people. The drone marks where AI has just begun to carry constraints upward.</em>
</div>

**Co-evolution dynamics.** Each layer is updated by an operator that reads a measurement of the whole system, and the capability of whoever executes the update may itself depend on the system:

```math
\begin{aligned}
X_{t+1} &= f_X\big(X_t,\ y_t;\ \theta_t\big), \qquad y_t = m(M_t, S_t, H_t), \qquad X \in \{M, S, H\} \\
\theta_{t+1} &= g\big(\theta_t;\ M_{t+1}, S_{t+1}, H_{t+1}\big)
\end{aligned}
```

Three properties separate this from static co-design. **The target moves:** while one layer optimizes, the others change. **Step sizes differ by orders of magnitude:** $f_S$ can run hourly, $f_M$ monthly and $f_H$ yearly, so the slowest layer sets the system's pace. **The executor can be inside the system:** when the executor is a language model, $\theta$ is determined by $M$ and trained and run on $S$ and $H$, so the system can act on the hand that improves it.

**Autonomy levels.** AI's autonomy in the R&D loop is defined by which part of the dynamics it has taken over. The catalog focuses on L0–L4; L5 and L6 are the horizon discussed in the survey's outlook.

{{LEVEL_TABLE}}

**Feedback signals.** An update operator is only as good as the signal it reads. Ordered by acquisition cost, the six signal tiers span roughly seven orders of magnitude:

| Signal | What it measures | Typical latency |
| --- | --- | --- |
| **S1** | Syntax and compilation | seconds |
| **S2** | Functional correctness (tests, equivalence checking) | minutes to hours |
| **S3** | Implementation quality: timing, area, power, DRC | hours |
| **S4** | Performance profiling | minutes |
| **S5** | End-to-end measurement on real hardware | hours to days |
| **S6** | Post-silicon and at-scale deployment data | months to years |

Between the expensive tiers, cost models (Roofline, Timeloop, MAESTRO, LLMCompass, Vidur) and scaling laws provide intermediate fidelity; see [Performance models, simulators and scaling laws](#part-foundations).

**The three paths compared** (survey Table 8):

| Path | Main levels | Main signals | Main executor | Typical loop period | Highest-level work |
| --- | --- | --- | --- | --- | --- |
| Model → Silicon | L0–L2 | S1–S3 | LLM agents | design in hours to days; tape-out in years | Design Conductor 2.0 (L3) |
| Model → Stack | L1–L2 | S2, S4–S5 | LLM agents | minutes to hours | AlphaEvolve (L4) |
| Silicon → Model | human-executed | S4–S6 | human teams | months to years | DeepSeek-V3.1 (human cross-layer co-design) |

No path yet has all three of a language-model executor, cross-layer feedback, and an acceptable loop period.

---
