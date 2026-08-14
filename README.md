# WOTT

A cycling performance desktop GUI app for race simulation and aerodynamic drag (CdA) testing.

## Installation

Download the latest release for your platform from the [Releases](../../releases) page:

- **macOS** — download `WOTT-macOS.zip`, unzip it, and double-click `WOTT.app`
- **Windows** — download `WOTT.exe` and double-click it
- **Linux** — download `WOTT`, make it executable (`chmod +x WOTT`), and run it

No Python installation required — all dependencies are bundled in the download.

## Development setup

Requires Python 3.11.

```bash
git clone <repo-url>
cd wott-project
pip install -r requirements-dev.txt
python main.py
```

### macOS: tkinter import errors

If `python main.py` fails with a `_tkinter` / `libtk8.6.dylib` load error, Homebrew has upgraded
`tcl-tk` past what your pyenv Python was built against. Fix:

```bash
brew install tcl-tk@8
rm -rf "$(pyenv root)/versions/3.11.5"
pyenv install 3.11.5
```

pyenv's `python-build` auto-detects Homebrew's `tcl-tk@8` and links against it — no manual configure flags needed.

## Building the standalone executable

```bash
pyinstaller wott.spec
# output is in dist/
```

Releases are built automatically via GitHub Actions when a version tag is pushed:

```bash
git tag v1.0.0
git push --tags
```