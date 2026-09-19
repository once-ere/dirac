#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
cargo_command="$(resolve_windows_command cargo)"
cd -- "$repository_root"

expected_vendor_commit="d1836e6a279d63a90fe2839a0020123245487e76"
actual_vendor_commit="$(git -C vendor/sundials_rs rev-parse HEAD)"
if [[ "$actual_vendor_commit" != "$expected_vendor_commit" ]]; then
    printf '%s\n' 'ERROR: solver submodule commit mismatch'
    exit 1
fi
if [[ -n "$(git -C vendor/sundials_rs status --porcelain)" ]]; then
    printf '%s\n' 'ERROR: solver submodule is dirty'
    exit 1
fi

generated=(
    studies/spinor_cosmology/src/generated.rs
    artifacts/spinor-cosmology/background.csv
    artifacts/spinor-cosmology/summary.json
)
existing=()
for path in "${generated[@]}"; do
    [[ ! -f "$path" ]] || existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/phase3-backup-generated-cosmology-bash.log -- \
        python scripts/backup_files.py "${existing[@]}"
fi

mkdir -p build/phase3
"$script_dir/run_logged.sh" logs/phase3-generate-cosmology-constants-bash.log -- \
    python scripts/generate_spinor_cosmology_constants.py
"$script_dir/run_logged.sh" logs/phase3-generate-cosmology-constants-repeat-bash.log -- \
    python scripts/generate_spinor_cosmology_constants.py \
        --output build/phase3/generated-repeat.rs
"$script_dir/run_logged.sh" logs/phase3-cargo-fmt-check-bash.log -- \
    "$cargo_command" fmt -p spinor_cosmology -- --check
"$script_dir/run_logged.sh" logs/phase3-spinor-cosmology-clippy-bash.log -- \
    "$cargo_command" clippy -p spinor_cosmology --all-targets -- -D warnings
"$script_dir/run_logged.sh" logs/phase3-spinor-cosmology-tests-bash.log -- \
    "$cargo_command" test -p spinor_cosmology
"$script_dir/run_logged.sh" logs/phase3-python-tests-bash.log -- \
    python -m unittest discover -s tests -v
"$script_dir/run_logged.sh" logs/phase3-spinor-cosmology-run-bash.log -- \
    "$cargo_command" run --release -p spinor_cosmology -- \
        --output artifacts/spinor-cosmology
"$script_dir/run_logged.sh" logs/phase3-spinor-cosmology-repeat-bash.log -- \
    "$cargo_command" run --release -p spinor_cosmology -- \
        --output build/phase3/spinor-cosmology-repeat
"$script_dir/run_logged.sh" logs/phase3-spinor-cosmology-check-bash.log -- \
    python scripts/check_spinor_cosmology.py \
        --repeat build/phase3/spinor-cosmology-repeat

generated_hash="$(sha256sum studies/spinor_cosmology/src/generated.rs | cut -d' ' -f1)"
repeat_hash="$(sha256sum build/phase3/generated-repeat.rs | cut -d' ' -f1)"
if [[ "$generated_hash" != "$repeat_hash" ]]; then
    printf '%s\n' 'ERROR: generated cosmology constants changed bytes'
    exit 1
fi

printf 'vendor_commit=%s\n' "$actual_vendor_commit"
printf 'generated_constants_sha256=%s\n' "$generated_hash"
printf '%s\n' 'phase3_spinor_cosmology_verification=OK'