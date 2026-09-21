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
    artifacts/curved-spin-geometry/geometry.json
    artifacts/curved-spin-geometry/wolfram-report.json
    studies/einstein_spinor_44/src/generated.rs
    artifacts/einstein-spinor-44/history.csv
    artifacts/einstein-spinor-44/summary.json
    provenance/CURVED_SPIN_BUNDLE.tex
    provenance/CURVED_SPIN_BUNDLE.pdf
    provenance/EINSTEIN_SPINOR_44.tex
    provenance/EINSTEIN_SPINOR_44.pdf
)
existing=()
for path in "${generated[@]}"; do
    [[ ! -f "$path" ]] || existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/phase5-backup-generated-bash.log -- \
        "$python_command" scripts/backup_files.py "${existing[@]}"
fi

rm -rf -- \
    build/phase5/bundle-pdf-a \
    build/phase5/bundle-pdf-b \
    build/phase5/gravity-pdf-a \
    build/phase5/gravity-pdf-b \
    build/phase5/einstein-spinor-repeat \
    build/phase5/einstein-spinor-refined
mkdir -p -- \
    build/phase5/bundle-pdf-a \
    build/phase5/bundle-pdf-b \
    build/phase5/gravity-pdf-a \
    build/phase5/gravity-pdf-b \
    build/phase5/einstein-spinor-repeat \
    build/phase5/einstein-spinor-refined

"$script_dir/run_logged.sh" logs/phase5-build-geometry-bash.log -- \
    "$python_command" scripts/build_curved_spin_geometry.py
"$script_dir/run_logged.sh" logs/phase5-build-geometry-repeat-bash.log -- \
    "$python_command" scripts/build_curved_spin_geometry.py \
        --output build/phase5/geometry-repeat.json
"$script_dir/run_logged.sh" logs/phase5-wolfram-geometry-bash.log -- \
    "$wolframscript_command" -file scripts/verify_curved_spin_geometry.wls -- \
        artifacts/curved-spin-geometry/wolfram-report.json
"$script_dir/run_logged.sh" logs/phase5-wolfram-geometry-repeat-bash.log -- \
    "$wolframscript_command" -file scripts/verify_curved_spin_geometry.wls -- \
        build/phase5/wolfram-report-repeat.json
"$script_dir/run_logged.sh" logs/phase5-check-geometry-bash.log -- \
    "$python_command" scripts/check_curved_spin_geometry.py
"$script_dir/run_logged.sh" logs/phase5-check-einstein-model-bash.log -- \
    "$python_command" scripts/check_einstein_spinor_model.py
"$script_dir/run_logged.sh" logs/phase5-generate-constants-bash.log -- \
    "$python_command" scripts/generate_einstein_spinor_constants.py
"$script_dir/run_logged.sh" logs/phase5-generate-constants-repeat-bash.log -- \
    "$python_command" scripts/generate_einstein_spinor_constants.py \
        --output build/phase5/einstein-spinor-generated-repeat.rs
"$script_dir/run_logged.sh" logs/phase5-cargo-fmt-bash.log -- \
    "$cargo_command" fmt -p einstein_spinor_44 -- --check
"$script_dir/run_logged.sh" logs/phase5-cargo-clippy-bash.log -- \
    "$cargo_command" clippy -p einstein_spinor_44 --all-targets -- -D warnings
"$script_dir/run_logged.sh" logs/phase5-cargo-test-bash.log -- \
    "$cargo_command" test -p einstein_spinor_44
"$script_dir/run_logged.sh" logs/phase5-python-tests-bash.log -- \
    "$python_command" -m unittest discover -s tests -v
"$script_dir/run_logged.sh" logs/phase5-run-gravity-bash.log -- \
    "$cargo_command" run --release -p einstein_spinor_44 -- \
        --output artifacts/einstein-spinor-44
"$script_dir/run_logged.sh" logs/phase5-run-gravity-repeat-bash.log -- \
    "$cargo_command" run --release -p einstein_spinor_44 -- \
        --output build/phase5/einstein-spinor-repeat
"$script_dir/run_logged.sh" logs/phase5-run-gravity-refined-bash.log -- \
    "$cargo_command" run --release -p einstein_spinor_44 -- \
        --output build/phase5/einstein-spinor-refined \
        --relative-tolerance 1e-12 \
        --absolute-tolerance 1e-14 \
        --maximum-step 0.001
"$script_dir/run_logged.sh" logs/phase5-check-gravity-bash.log -- \
    "$python_command" scripts/check_einstein_spinor_44.py \
        --repeat build/phase5/einstein-spinor-repeat \
        --refined build/phase5/einstein-spinor-refined

for document in CURVED_SPIN_BUNDLE EINSTEIN_SPINOR_44; do
    "$script_dir/run_logged.sh" "logs/phase5-build-${document}-bash.log" -- \
        "$python_command" scripts/build_dissertation_tex.py \
            --strip-heading-numbers \
            --input "provenance/$document.md" \
            --output "provenance/$document.tex"
    "$script_dir/run_logged.sh" \
        "logs/phase5-build-${document}-repeat-bash.log" -- \
        "$python_command" scripts/build_dissertation_tex.py \
            --strip-heading-numbers \
            --input "provenance/$document.md" \
            --output "build/phase5/$document-repeat.tex"
