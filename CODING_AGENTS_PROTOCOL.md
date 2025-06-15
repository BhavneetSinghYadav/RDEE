# CODING_AGENTS_PROTOCOL.md

## RECURSIVE DYNAMICAL EXISTENCE ENGINE (RDEE)

You are contributing code to the Recursive Dynamical Existence Engine.

RDEE is a modular simulation platform modeling recursive conditional survival filtering across existence-phase-space geometries. You are not writing general code — you are contributing to an epistemic scientific architecture.

---

## 1 — SYSTEM DESIGN PHILOSOPHY

- The system is fully modular.
- Each subsystem operates within strict functional boundaries.
- Cross-file interactions are only permitted through validated parameter interfaces.
- No global hard-coding. Everything flows through controlled parameter pipelines.

---

## 2 — MODULE DIRECTORIES

You are only allowed to modify files inside the following directories:

- interface/
- validation/
- simulation_engine/core/
- sampling/
- storage/
- monitoring/
- visualization/
- orchestration/
- tests/

All files outside these directories are off-limits unless explicitly instructed.

---

## 3 — PRIMARY MODULES & FILES

(Refer to directory structure already scaffolded.)

Each module operates on its own file set. No module may alter files outside its own assigned directory.

---

## 4 — CODING STANDARDS

- Python 3.11+
- Use full type annotations.
- Use full docstrings for every function.
- Use dataclasses where appropriate.
- Handle errors gracefully and explicitly.
- Use only these libraries unless authorized:  
  - numpy, scipy, pandas, h5py, sqlite3, matplotlib, seaborn, plotly.
- Follow PEP8.
- Code must be readable, testable, and modular.

---

## 5 — FUNCTION INTERFACE RULES

- Inputs must be explicitly typed.
- Outputs must be explicitly typed.
- Shared data flows through structured dictionaries or dataclasses.
- No implicit shared state.
- If modifying global data structures, update schema files first.

---

## 6 — BUILDING ORDER

- Build occurs in strict module-by-module sequence.
- No module references downstream modules during early build stages.
- You only write orchestration code once all modules have been built, tested, and integrated.

---

## 7 — FILE SCOPE BOUNDARY

You may only modify files you are assigned for each coding session.  
**Do not create additional files, directories, or classes unless explicitly instructed.**

---

## 8 — TESTING PROTOCOL

- Unit tests are written into `/tests/` directory.
- Tests are executed after each module build before proceeding.

---

## 9 — OUTPUT LIMITS

- Limit any code output to 200–250 lines per Codex session.
- Build system incrementally.
- Avoid attempting full system implementations.

---

## 10 — AGENT BEHAVIOR

- Do not hallucinate.
- Do not refactor prior code.
- Do not create speculative optimizations.
- Ask for clarification rather than making unsafe assumptions.
