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