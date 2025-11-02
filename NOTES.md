# 📦 ADI Map (by band) — Full Python Project

Below is a complete, ready-to-install Python project using a modern `src/` layout,
packaging via **Hatchling**, a CLI entry point, tests, Ruff/Flake8 config, and
pre-commit hooks.

Copy these files into a new folder (e.g., `adi-map/`) preserving the structure.

---

## Project tree

``` text
adi-map/
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ .gitignore
├─ .pre-commit-config.yaml
├─ src/
│  └─ adimap/
│     ├─ __init__.py
│     ├─ adif.py
│     ├─ maidenhead.py
│     ├─ map_builder.py
│     └─ cli.py
└─ tests/
   ├─ test_adif.py
   └─ test_maidenhead.py
```

---
