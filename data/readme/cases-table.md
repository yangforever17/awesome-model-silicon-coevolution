| Case | Year · source | Loop | Level | Where it breaks |
| --- | --- | --- | :---: | --- |
| NVCell | 2021 · DAC | RL generates standard-cell layouts | L1 | Designer is not the model being trained |
| AlphaTensor | 2022 · Nature | Searches matmul algorithms for specific hardware | L1 | Hardware is fixed |
| PrefixRL | 2022 · DAC | RL prefix circuits shipped in NVIDIA GPUs | L1 | Designer is not the model being trained |
| AlphaDev | 2023 · Nature | Sorting routines merged into LLVM libc++ | L1 | Only software updates |
| AlphaEvolve | 2025 · DeepMind | One agent rewrites a TPU circuit and a Gemini kernel | **L4** | Closed, but one turn is worth ~1% |
| OpenAI × Broadcom | 2025 · interview | ~20 optimizations on human-optimized blocks | Claimed | Cannot be verified |
| MTIA v2 | 2025 · ISCA | Recommendation workloads drive chip design | Human | Executor is not a model |
| Pangu Ultra × Ascend | 2025 · tech report | Model and recipe built around NPUs | Human | Executor is not a model |
| Jalapeño | 2026 · press | Nine months from design to tape-out | Undisclosed | Cannot be verified |
| Qwen chip–model | 2026 · blog | Chip and inference stack adapted in parallel | L2 | The two ends are not connected |
| *Design Conductor 2.0* | 2026 · arXiv | Reads an algorithm paper, designs an accelerator | L3 | Product does not flow back to the designer |

Three failure patterns: the **executor** is not the trained model or is a human team; the **signal** does not flow between the two ends; or the **gain** per turn is too small or cannot be checked.
