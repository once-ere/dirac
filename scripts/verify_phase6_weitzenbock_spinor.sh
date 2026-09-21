#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
python_command="$(resolve_windows_command python.exe)"
cargo_command="$(resolve_windows_command cargo.exe)"
pdflatex_command="$(resolve_miktex_pdflatex)"
wolframscript_command="$(resolve_wolframscript)"
cd -- "$repository_root"

expected_vendor_commit="d1836e6a279d63a90fe2839a0020123245487e76"
actual_vendor_commit="$(git -C vendor/sundials_rs rev-parse HEAD | tr -d '\r')"
if [[ "$actual_vendor_commit" != "$expected_vendor_commit" ]]; then
    printf '%s\n' 'ERROR: solver submodule commit mismatch' >&2
    exit 1
fi
if [[ -n "$(git -C vendor/sundials_rs status --porcelain)" ]]; then
    printf '%s\n' 'ERROR: solver submodule is dirty' >&2
    exit 1
fi

generated=(
    artifacts/weitzenbock-spin-geometry/geometry.json
    artifacts/weitzenbock-spin-geometry/wolfram-report.json
    studies/weitzenbock_spinor_44/src/generated.rs
    artifacts/weitzenbock-spinor-44/history.csv
    artifacts/weitzenbock-spinor-44/summary.json
    notebooks/DiracTriality.nb
    provenance/WEITZENBOCK_SPINOR_44.tex
    provenance/WEITZENBOCK_SPINOR_44.pdf
)
existing=()
for path in "${generated[@]}"; do
    [[ ! -f "$path" ]] || existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/phase6-backup-generated-bash.log -- \
        "$python_command" scripts/backup_files.py "${existing[@]}"
fi

rm -rf -- \
    build/phase6/pdf-a \
    build/phase6/pdf-b \
    build/phase6/weitzenbock-repeat \
    build/phase6/weitzenbock-refined
mkdir -p -- \
    build/phase6/pdf-a \
    build/phase6/pdf-b \
    build/phase6/weitzenbock-repeat \
    build/phase6/weitzenbock-refined

"$script_dir/run_logged.sh" logs/phase6-build-geometry-bash.log -- \
    "$python_command" scripts/build_weitzenbock_spin_geometry.py
"$script_dir/run_logged.sh" logs/phase6-build-geometry-repeat-bash.log -- \
    "$python_command" scripts/build_weitzenbock_spin_geometry.py \
        --output build/phase6/geometry-repeat.json
"$script_dir/run_logged.sh" logs/phase6-wolfram-geometry-bash.log -- \
    "$wolframscript_command" -file scripts/verify_weitzenbock_spin_geometry.wls -- \
        artifacts/weitzenbock-spin-geometry/wolfram-report.json
"$script_dir/run_logged.sh" logs/phase6-wolfram-geometry-repeat-bash.log -- \
    "$wolframscript_command" -file scripts/verify_weitzenbock_spin_geometry.wls -- \
        build/phase6/wolfram-report-repeat.json
"$script_dir/run_logged.sh" logs/phase6-check-geometry-bash.log -- \
    "$python_command" scripts/check_weitzenbock_spin_geometry.py
"$script_dir/run_logged.sh" logs/phase6-check-model-bash.log -- \
    "$python_command" scripts/check_weitzenbock_spinor_model.py
"$script_dir/run_logged.sh" logs/phase6-generate-constants-bash.log -- \
    "$python_command" scripts/generate_weitzenbock_spinor_constants.py
"$script_dir/run_logged.sh" logs/phase6-generate-constants-repeat-bash.log -- \
    "$python_command" scripts/generate_weitzenbock_spinor_constants.py \
        --output build/phase6/generated-repeat.rs
"$script_dir/run_logged.sh" logs/phase6-cargo-fmt-bash.log -- \
    "$cargo_command" fmt -p weitzenbock_spinor_44 -- --check
"$script_dir/run_logged.sh" logs/phase6-cargo-clippy-bash.log -- \
    "$cargo_command" clippy -p weitzenbock_spinor_44 --all-targets -- -D warnings
"$script_dir/run_logged.sh" logs/phase6-cargo-test-bash.log -- \
    "$cargo_command" test -p weitzenbock_spinor_44
"$script_dir/run_logged.sh" logs/phase6-python-tests-bash.log -- \
    "$python_command" -m unittest discover -s tests -v
"$script_dir/run_logged.sh" logs/phase6-run-bash.log -- \
    "$cargo_command" run --release -p weitzenbock_spinor_44 -- \
        --output artifacts/weitzenbock-spinor-44
"$script_dir/run_logged.sh" logs/phase6-run-repeat-bash.log -- \
    "$cargo_command" run --release -p weitzenbock_spinor_44 -- \
        --output build/phase6/weitzenbock-repeat
"$script_dir/run_logged.sh" logs/phase6-run-refined-bash.log -- \
    "$cargo_command" run --release -p weitzenbock_spinor_44 -- \
        --output build/phase6/weitzenbock-refined \
        --relative-tolerance 1e-12 \
        --absolute-tolerance 1e-14 \
        --maximum-step 0.001
