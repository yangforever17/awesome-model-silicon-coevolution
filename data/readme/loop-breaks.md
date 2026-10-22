<a id="where-the-loop-breaks"></a>

## Where the Loop Breaks <sub><a href="#readme-top">↑ top</a></sub>

Place any work by three coordinates (which layer it acts on, which level it reaches, how slow its feedback is) and a mismatch appears: **the higher the level, the fewer the instances.** LLM-driven work mostly sits at L0 and L1; end-to-end L2 delivery arrived in volume only after 2025; L3 has scattered footprints; L4 has one public instance. Cross-layer coupling is not rare. Hardware has shaped models for years, but the cross-layer decisions have always been made by people.

| Layer of the problem | What breaks | Where to read more |
| --- | --- | --- |
| **Physics** | The lower the layer, the slower, costlier and sparser the feedback: compilation in seconds, place-and-route in hours, silicon in years. One chip generation yields one sample, which invites reward hacking and blurs attribution. | [Multi-fidelity optimization](#part-intelligence), [pre-/post-silicon gap](#part-intelligence) |
| **Agents** | Pretraining and post-training removed early bottlenecks (syntax, tool calls, single-module correctness). The binding constraint is now the agent: a horizon of hours against a loop of years, no memory that survives a chip generation, and capability that grows only where verifiable rewards exist. Kernels have profilers and RTL has testbenches, but there is no cross-layer environment to train in. | [Verifiable rewards](#part-intelligence), [training environments](#part-benchmarks) |
| **Ecosystem** | Layers belong to different labs, chip companies, foundries and EDA vendors, with interfaces fixed by contracts and standards. A cross-layer loop needs one executor with read/write access to several layers, which almost only exists inside vertically integrated firms (AlphaEvolve with TPU and Gemini, MTIA, Pangu with Ascend, Qwen with T-Head). | [Closed-loop cases](#part-cases), [outlook](#part-outlook) |

Two measurements would separate real cross-layer progress from parallel single-layer progress: **cross-layer gain**, whether jointly changing two layers beats the sum of changing each alone (the L2/L3 boundary), and **loop period**, the time to complete one round of modification, evaluation and adoption.

---
