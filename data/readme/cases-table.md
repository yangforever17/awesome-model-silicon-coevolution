**Where each loop breaks** (survey Tables 6 and 7):

| Case | Year · source | Loop path | Level | Executor | Slowest segment | Where the loop breaks |
| --- | --- | --- | --- | --- | --- | --- |
| NVCell | 2021 · DAC | RL generates standard-cell layouts | L1 | dedicated RL policy | tape-out and volume production (years) | The designer is not the model being trained |
| AlphaTensor | 2022 · Nature | Searches matrix-multiplication algorithms for specific hardware | L1 | RL | on-hardware measurement (minutes) | Hardware is fixed; only the algorithm side updates |
| PrefixRL | 2022 · DAC | RL designs prefix circuits that ship in NVIDIA GPUs | L1 | dedicated RL policy | tape-out and volume production (years) | The designer is not the model being trained |
| AlphaDev | 2023 · Nature | Discovered sorting routines merged into LLVM libc++ | L1 | RL | review and merge | Only the software side updates |
| AlphaEvolve | 2025 · DeepMind | One agent rewrites a TPU circuit and a Gemini kernel | **L4** | LLM agent | tape-out of the hardware change (years) | Closed, but one turn is worth ~1% |
| OpenAI × Broadcom | 2025 · announcement, interview | Models find ~20 optimizations on human-optimized blocks | L1 (claimed) | LLM and humans | undisclosed | Cannot be verified |
| MTIA v2 | 2025 · ISCA | Recommendation workloads drive chip design | Human-driven | human teams | chip generation | Executor is not a language model |
| Pangu Ultra × Ascend | 2025 · tech report | Model architecture and recipe built around NPUs | Human-driven | human teams | model generation | Executor is not a language model |
| Jalapeño | 2026 · press release | Nine months from design to tape-out with model help | Undisclosed | LLM and humans | nine-month tape-out | Cannot be verified |
| Qwen chip–model co-evolution | 2026 · tech blog | Chip-module design and inference-stack adaptation in parallel | L2 | LLM agent | chip-side physical implementation | The two ends are not connected |
| *Design Conductor 2.0* (§4) | 2026 · arXiv | Reads an algorithm paper, designs an accelerator | L3 | LLM agent | FPGA and backend (days) | The product does not flow back to the designing model |

Three patterns emerge. **Executor mismatch:** the loop closes physically, but the designer is not the trained model (PrefixRL, AlphaChip) or is a human team (MTIA, Pangu, DeepSeek). **Signal not connected:** the same executor works on both ends, but no measurement flows between them (Qwen). **Gain too small or invisible:** the loop closes and can be checked, but one turn is worth little (AlphaEvolve), or the gain cannot be checked at all (Jalapeño).
