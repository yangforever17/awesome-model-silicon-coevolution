| Case | Year · source | Loop | Level | Where it breaks |
| --- | --- | --- | :---: | --- |
| AlphaChip | 2020–24&nbsp;·&nbsp;Nature | RL placement in three TPU generations | L1 | Designer is not the model being trained |
| PrefixRL | 2022&nbsp;·&nbsp;DAC | RL designs parallel prefix circuits for NVIDIA GPUs | L1 | Designer is not the model being trained |
| AlphaEvolve | 2025&nbsp;·&nbsp;DeepMind | One agent rewrites a TPU circuit and a Gemini kernel | **L3[S]** | Closed, but one turn is worth ~1% and the layers do not co-adapt |
| OpenAI × Broadcom, Jalapeño | 2025–26&nbsp;·&nbsp;podcast,&nbsp;press | Models help design the inference chip that serves them, taped out in nine months | Possible L3[H] | Cannot be verified |
| Kimi K3 | 2026&nbsp;·&nbsp;tech&nbsp;report | Kernels for its own modules; a chip prototype for a small model of the same architecture | Possible L3[S] | Kernels adapt one way; the chip does not return to K3 |
| Qwen chip–model | 2026&nbsp;·&nbsp;blog | Chip-block design, inference-stack adaptation and self-directed training | L3[θ] | Self-improvement bypasses the chip and inference ends |
| *Design Conductor 2.0* | 2026&nbsp;·&nbsp;arXiv | Reads an algorithm paper, designs an accelerator | L2 | Product does not flow back to the designer |

Three failure patterns: the **executor** is not the trained model or is a human team; the **signal** does not flow between the two ends; or the **gain** per turn is too small or cannot be checked.
