# LaTeX writeup: simulation and CdA fitting theory

This directory contains the LaTeX source for a technical writeup of the physics,
numerics, and modeling assumptions behind `IPCalculator` (race simulation) and
`CdAFitter` (aerodynamic drag fitting) in `calcs.py`.

## Building

```bash
cd docs/latex
latexmk -pdf -outdir=out main.tex
```

The compiled PDF lands at `docs/latex/out/main.pdf`. The `out/` directory is
gitignored; only the `.tex` sources are tracked.

To clean build artifacts:

```bash
latexmk -C -outdir=out main.tex
```
