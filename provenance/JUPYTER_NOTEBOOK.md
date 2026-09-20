# Deterministic Jupyter notebook provenance

## Artifacts

```text
notebooks/dirac_triality.ipynb
notebooks/dirac_triality.executed.ipynb
artifacts/notebooks/jupyter-report.json
```

The notebook uses a standard Python kernel. It runs the independent exact and
numerical checkers, reads both canonical CSV datasets, validates row counts and
endpoints, checks all source hashes, and writes a six-check JSON report. The
runner removes volatile execution metadata before serialization. Jupyter may
emit adjacent `stdout` fragments either separately or as one stream depending
on kernel message batching. The runner coalesces adjacent streams with the
same channel before serialization, so equivalent output has one canonical
representation.

Canonical executed-notebook SHA-256:

```text
2d998c596ac81be060562ed0d9a324c937b5069521320d95372f6a2dbce6b169
```

## Complete Windows commands

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
python -c "import nbformat, nbclient; print(nbformat.__version__, nbclient.__version__)"
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-build-jupyter.log `
  -Command "python scripts/build_jupyter_notebook.py"
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-build-jupyter-repeat.log `
  -Command "python scripts/build_jupyter_notebook.py --output build/phase4/dirac_triality-repeat.ipynb"
$first = (Get-FileHash notebooks\dirac_triality.ipynb -Algorithm SHA256).Hash
$second = (Get-FileHash build\phase4\dirac_triality-repeat.ipynb -Algorithm SHA256).Hash
if ($first -ne $second) { throw "Jupyter source generation changed bytes" }
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-run-jupyter.log `
  -Command "python scripts/run_jupyter_notebook.py notebooks/dirac_triality.ipynb --output notebooks/dirac_triality.executed.ipynb"
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-run-jupyter-repeat.log `
  -Command "python scripts/run_jupyter_notebook.py build/phase4/dirac_triality-repeat.ipynb --output build/phase4/dirac_triality-repeat.executed.ipynb"
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-check-jupyter.log `
  -Command "python scripts/check_jupyter_notebook.py notebooks/dirac_triality.executed.ipynb --repeat build/phase4/dirac_triality-repeat.executed.ipynb"
```

The checker must report 12 passing checks, five executed code cells, no error
outputs, six passing notebook checks, the canonical executed-notebook hash, and
byte-identical executed notebooks.

## Complete Git Bash or WSL commands

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
source ./scripts/resolve_wolframscript.sh
python_command="$(resolve_windows_command python.exe)"
"$python_command" -c 'import nbformat, nbclient; print(nbformat.__version__, nbclient.__version__)'
./scripts/run_logged.sh logs/phase4-build-jupyter-bash.log -- \
  "$python_command" scripts/build_jupyter_notebook.py
./scripts/run_logged.sh logs/phase4-build-jupyter-repeat-bash.log -- \
  "$python_command" scripts/build_jupyter_notebook.py \
    --output build/phase4/dirac_triality-repeat.ipynb
test "$(sha256sum notebooks/dirac_triality.ipynb | cut -d' ' -f1)" = \
  "$(sha256sum build/phase4/dirac_triality-repeat.ipynb | cut -d' ' -f1)"
./scripts/run_logged.sh logs/phase4-run-jupyter-bash.log -- \
  "$python_command" scripts/run_jupyter_notebook.py notebooks/dirac_triality.ipynb \
    --output notebooks/dirac_triality.executed.ipynb
./scripts/run_logged.sh logs/phase4-run-jupyter-repeat-bash.log -- \
  "$python_command" scripts/run_jupyter_notebook.py build/phase4/dirac_triality-repeat.ipynb \
    --output build/phase4/dirac_triality-repeat.executed.ipynb
./scripts/run_logged.sh logs/phase4-check-jupyter-bash.log -- \
  "$python_command" scripts/check_jupyter_notebook.py \
    notebooks/dirac_triality.executed.ipynb \
    --repeat build/phase4/dirac_triality-repeat.executed.ipynb
```