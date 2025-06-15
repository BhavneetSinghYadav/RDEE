# AGENTS.md

## RECURSIVE DYNAMICAL EXISTENCE ENGINE (RDEE)

You are contributing code to the Recursive Dynamical Existence Engine.

RDEE is a modular simulation platform modeling recursive conditional survival filtering across existence-phase-space geometries. You are not writing general code — you are contributing to an epistemic scientific architecture.

---

## 1 — SYSTEM DESIGN PHILOSOPHY

- The system is fully modular.
- Each subsystem operates within strict functional boundaries.
- Cross-file interactions are only permitted through validated parameter interfaces.
- No global hard-coding. Everything flows through controlled parameter pipelines.
- All parameter schemas are governed by `parameter_schema.py` inside `/interface/`.
- All module files operate with strict file scope isolation.

---

## 2 — MODULE DIRECTORIES

Allowed directories:

- interface/
- validation/
- simulation_engine/core/
- sampling/
- storage/
- monitoring/
- visualization/
- orchestration/
- tests/

No modules may write files outside these authorized directories.

---

## 3 — PRIMARY MODULE FILES

Core module files exist inside these directories.
Each module operates strictly within its assigned file scope.
No module may modify other module files outside its own assigned contract.

---

## 4 — CODING STANDARDS

- Language: Python 3.11+
- Full type annotations required.
- Full docstrings for every function, class, and dataclass.
- Use dataclasses where appropriate.
- All custom exceptions must subclass Python's Exception.
- Handle all errors gracefully with clear exception design.
- Use PEP8-compliant style.
- Maximum 250 lines of code per Codex session.
- No CLI entry points, no __main__, no arbitrary file I/O beyond assigned storage layer.

---

## 5 — ALLOWED LIBRARIES

You may only import the following libraries unless explicitly authorized:

**Scientific & Numeric**

- numpy
- scipy
- pandas

**Storage & Persistence**

- h5py
- sqlite3

**Visualization**

- matplotlib
- seaborn
- plotly

**Sampling**

- random
- itertools

**Dataclass / Typing**

- dataclasses
- typing

**YAML Parsing**

- yaml

**Serialization**

- json

**Filesystem**

- os
- pathlib

**Error Handling**

- builtins (standard Python exceptions)

**Runtime Monitoring**

- time
- datetime

**Strict Limitation**

- No unauthorized network calls
- No external web APIs
- No machine learning libraries
- No heavy neural libraries
- No OS-level system calls

---

## 6 — FUNCTION INTERFACE RULES

- Inputs: explicitly typed dataclasses or primitive types.
- Outputs: explicitly typed return values.
- Shared data must always be passed explicitly — no global variables.
- Use structured dictionaries only where parameter schemas are intentionally flattened for storage or serialization.

---

## 7 — BUILDING ORDER & FILE SEQUENCING

- You may only build modules in assigned order following Codex prompt contracts.
- Files may not import downstream modules unless explicitly authorized.
- Orchestration may only be implemented after all lower subsystems are stabilized, tested, and committed.

---

## 8 — FILE SCOPE BOUNDARY

- You may only modify files you are assigned during each build phase.
- No speculative file creation.
- Do not create speculative optimizations or generalizations unless directly requested.
- No modifications to AGENTS.md, MODULE_EXTENSION.md or PARAMETER_SCHEMA.md during module coding.

---

## 9 — TESTING PROTOCOL

- All modules must have corresponding tests inside `/tests/` directory.
- Unit tests must verify:
  - Function signature compliance
  - Input-output logic correctness
  - Controlled exception raising
  - Scientific model integrity where applicable
- Use pytest-compatible structure.
- Tests will be written under separate Codex prompts.

---

## 10 — AGENT BEHAVIOR

- Do not hallucinate.
- Do not refactor prior code unless explicitly instructed.
- Do not optimize unless safety-verified.
- Prioritize epistemic stability over speculative complexity.
- Strict adherence to all modular decomposition rules is mandatory.
