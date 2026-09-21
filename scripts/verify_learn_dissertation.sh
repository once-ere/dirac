#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
python_command="$(resolve_windows_command python.exe)"
pdflatex_command="$(resolve_miktex_pdflatex)"
cd -- "$repository_root"

original_pairs=(
    "dissertation/dirac-triality.md:44b76c2d872598ad1b038a8d4ad1293b18885ab228297c921579daa86eeb1381"
    "dissertation/dirac-triality.tex:12df60627b5f11b09ccbbadd9ca38fd2ce7efcfccd769f69fd8280b78a6cec38"
    "dissertation/dirac-triality.pdf:8531af531c91fbf366fbcb30759da63e3881dcc241931698a9f6ee3a6ae0b69e"
)
for pair in "${original_pairs[@]}"; do
    path="${pair%%:*}"
    expected="${pair#*:}"
    actual="$(sha256sum "$path" | cut -d' ' -f1)"
    if [[ "$actual" != "$expected" ]]; then
        printf 'ERROR: original dissertation drifted: %s\n' "$path" >&2
        exit 1
    fi
done

generated=(
    dissertation/Learn_dirac-triality.tex
    dissertation/Learn_dirac-triality.pdf
)
existing=()
for path in "${generated[@]}"; do
    [[ ! -f "$path" ]] || existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/learn-backup-generated-bash.log -- \
        "$python_command" scripts/backup_files.py "${existing[@]}"
fi

rm -rf -- build/learn/verify-pdf-a build/learn/verify-pdf-b
mkdir -p -- build/learn/verify-pdf-a build/learn/verify-pdf-b
"$script_dir/run_logged.sh" logs/learn-build-tex-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers \
        --input dissertation/Learn_dirac-triality.md \
        --output dissertation/Learn_dirac-triality.tex
"$script_dir/run_logged.sh" logs/learn-build-tex-repeat-bash.log -- \
    "$python_command" scripts/build_dissertation_tex.py \
        --strip-heading-numbers \
        --input dissertation/Learn_dirac-triality.md \
        --output build/learn/Learn_dirac-triality-repeat.tex
"$script_dir/run_logged.sh" logs/learn-check-content-bash.log -- \
    "$python_command" scripts/check_learn_dissertation.py

for pass in 1 2 3; do
    "$script_dir/run_logged.sh" "logs/learn-build-pdf-a${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-a \
        dissertation/Learn_dirac-triality.tex
    "$script_dir/run_logged.sh" "logs/learn-build-pdf-b${pass}-bash.log" -- \
        "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
        -jobname=Learn_dirac-triality -output-directory=build/learn/verify-pdf-b \
        build/learn/Learn_dirac-triality-repeat.tex
done

"$script_dir/run_logged.sh" logs/learn-check-pdf-bash.log -- \
    "$python_command" scripts/check_dissertation_pdf.py --edition learn \
        build/learn/verify-pdf-a/Learn_dirac-triality.pdf \
        --repeat build/learn/verify-pdf-b/Learn_dirac-triality.pdf
"$script_dir/run_logged.sh" logs/learn-test-builder-bash.log -- \
    "$python_command" -m unittest discover -s tests -p test_dissertation_builder.py -v
"$script_dir/run_logged.sh" logs/learn-test-content-bash.log -- \
    "$python_command" -m unittest discover -s tests -p test_learn_dissertation.py -v
"$script_dir/run_logged.sh" logs/learn-test-pdf-bash.log -- \
    "$python_command" -m unittest discover -s tests -p test_dissertation_pdf.py -v

test "$(sha256sum dissertation/Learn_dirac-triality.tex | cut -d' ' -f1)" = \
    "$(sha256sum build/learn/Learn_dirac-triality-repeat.tex | cut -d' ' -f1)"
test "$(sha256sum build/learn/verify-pdf-a/Learn_dirac-triality.pdf | cut -d' ' -f1)" = \
    "$(sha256sum build/learn/verify-pdf-b/Learn_dirac-triality.pdf | cut -d' ' -f1)"
! grep -Ei '^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Undefined control sequence' \
    build/learn/verify-pdf-a/Learn_dirac-triality.log \
    build/learn/verify-pdf-b/Learn_dirac-triality.log
cp build/learn/verify-pdf-a/Learn_dirac-triality.pdf \
    dissertation/Learn_dirac-triality.pdf

printf 'learn_markdown_sha256=%s\n' \
    "$(sha256sum dissertation/Learn_dirac-triality.md | cut -d' ' -f1)"
printf 'learn_tex_sha256=%s\n' \
    "$(sha256sum dissertation/Learn_dirac-triality.tex | cut -d' ' -f1)"
printf 'learn_pdf_sha256=%s\n' \
    "$(sha256sum dissertation/Learn_dirac-triality.pdf | cut -d' ' -f1)"
printf '%s\n' 'learn_dissertation_verification=OK'