done

for pass in 1 2 3; do
    "$script_dir/run_logged.sh" "logs/phase5-bundle-pdf-a${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=CURVED_SPIN_BUNDLE \
        -output-directory=build/phase5/bundle-pdf-a \
        provenance/CURVED_SPIN_BUNDLE.tex
    "$script_dir/run_logged.sh" "logs/phase5-bundle-pdf-b${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=CURVED_SPIN_BUNDLE \
        -output-directory=build/phase5/bundle-pdf-b \
        build/phase5/CURVED_SPIN_BUNDLE-repeat.tex
    "$script_dir/run_logged.sh" "logs/phase5-gravity-pdf-a${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=EINSTEIN_SPINOR_44 \
        -output-directory=build/phase5/gravity-pdf-a \
        provenance/EINSTEIN_SPINOR_44.tex
    "$script_dir/run_logged.sh" "logs/phase5-gravity-pdf-b${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=EINSTEIN_SPINOR_44 \
        -output-directory=build/phase5/gravity-pdf-b \
        build/phase5/EINSTEIN_SPINOR_44-repeat.tex
done

"$script_dir/run_logged.sh" logs/phase5-check-bundle-pdf-bash.log -- \
    "$python_command" scripts/check_provenance_pdf.py \
        --edition curved-spin-bundle \
        build/phase5/bundle-pdf-a/CURVED_SPIN_BUNDLE.pdf \
        --repeat build/phase5/bundle-pdf-b/CURVED_SPIN_BUNDLE.pdf
"$script_dir/run_logged.sh" logs/phase5-check-gravity-pdf-bash.log -- \
    "$python_command" scripts/check_provenance_pdf.py \
        --edition einstein-spinor-44 \
        build/phase5/gravity-pdf-a/EINSTEIN_SPINOR_44.pdf \
        --repeat build/phase5/gravity-pdf-b/EINSTEIN_SPINOR_44.pdf

pairs=(
    "artifacts/curved-spin-geometry/geometry.json:build/phase5/geometry-repeat.json"
    "artifacts/curved-spin-geometry/wolfram-report.json:build/phase5/wolfram-report-repeat.json"
    "studies/einstein_spinor_44/src/generated.rs:build/phase5/einstein-spinor-generated-repeat.rs"
    "artifacts/einstein-spinor-44/history.csv:build/phase5/einstein-spinor-repeat/history.csv"
    "artifacts/einstein-spinor-44/summary.json:build/phase5/einstein-spinor-repeat/summary.json"
    "provenance/CURVED_SPIN_BUNDLE.tex:build/phase5/CURVED_SPIN_BUNDLE-repeat.tex"
    "provenance/EINSTEIN_SPINOR_44.tex:build/phase5/EINSTEIN_SPINOR_44-repeat.tex"
    "build/phase5/bundle-pdf-a/CURVED_SPIN_BUNDLE.pdf:build/phase5/bundle-pdf-b/CURVED_SPIN_BUNDLE.pdf"
    "build/phase5/gravity-pdf-a/EINSTEIN_SPINOR_44.pdf:build/phase5/gravity-pdf-b/EINSTEIN_SPINOR_44.pdf"
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
    build/phase5/bundle-pdf-a/CURVED_SPIN_BUNDLE.log \
    build/phase5/bundle-pdf-b/CURVED_SPIN_BUNDLE.log \
    build/phase5/gravity-pdf-a/EINSTEIN_SPINOR_44.log \
    build/phase5/gravity-pdf-b/EINSTEIN_SPINOR_44.log
cp build/phase5/bundle-pdf-a/CURVED_SPIN_BUNDLE.pdf \
    provenance/CURVED_SPIN_BUNDLE.pdf
cp build/phase5/gravity-pdf-a/EINSTEIN_SPINOR_44.pdf \
    provenance/EINSTEIN_SPINOR_44.pdf

printf 'vendor_commit=%s\n' "$actual_vendor_commit"
printf 'geometry_sha256=%s\n' \
    "$(sha256sum artifacts/curved-spin-geometry/geometry.json | cut -d' ' -f1)"
printf 'gravity_history_sha256=%s\n' \
    "$(sha256sum artifacts/einstein-spinor-44/history.csv | cut -d' ' -f1)"
printf 'gravity_summary_sha256=%s\n' \
    "$(sha256sum artifacts/einstein-spinor-44/summary.json | cut -d' ' -f1)"
printf 'bundle_pdf_sha256=%s\n' \
    "$(sha256sum provenance/CURVED_SPIN_BUNDLE.pdf | cut -d' ' -f1)"
printf 'gravity_pdf_sha256=%s\n' \
    "$(sha256sum provenance/EINSTEIN_SPINOR_44.pdf | cut -d' ' -f1)"
printf '%s\n' 'phase5_curved_spin_gravity_verification=OK'
