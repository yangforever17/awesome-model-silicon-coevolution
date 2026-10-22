> This repository accompanies the survey [**When Models Build Their Own Machines: From Silicon to Self-Scaling Intelligence**](#companion-survey) (ACM TODAES, in preparation). Every entry is a reference from the survey, tagged with the layer edge it acts on and, where the survey or the curators can place it, its R&D autonomy level.

Every model runs on a machine it did not design. That is starting to change: language models now write RTL, tune kernels, orchestrate EDA flows and help design the chips that train and serve them. **Co-evolution** treats the model (M), the software stack (S) and the silicon (H) as three layers that keep rewriting each other's objectives: hardware constraints shape the next model, model demands shape the next chip, and every layer chases a target that the other layers have moved. The question this catalog tracks is how far each piece of work pushes that loop around, and who closes it.

<div align="center">
  <img src="./assets/tower.png" width="88%" alt="The model / software-stack / silicon tower. Silicon is the base, the software stack is in the middle and the model is on top; their iteration cadences are years, hours and months. On the left, AI-driven arrows go down from the model to the stack and to silicon. On the right, grey arrows show humans and classical search carrying constraints up from silicon to the stack and from the stack to the model; dashed blue arrows show the emerging paths where AI carries those constraints.">
  <br>
  <em><b>Figure 1.</b> The model–stack–silicon loop. Design flows down with AI as the designer; constraints flow up, so far almost entirely carried by people. Dashed arrows mark the paths where AI has just started to carry constraints upward.</em>
</div>

---
