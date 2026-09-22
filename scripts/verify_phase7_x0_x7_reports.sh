#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
python_command="$(resolve_windows_command python.exe)"
cargo_command="$(resolve_windows_command cargo.exe)"
pdflatex_command="$(resolve_miktex_pdflatex)"
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
    refinement/phase7-x0-x7/evidence.json
    refinement/phase7-x0-x7/convergence.json
    provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex
    provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf
    provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex
    provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf
)
existing=()
for path in "${generated[@]}"; do
    [[ ! -f "$path" ]] || existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/phase7-backup-generated-bash.log -- \
        "$python_command" scripts/backup_files.py "${existing[@]}"
fi

rm -rf -- \
    build/phase7/components-pdf-a \
    build/phase7/components-pdf-b \
    build/phase7/numerics-pdf-a \
    build/phase7/numerics-pdf-b \
    build/phase7/einstein-spinor-repeat \
    build/phase7/einstein-spinor-refined
rm -f -- build/phase7/evidence-repeat.json
rm -f -- build/phase7/convergence-repeat.json
mkdir -p -- \
    build/phase7/components-pdf-a \
    build/phase7/components-pdf-b \
    build/phase7/numerics-pdf-a \
    build/phase7/numerics-pdf-b \
    build/phase7/einstein-spinor-repeat \
    build/phase7/einstein-spinor-refined

"$script_dir/run_logged.sh" logs/phase7-check-components-bash.log -- \
    "$python_command" refinement/phase7-x0-x7/verify_component_claims.py
"$script_dir/run_logged.sh" logs/phase7-check-exact-model-bash.log -- \
    "$python_command" scripts/check_einstein_spinor_model.py
"$script_dir/run_logged.sh" logs/phase7-cargo-fmt-bash.log -- \
    "$cargo_command" fmt -p einstein_spinor_44 -- --check
"$script_dir/run_logged.sh" logs/phase7-cargo-clippy-bash.log -- \
    "$cargo_command" clippy -p einstein_spinor_44 --all-targets -- -D warnings
"$script_dir/run_logged.sh" logs/phase7-cargo-test-bash.log -- \
    "$cargo_command" test -p einstein_spinor_44
"$script_dir/run_logged.sh" logs/phase7-run-repeat-bash.log -- \
    "$cargo_command" run --release -p einstein_spinor_44 -- \
        --output build/phase7/einstein-spinor-repeat
"$script_dir/run_logged.sh" logs/phase7-run-refined-bash.log -- \
    "$cargo_command" run --release -p einstein_spinor_44 -- \
        --output build/phase7/einstein-spinor-refined \
        --relative-tolerance 1e-12 \
        --absolute-tolerance 1e-14 \
        --maximum-step 0.001
"$script_dir/run_logged.sh" logs/phase7-check-numerical-output-bash.log -- \
    "$python_command" scripts/check_einstein_spinor_44.py \
        --repeat build/phase7/einstein-spinor-repeat \
        --refined build/phase7/einstein-spinor-refined
"$script_dir/run_logged.sh" logs/phase7-build-convergence-bash.log -- \
    "$python_command" refinement/phase7-x0-x7/build_convergence_evidence.py
"$script_dir/run_logged.sh" logs/phase7-build-convergence-repeat-bash.log -- \
    "$python_command" refinement/phase7-x0-x7/build_convergence_evidence.py \
        --output build/phase7/convergence-repeat.json
"$script_dir/run_logged.sh" logs/phase7-build-evidence-bash.log -- \
    "$python_command" refinement/phase7-x0-x7/build_evidence.py
"$script_dir/run_logged.sh" logs/phase7-build-evidence-repeat-bash.log -- \
    "$python_command" refinement/phase7-x0-x7/build_evidence.py \
        --output build/phase7/evidence-repeat.json
"$script_dir/run_logged.sh" logs/phase7-check-reports-bash.log -- \
    "$python_command" scripts/check_phase7_x0_x7_reports.py
"$script_dir/run_logged.sh" logs/phase7-tests-bash.log -- \
    "$python_command" -m unittest \
        tests.test_phase7_x0_x7_refinement \
        tests.test_curved_spin_publications -v

"$script_dir/run_logged.sh" logs/phase7-build-components-tex-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers \
        --input provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md \
        --output provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex
