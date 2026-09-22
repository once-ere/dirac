#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
python_command="$(resolve_windows_command python.exe)"
pdflatex_command="$(resolve_miktex_pdflatex)"
git_command="$(resolve_windows_command git.exe)"
cd -- "$repository_root"

expected_vendor_commit="d1836e6a279d63a90fe2839a0020123245487e76"
actual_vendor_commit="$("$git_command" -C vendor/sundials_rs rev-parse HEAD | tr -d '\r')"
if [[ "$actual_vendor_commit" != "$expected_vendor_commit" ]]; then
    printf '%s\n' 'ERROR: solver submodule commit mismatch' >&2
    exit 1
fi
if [[ -n "$("$git_command" -C vendor/sundials_rs status --porcelain)" ]]; then
    printf '%s\n' 'ERROR: solver submodule is dirty' >&2
    exit 1
fi

generated=(DEVELOPER_SUMMARY.tex DEVELOPER_SUMMARY.pdf)
existing=()
for path in "${generated[@]}"; do
    [[ ! -f "$path" ]] || existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/developer-summary-backup-bash.log -- \
        "$python_command" scripts/backup_files.py "${existing[@]}"
fi

rm -rf -- build/developer-summary
mkdir -p -- build/developer-summary/pdf-a build/developer-summary/pdf-b

"$script_dir/run_logged.sh" logs/developer-summary-check-bash.log -- \
    "$python_command" scripts/check_developer_summary.py
"$script_dir/run_logged.sh" logs/developer-summary-build-tex-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers --developer-layout \
        --input DEVELOPER_SUMMARY.md \
        --output DEVELOPER_SUMMARY.tex
"$script_dir/run_logged.sh" logs/developer-summary-build-tex-repeat-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers --developer-layout \
        --input DEVELOPER_SUMMARY.md \
        --output build/developer-summary/DEVELOPER_SUMMARY-repeat.tex

for pass in 1 2 3; do
    "$script_dir/run_logged.sh" "logs/developer-summary-pdf-a${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=DEVELOPER_SUMMARY \
        -output-directory=build/developer-summary/pdf-a \
        DEVELOPER_SUMMARY.tex
    "$script_dir/run_logged.sh" "logs/developer-summary-pdf-b${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=DEVELOPER_SUMMARY \
        -output-directory=build/developer-summary/pdf-b \
        build/developer-summary/DEVELOPER_SUMMARY-repeat.tex
done

cp build/developer-summary/pdf-a/DEVELOPER_SUMMARY.pdf DEVELOPER_SUMMARY.pdf

"$script_dir/run_logged.sh" logs/developer-summary-check-pdf-bash.log -- \
    "$python_command" scripts/check_provenance_pdf.py \
        --edition developer-summary \
        DEVELOPER_SUMMARY.pdf \
        --repeat build/developer-summary/pdf-b/DEVELOPER_SUMMARY.pdf

test "$(sha256sum DEVELOPER_SUMMARY.tex | cut -d' ' -f1)" = \
    "$(sha256sum build/developer-summary/DEVELOPER_SUMMARY-repeat.tex | cut -d' ' -f1)"
test "$(sha256sum DEVELOPER_SUMMARY.pdf | cut -d' ' -f1)" = \
    "$(sha256sum build/developer-summary/pdf-b/DEVELOPER_SUMMARY.pdf | cut -d' ' -f1)"

warning_pattern='^!|LaTeX Warning|Package .* Warning|'
warning_pattern+='Overfull|Underfull|Undefined control sequence'
! grep -Ei "$warning_pattern" \
    build/developer-summary/pdf-a/DEVELOPER_SUMMARY.log \
    build/developer-summary/pdf-b/DEVELOPER_SUMMARY.log

"$script_dir/run_logged.sh" logs/developer-summary-tests-bash.log -- \
    "$python_command" -m unittest discover -s tests -v

printf 'vendor_commit=%s\n' "$actual_vendor_commit"
printf 'developer_summary_md_sha256=%s\n' \
    "$(sha256sum DEVELOPER_SUMMARY.md | cut -d' ' -f1)"
printf 'developer_summary_tex_sha256=%s\n' \
    "$(sha256sum DEVELOPER_SUMMARY.tex | cut -d' ' -f1)"
printf 'developer_summary_pdf_sha256=%s\n' \
    "$(sha256sum DEVELOPER_SUMMARY.pdf | cut -d' ' -f1)"
printf '%s\n' 'developer_summary_verification=OK'
