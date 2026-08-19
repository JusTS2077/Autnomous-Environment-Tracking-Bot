# Autonomous Mars Rover (Propositional Logic KB Agent)

> **College AI Express Hackathon** | Units 1–4 AI Foundations  
> **Track**: Propositional Logic Knowledge-Based Agent (Resolution & Model Entailment)

---
https://docs.google.com/videos/d/1VjZRDHU012GUij48vpXsCdplp2oowx6sh5-rq3Bkl0U/play?usp=sharing

## 🚀 Scenario & Overview

This repository contains an autonomous **Mars Rover Agent** navigating an unexplored $N \times N$ grid terrain. Unlike basic graph-search agents that have full map visibility upfront, this Knowledge-Based (KB) agent operates under **partial observability (Fog of War)**. The grid contains hidden **Hazard craters ($H$)** and **Radiation anomalies ($R$)**.

The rover uses a **Propositional Logic Inference Engine** to infer cell safety from local sensor percepts (**Breeze $B$** for adjacent hazards, **Glow $G$** for adjacent radiation). The rover moves ONLY to cells that can be **PROVABLY ENTAILED SAFE** ($KB \models S_{x,y}$).

---

## 📁 Repository Structure

```
├── grid.py          # Mars environment: Hidden hazards, radiation, sensor percept model
├── kb_agent.py      # Propositional logic KB: Unit resolution, entailment engine, safe path policy
├── main.py          # Pygame visual renderer (fog of war, safe/hazard/radiation cells) & live log
├── generate_pdf.py  # Automated script generating 1-Page SUMMARY.pdf submission sheet
└── README.md        # Setup guide, PEAS matrix, propositional logic rules, & Big-O complexity
```

---

## ⚙️ Quickstart & Setup

### 1. Requirements
- Python 3.8+
- Pygame (`pip install pygame`)
- ReportLab (`pip install reportlab` - for PDF summary sheet generation)

### 2. Run the Mars Rover Agent
```bash
# Install dependencies
pip install pygame reportlab

# Launch main simulation and live terminal log
python main.py

# Generate 1-Page SUMMARY.pdf for hackathon submission
python generate_pdf.py
```

---

## 🧠 Propositional Logic Formulation (Units 3 & 4)

### 1. Atomic Propositions per Cell $(x, y)$
- $H_{x,y}$: Cell $(x, y)$ contains a Hazard (Crater/Chasm).
- $R_{x,y}$: Cell $(x, y)$ contains a Radiation Anomaly.
- $B_{x,y}$: Breeze / Hazard Sensor Signal perceived at $(x, y)$.
- $G_{x,y}$: Glow / Radiation Sensor Signal perceived at $(x, y)$.
- $S_{x,y}$: Cell $(x, y)$ is Safe $\iff \neg H_{x,y} \land \neg R_{x,y}$.
- $V_{x,y}$: Cell $(x, y)$ has been Visited by the Rover.

### 2. Logical Inference Rules
- **Percept Rule 1 (No Breeze)**: $\neg B_{x,y} \implies \bigwedge_{(nx,ny) \in \text{Adj}} \neg H_{nx,ny}$
- **Percept Rule 2 (Breeze Detected)**: $B_{x,y} \implies \bigvee_{(nx,ny) \in \text{Adj}} H_{nx,ny}$
- **Percept Rule 3 (No Glow)**: $\neg G_{x,y} \implies \bigwedge_{(nx,ny) \in \text{Adj}} \neg R_{nx,ny}$
- **Percept Rule 4 (Glow Detected)**: $G_{x,y} \implies \bigvee_{(nx,ny) \in \text{Adj}} R_{nx,ny}$
- **Safety Entailment Query**: $KB \models S_{nx,ny} \iff (KB \models \neg H_{nx,ny} \land KB \models \neg R_{nx,ny})$

---

## 📊 PEAS Framework Matrix

| PEAS Parameter | Specification |
| :--- | :--- |
| **P**erformance Measure | Reach Goal $(G)$ safely, zero steps into hazard/radiation cells, minimize path steps, minimize KB updates/inferences. |
| **E**nvironment | $10 \times 10$ 2D grid, partially observable (fog of war), deterministic state transitions, static hidden terrain, discrete, single-agent. |
| **A**ctuators | Orthogonal motion commands: `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`. |
| **S**ensors | Local Hazard Sensor ($B_{x,y}$ breeze), Local Radiation Sensor ($G_{x,y}$ glow), Position Sensor $(x, y)$, Goal location sensor $(x_g, y_g)$. |

---

## 🧮 Theoretical & Big-O Complexity Analysis

### 1. Time Complexity: $\mathcal{O}(N^2 \cdot k)$ per step / $\mathcal{O}(2^n)$ General SAT
- **General Propositional Entailment**: Checking $KB \models \alpha$ is co-NP-complete ($\mathcal{O}(2^n)$ worst-case truth table enumeration).
- **Unit Resolution Optimization**: Using Horn-clause / Unit Resolution over 2D grid literals reduces inference to polynomial time $\mathcal{O}(N^2 \cdot k)$ per step, where $N^2 = 100$ grid cells and $k$ is active disjunctive clause count.

### 2. Space Complexity: $\mathcal{O}(N^2)$
- KB stores propositional literal sets ($V, S, H, R, \neg H, \neg R$) and active disjunctive clauses. Total memory is bounded by $\mathcal{O}(N^2)$ states.

---

## 🎥 Split-Screen Video Submission Checklist (60–90 Seconds)

1. **Window Setup**: Arrange Pygame visual window (showing dark fog-of-war, mint safe cells, red hazards, purple radiation) side-by-side with the terminal console.
2. **00:00 - 00:15**: Voiceover introducing team members, GitHub URL, track name, and initial $S_{0,0}$ safe assertion.
3. **00:15 - 01:00**: Live execution showing sensor signals ($B, G$), facts asserted into KB, resolution inferring safe/hazard cells, and rover moving strictly to provably safe cells.
4. **01:00 - 01:15**: Highlight final metrics logged in terminal (Total Time, Steps Taken, Total KB Updates & Inferences).
