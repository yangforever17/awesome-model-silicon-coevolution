<a id="framework"></a>

## Framework

We split the system into three layers: the **model** $M$, the **software stack** $S$ (compilers, kernels, serving) and the **hardware** $H$ (microarchitecture, RTL, layout). Design flows down, constraints flow up, and each layer moves the target of the others.

<div align="center">
  <img src="./assets/tower.png" width="78%" alt="The model, software-stack and silicon tower. Silicon at the base iterates in years, the software stack in hours, the model in months. A robot on top sends kernels and RTL down; people on the side haul constraints such as HBM, FLOPs, FP8 and 2:4 sparsity up, with a small drone showing AI starting to carry constraints too.">
  <p><sub><b>Figure 3.</b> The model–stack–silicon tower. AI already sends designs down; constraints are still hauled up almost entirely by people.</sub></p>
</div>

**Autonomy levels.** How much of the R&D loop does the AI run? The catalog covers L0–L4; L5–L6 are the horizon.

{{LEVEL_TABLE}}

<details>
<summary><b>Dynamics, feedback signals and the three paths</b></summary>

<br>

Each layer is updated by an operator that reads a measurement of the whole system, and the executor's capability $\theta$ may itself depend on the system:

```math
X_{t+1} = f_X(X_t,\ y_t;\ \theta_t),\quad y_t = m(M_t, S_t, H_t),\quad X \in \{M, S, H\},\qquad \theta_{t+1} = g(\theta_t;\ M_{t+1}, S_{t+1}, H_{t+1})
```

Unlike static co-design, the target moves, the layers update at very different speeds ($f_S$ hourly, $f_M$ monthly, $f_H$ yearly), and when the executor is a language model it can improve the machine it runs on.

**Feedback signals**, by cost: **S1** compilation (seconds) · **S2** functional tests (minutes–hours) · **S3** timing, area, power (hours) · **S4** profiling (minutes) · **S5** end-to-end on hardware (hours–days) · **S6** post-silicon and deployment (months–years).

| Path | Levels | Signals | Executor | Loop period | Highest-level work |
| --- | --- | --- | --- | --- | --- |
| Model → Silicon | L0–L2 | S1–S3 | LLM agents | hours to days; tape-out in years | Design Conductor 2.0 (L3) |
| Model → Stack | L1–L2 | S2, S4–S5 | LLM agents | minutes to hours | AlphaEvolve (L4) |
| Silicon → Model | human | S4–S6 | human teams | months to years | DeepSeek-V3.1 |

</details>

<details>
<summary><b>Where the loop breaks</b></summary>

<br>

| | What breaks |
| --- | --- |
| **Physics** | Lower layers give slower, costlier, sparser feedback: seconds to compile, hours to place and route, years for silicon. |
| **Agents** | Agent horizons are hours while hardware loops take years; nothing remembers across chip generations, and there is no cross-layer environment to train in. |
| **Ecosystem** | The layers belong to different companies. A cross-layer loop needs one executor with access to several layers, which mostly exists only inside vertically integrated firms. |

</details>