"$script_dir/run_logged.sh" logs/phase6-check-output-bash.log -- \
    "$python_command" scripts/check_weitzenbock_spinor_44.py \
        --repeat build/phase6/weitzenbock-repeat \
        --refined build/phase6/weitzenbock-refined
"$script_dir/run_logged.sh" logs/phase6-build-mathematica-bash.log -- \
    "$wolframscript_command" -file scripts/build_mathematica_notebook.wls -- \
        notebooks/DiracTriality.nb
"$script_dir/run_logged.sh" logs/phase6-build-mathematica-repeat-bash.log -- \
    "$wolframscript_command" -file scripts/build_mathematica_notebook.wls -- \
        build/phase6/DiracTriality-repeat.nb
"$script_dir/run_logged.sh" logs/phase6-check-mathematica-bash.log -- \
    "$wolframscript_command" -file scripts/verify_mathematica_notebook.wls -- \
        notebooks/DiracTriality.nb
"$script_dir/run_logged.sh" logs/phase6-build-tex-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers \
        --input provenance/WEITZENBOCK_SPINOR_44.md \
        --output provenance/WEITZENBOCK_SPINOR_44.tex
"$script_dir/run_logged.sh" logs/phase6-build-tex-repeat-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers \
        --input provenance/WEITZENBOCK_SPINOR_44.md \
        --output build/phase6/WEITZENBOCK_SPINOR_44-repeat.tex

for pass in 1 2 3; do
    "$script_dir/run_logged.sh" "logs/phase6-pdf-a${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=WEITZENBOCK_SPINOR_44 \
        -output-directory=build/phase6/pdf-a \
        provenance/WEITZENBOCK_SPINOR_44.tex
    "$script_dir/run_logged.sh" "logs/phase6-pdf-b${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=WEITZENBOCK_SPINOR_44 \
        -output-directory=build/phase6/pdf-b \
        build/phase6/WEITZENBOCK_SPINOR_44-repeat.tex
done

"$script_dir/run_logged.sh" logs/phase6-check-pdf-bash.log -- \
    "$python_command" scripts/check_provenance_pdf.py \
        --edition weitzenbock-spinor-44 \
        build/phase6/pdf-a/WEITZENBOCK_SPINOR_44.pdf \
        --repeat build/phase6/pdf-b/WEITZENBOCK_SPINOR_44.pdf

pairs=(
    "artifacts/weitzenbock-spin-geometry/geometry.json:build/phase6/geometry-repeat.json"
    "artifacts/weitzenbock-spin-geometry/wolfram-report.json:build/phase6/wolfram-report-repeat.json"
    "studies/weitzenbock_spinor_44/src/generated.rs:build/phase6/generated-repeat.rs"
    "artifacts/weitzenbock-spinor-44/history.csv:build/phase6/weitzenbock-repeat/history.csv"
    "artifacts/weitzenbock-spinor-44/summary.json:build/phase6/weitzenbock-repeat/summary.json"
    "notebooks/DiracTriality.nb:build/phase6/DiracTriality-repeat.nb"
    "provenance/WEITZENBOCK_SPINOR_44.tex:build/phase6/WEITZENBOCK_SPINOR_44-repeat.tex"
    "build/phase6/pdf-a/WEITZENBOCK_SPINOR_44.pdf:build/phase6/pdf-b/WEITZENBOCK_SPINOR_44.pdf"
)
for pair in "${pairs[@]}"; do
    first="${pair%%:*}"
    second="${pair#*:}"
    test "$(sha256sum "$first" | cut -d' ' -f1)" = \
        "$(sha256sum "$second" | cut -d' ' -f1)"
done

warning_pattern='^!|LaTeX Warning|Package .* Warning|'
warning_pattern+='Overfull|Underfull|Undefined control sequence'
! grep -Ei "$warning_pattern" \
    build/phase6/pdf-a/WEITZENBOCK_SPINOR_44.log \
    build/phase6/pdf-b/WEITZENBOCK_SPINOR_44.log
cp build/phase6/pdf-a/WEITZENBOCK_SPINOR_44.pdf \
    provenance/WEITZENBOCK_SPINOR_44.pdf

printf 'vendor_commit=%s\n' "$actual_vendor_commit"
printf 'geometry_sha256=%s\n' \
    "$(sha256sum artifacts/weitzenbock-spin-geometry/geometry.json | cut -d' ' -f1)"
printf 'wolfram_sha256=%s\n' \
    "$(sha256sum artifacts/weitzenbock-spin-geometry/wolfram-report.json | cut -d' ' -f1)"
printf 'history_sha256=%s\n' \
    "$(sha256sum artifacts/weitzenbock-spinor-44/history.csv | cut -d' ' -f1)"
printf 'summary_sha256=%s\n' \
    "$(sha256sum artifacts/weitzenbock-spinor-44/summary.json | cut -d' ' -f1)"
printf 'notebook_sha256=%s\n' \
    "$(sha256sum notebooks/DiracTriality.nb | cut -d' ' -f1)"
printf 'provenance_pdf_sha256=%s\n' \
    "$(sha256sum provenance/WEITZENBOCK_SPINOR_44.pdf | cut -d' ' -f1)"
printf '%s\n' 'phase6_weitzenbock_spinor_verification=OK'