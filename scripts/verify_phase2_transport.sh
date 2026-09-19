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
    studies/triality_transport/src/generated.rs
    artifacts/triality-transport/trajectory.csv
    artifacts/triality-transport/summary.json
)
existing=()
for path in "${generated[@]}"; do
    [[ ! -f "$path" ]] || existing+=("$path")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/phase2-backup-generated-transport-bash.log -- \
        python scripts/backup_files.py "${existing[@]}"
fi

mkdir -p build/phase2
"$script_dir/run_logged.sh" logs/phase2-generate-triality-constants-bash.log -- \
    python scripts/generate_triality_transport_constants.py
"$script_dir/run_logged.sh" logs/phase2-generate-triality-constants-repeat-bash.log -- \
    python scripts/generate_triality_transport_constants.py \
        --output build/phase2/generated-repeat.rs
"$script_dir/run_logged.sh" logs/phase2-cargo-fmt-check-bash.log -- \
    "$cargo_command" fmt -p triality_transport -- --check
"$script_dir/run_logged.sh" logs/phase2-triality-transport-clippy-bash.log -- \
    "$cargo_command" clippy -p triality_transport --all-targets -- -D warnings
"$script_dir/run_logged.sh" logs/phase2-triality-transport-tests-bash.log -- \
    "$cargo_command" test -p triality_transport
"$script_dir/run_logged.sh" logs/phase2-python-tests-bash.log -- \
    python -m unittest discover -s tests -v
"$script_dir/run_logged.sh" logs/phase2-triality-transport-run-bash.log -- \
    "$cargo_command" run --release -p triality_transport -- --output artifacts/triality-transport
"$script_dir/run_logged.sh" logs/phase2-triality-transport-repeat-bash.log -- \
    "$cargo_command" run --release -p triality_transport -- \
        --output build/phase2/triality-transport-repeat
"$script_dir/run_logged.sh" logs/phase2-triality-transport-check-bash.log -- \
    python scripts/check_triality_transport.py \
        --repeat build/phase2/triality-transport-repeat

generated_hash="$(sha256sum studies/triality_transport/src/generated.rs | cut -d' ' -f1)"
repeat_hash="$(sha256sum build/phase2/generated-repeat.rs | cut -d' ' -f1)"
if [[ "$generated_hash" != "$repeat_hash" ]]; then
    printf '%s\n' 'ERROR: generated Rust constants changed bytes'
    exit 1
fi

printf 'vendor_commit=%s\n' "$actual_vendor_commit"
printf 'generated_constants_sha256=%s\n' "$generated_hash"
printf '%s\n' 'phase2_triality_transport_verification=OK'