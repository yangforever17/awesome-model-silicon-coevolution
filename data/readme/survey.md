<a id="companion-survey"></a>

## Companion Survey <sub><a href="#readme-top">↑ top</a></sub>

**When Models Build Their Own Machines: From Silicon to Self-Scaling Intelligence.** Manuscript in preparation for *ACM Transactions on Design Automation of Electronic Systems (TODAES)*. The link will be added here when the preprint is public.

> Every model runs on a machine it did not design. This is changing. Language models already write RTL, tune kernels and orchestrate EDA flows, and they have begun to take part in designing the chips that train and serve them. When models improve chips and chips train stronger models, the growth of intelligence may break through the software ceiling into a scaling loop that drives itself. We treat the chip as the physical layer of recursive self-improvement, describe the co-evolution of model, software stack and silicon as a dynamical system, and propose AI R&D autonomy levels L0–L6, from design assistance, autonomous optimization and end-to-end design to cross-layer co-design and recursive self-enhancement, with self-expansion and open-ended evolution as the horizon. Mapping roughly 260 works, we find that in three years language models have covered most of the ground *within* a single layer, yet decisions that cross layer boundaries are still made by people, and very few works close the loop between silicon and intelligence. The loop breaks in three places: silicon feedback is slow and sparse, agents' horizons are short, and the ecosystem and its training environments are fragmented.

The survey makes three contributions:

1. **Perspective.** The chip is the physical layer of recursive self-improvement: it sets how fast self-improvement can go, and where humans can still keep watch over it.
2. **Framework.** A dynamical formulation of model–stack–silicon co-evolution, and the L0–L6 autonomy levels derived from it. Every work is placed by three coordinates: the layer it acts on, the level it reaches, and the feedback signal it depends on.
3. **Diagnosis and agenda.** Why the loop breaks at the top (physics, agents, ecosystem), and why cross-layer training environments and system-level world models are the keys to closing it.

---
