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
gitignored; only the `.tex` sources are tracked there.

To clean build artifacts:

```bash
latexmk -C -outdir=out main.tex
```

## Publishing

`docs/simulation-and-cda-theory.pdf` is a tracked, checked-in copy of the
compiled PDF, kept for anyone browsing the repo without a LaTeX toolchain. It
is not regenerated automatically -- after changing the source and
rebuilding, publish an update with:

```bash
cp out/main.pdf ../simulation-and-cda-theory.pdf
```

then commit the result alongside the source changes that produced it.
