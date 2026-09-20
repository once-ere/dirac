#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
wolframscript_command="$(resolve_wolframscript)"
python_command="$(resolve_windows_command python.exe)"
pdflatex_command="$(resolve_miktex_pdflatex)"
cd -- "$repository_root"

generated=(
    artifacts/wolfram/dirac-triality-report.json
    notebooks/DiracTriality.nb
    notebooks/dirac_triality.ipynb
    notebooks/dirac_triality.executed.ipynb
    artifacts/notebooks/jupyter-report.json
    dissertation/dirac-triality.tex
    dissertation/dirac-triality.pdf
)
existing=()
for path in "${generated[@]}"; do
    [[ ! -f "$path" ]] || existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/phase4-backup-generated-publication-bash.log -- \
    "$python_command" scripts/backup_files.py "${existing[@]}"
fi

mkdir -p build/phase4/pdf-a build/phase4/pdf-b
"$script_dir/run_logged.sh" logs/phase4-standalone-wolfram-bash.log -- \
    "$wolframscript_command" -file wolfram/dirac_triality.wls -- \
    artifacts/wolfram/dirac-triality-report.json
"$script_dir/run_logged.sh" logs/phase4-build-mathematica-notebook-bash.log -- \
    "$wolframscript_command" -file scripts/build_mathematica_notebook.wls -- \
    notebooks/DiracTriality.nb
"$script_dir/run_logged.sh" logs/phase4-build-mathematica-notebook-repeat-bash.log -- \
    "$wolframscript_command" -file scripts/build_mathematica_notebook.wls -- \
    build/phase4/DiracTriality-repeat.nb
"$script_dir/run_logged.sh" logs/phase4-verify-mathematica-notebook-bash.log -- \
    "$wolframscript_command" -file scripts/verify_mathematica_notebook.wls -- \
    notebooks/DiracTriality.nb
"$script_dir/run_logged.sh" logs/phase4-build-jupyter-bash.log -- \
    "$python_command" scripts/build_jupyter_notebook.py
"$script_dir/run_logged.sh" logs/phase4-build-jupyter-repeat-bash.log -- \
    "$python_command" scripts/build_jupyter_notebook.py \
        --output build/phase4/dirac_triality-repeat.ipynb
"$script_dir/run_logged.sh" logs/phase4-run-jupyter-bash.log -- \
    "$python_command" scripts/run_jupyter_notebook.py notebooks/dirac_triality.ipynb \
        --output notebooks/dirac_triality.executed.ipynb
"$script_dir/run_logged.sh" logs/phase4-run-jupyter-repeat-bash.log -- \
    "$python_command" scripts/run_jupyter_notebook.py build/phase4/dirac_triality-repeat.ipynb \
        --output build/phase4/dirac_triality-repeat.executed.ipynb
"$script_dir/run_logged.sh" logs/phase4-check-jupyter-bash.log -- \
    "$python_command" scripts/check_jupyter_notebook.py notebooks/dirac_triality.executed.ipynb \
        --repeat build/phase4/dirac_triality-repeat.executed.ipynb
"$script_dir/run_logged.sh" logs/phase4-build-dissertation-tex-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py
"$script_dir/run_logged.sh" logs/phase4-build-dissertation-tex-repeat-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --output build/phase4/dirac-triality-repeat.tex
"$script_dir/run_logged.sh" logs/phase4-build-pdf-a1-bash.log -- \
    "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex
"$script_dir/run_logged.sh" logs/phase4-build-pdf-a2-bash.log -- \
    "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex
"$script_dir/run_logged.sh" logs/phase4-build-pdf-a3-bash.log -- \
    "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -output-directory=build/phase4/pdf-a dissertation/dirac-triality.tex
"$script_dir/run_logged.sh" logs/phase4-build-pdf-b1-bash.log -- \
    "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=dirac-triality -output-directory=build/phase4/pdf-b \
        build/phase4/dirac-triality-repeat.tex
"$script_dir/run_logged.sh" logs/phase4-build-pdf-b2-bash.log -- \
    "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=dirac-triality -output-directory=build/phase4/pdf-b \
        build/phase4/dirac-triality-repeat.tex
"$script_dir/run_logged.sh" logs/phase4-build-pdf-b3-bash.log -- \
    "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=dirac-triality -output-directory=build/phase4/pdf-b \
        build/phase4/dirac-triality-repeat.tex
"$script_dir/run_logged.sh" logs/phase4-check-dissertation-pdf-bash.log -- \
    "$python_command" scripts/check_dissertation_pdf.py \
        build/phase4/pdf-a/dirac-triality.pdf \
        --repeat build/phase4/pdf-b/dirac-triality.pdf
"$script_dir/run_logged.sh" logs/phase4-python-tests-bash.log -- \
    "$python_command" -m unittest discover -s tests -v
"$script_dir/run_logged.sh" logs/phase4-verify-learn-dissertation-bash.log -- \
    bash "$script_dir/verify_learn_dissertation.sh"

pairs=(
    "notebooks/DiracTriality.nb:build/phase4/DiracTriality-repeat.nb"
    "notebooks/dirac_triality.ipynb:build/phase4/dirac_triality-repeat.ipynb"
    "notebooks/dirac_triality.executed.ipynb:build/phase4/dirac_triality-repeat.executed.ipynb"
    "dissertation/dirac-triality.tex:build/phase4/dirac-triality-repeat.tex"
    "build/phase4/pdf-a/dirac-triality.pdf:build/phase4/pdf-b/dirac-triality.pdf"
)
for pair in "${pairs[@]}"; do
    first="${pair%%:*}"
    second="${pair#*:}"
    test "$(sha256sum "$first" | cut -d' ' -f1)" = \
        "$(sha256sum "$second" | cut -d' ' -f1)"
done
! grep -Ei '^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Undefined control sequence' \
    build/phase4/pdf-a/dirac-triality.log build/phase4/pdf-b/dirac-triality.log
cp build/phase4/pdf-a/dirac-triality.pdf dissertation/dirac-triality.pdf

printf 'mathematica_notebook_sha256=%s\n' \
    "$(sha256sum notebooks/DiracTriality.nb | cut -d' ' -f1)"
printf 'jupyter_notebook_sha256=%s\n' \
    "$(sha256sum notebooks/dirac_triality.executed.ipynb | cut -d' ' -f1)"
printf 'dissertation_pdf_sha256=%s\n' \
    "$(sha256sum dissertation/dirac-triality.pdf | cut -d' ' -f1)"
printf 'learn_dissertation_pdf_sha256=%s\n' \
    "$(sha256sum dissertation/Learn_dirac-triality.pdf | cut -d' ' -f1)"
printf '%s\n' 'phase4_publication_verification=OK'