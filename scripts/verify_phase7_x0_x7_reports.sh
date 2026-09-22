#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
python_command="$(resolve_windows_command python.exe)"
pdflatex_command="$(resolve_miktex_pdflatex)"
cd -- "$repository_root"

generated=(
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
    build/phase7/numerics-pdf-b
mkdir -p -- \
    build/phase7/components-pdf-a \
    build/phase7/components-pdf-b \
    build/phase7/numerics-pdf-a \
    build/phase7/numerics-pdf-b

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
printf '%s\n' 'phase7_x0_x7_reports_verification=OK'