"$script_dir/run_logged.sh" logs/phase7-build-components-tex-repeat-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers \
        --input provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md \
        --output build/phase7/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7-repeat.tex
"$script_dir/run_logged.sh" logs/phase7-build-numerics-tex-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers \
        --input provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md \
        --output provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex
"$script_dir/run_logged.sh" logs/phase7-build-numerics-tex-repeat-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers \
        --input provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md \
        --output build/phase7/EINSTEIN_SPINOR_44_NUMERICS_X0_X7-repeat.tex

for pass in 1 2 3; do
    "$script_dir/run_logged.sh" "logs/phase7-components-pdf-a${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=EINSTEIN_SPINOR_44_COMPONENTS_X0_X7 \
        -output-directory=build/phase7/components-pdf-a \
        provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex
    "$script_dir/run_logged.sh" "logs/phase7-components-pdf-b${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=EINSTEIN_SPINOR_44_COMPONENTS_X0_X7 \
        -output-directory=build/phase7/components-pdf-b \
        build/phase7/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7-repeat.tex
    "$script_dir/run_logged.sh" "logs/phase7-numerics-pdf-a${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=EINSTEIN_SPINOR_44_NUMERICS_X0_X7 \
        -output-directory=build/phase7/numerics-pdf-a \
        provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex
    "$script_dir/run_logged.sh" "logs/phase7-numerics-pdf-b${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=EINSTEIN_SPINOR_44_NUMERICS_X0_X7 \
        -output-directory=build/phase7/numerics-pdf-b \
        build/phase7/EINSTEIN_SPINOR_44_NUMERICS_X0_X7-repeat.tex
done

"$script_dir/run_logged.sh" logs/phase7-check-components-pdf-bash.log -- \
    "$python_command" scripts/check_provenance_pdf.py \
        --edition einstein-spinor-44-components-x0-x7 \
        build/phase7/components-pdf-a/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf \
        --repeat build/phase7/components-pdf-b/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf
"$script_dir/run_logged.sh" logs/phase7-check-numerics-pdf-bash.log -- \
    "$python_command" scripts/check_provenance_pdf.py \
        --edition einstein-spinor-44-numerics-x0-x7 \
        build/phase7/numerics-pdf-a/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf \
        --repeat build/phase7/numerics-pdf-b/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf

pairs=(
    "refinement/phase7-x0-x7/evidence.json:build/phase7/evidence-repeat.json"
    "refinement/phase7-x0-x7/convergence.json:build/phase7/convergence-repeat.json"
    "provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex:build/phase7/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7-repeat.tex"
    "provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex:build/phase7/EINSTEIN_SPINOR_44_NUMERICS_X0_X7-repeat.tex"
    "build/phase7/components-pdf-a/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf:build/phase7/components-pdf-b/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf"
    "build/phase7/numerics-pdf-a/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf:build/phase7/numerics-pdf-b/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf"
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
    build/phase7/components-pdf-a/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.log \
    build/phase7/components-pdf-b/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.log \
    build/phase7/numerics-pdf-a/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.log \
    build/phase7/numerics-pdf-b/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.log

cp build/phase7/components-pdf-a/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf \
    provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf
cp build/phase7/numerics-pdf-a/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf \
    provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf

printf 'components_md_sha256=%s\n' \
    "$(sha256sum provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md | cut -d' ' -f1)"
printf 'components_tex_sha256=%s\n' \
    "$(sha256sum provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex | cut -d' ' -f1)"
printf 'components_pdf_sha256=%s\n' \
    "$(sha256sum provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf | cut -d' ' -f1)"
printf 'numerics_md_sha256=%s\n' \
    "$(sha256sum provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md | cut -d' ' -f1)"
printf 'numerics_tex_sha256=%s\n' \
    "$(sha256sum provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex | cut -d' ' -f1)"
printf 'numerics_pdf_sha256=%s\n' \
    "$(sha256sum provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf | cut -d' ' -f1)"
printf 'evidence_sha256=%s\n' \
    "$(sha256sum refinement/phase7-x0-x7/evidence.json | cut -d' ' -f1)"
printf 'convergence_sha256=%s\n' \
    "$(sha256sum refinement/phase7-x0-x7/convergence.json | cut -d' ' -f1)"
printf 'vendor_commit=%s\n' "$actual_vendor_commit"
printf '%s\n' 'phase7_x0_x7_reports_verification=OK'
