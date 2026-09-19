#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
wolframscript_command="$(resolve_wolframscript)"
cd -- "$repository_root"

artifacts=(
    artifacts/exact/cl44-seed.json
    artifacts/exact/split-octonion.json
    artifacts/exact/triality44.json
)
existing=()
for artifact in "${artifacts[@]}"; do
    [[ ! -f "$artifact" ]] || existing+=("$artifact")
done
if ((${#existing[@]} > 0)); then
    "$script_dir/run_logged.sh" logs/phase1-backup-generated-exact-bash.log -- \
        python scripts/backup_files.py "${existing[@]}"
fi

mkdir -p build/phase1
"$script_dir/run_logged.sh" logs/phase1-cl44-seed-bash.log -- \
    "$wolframscript_command" -file scripts/verify_cl44.wls -- artifacts/exact/cl44-seed.json
"$script_dir/run_logged.sh" logs/phase1-split-octonion-bash.log -- \
    "$wolframscript_command" -file scripts/verify_split_octonion.wls -- artifacts/exact/split-octonion.json
"$script_dir/run_logged.sh" logs/phase1-triality44-bash.log -- \
    "$wolframscript_command" -file scripts/verify_triality44.wls -- artifacts/exact/triality44.json
"$script_dir/run_logged.sh" logs/phase1-cl44-seed-repeat-bash.log -- \
    "$wolframscript_command" -file scripts/verify_cl44.wls -- build/phase1/cl44-seed-repeat.json
"$script_dir/run_logged.sh" logs/phase1-split-octonion-repeat-bash.log -- \
    "$wolframscript_command" -file scripts/verify_split_octonion.wls -- build/phase1/split-octonion-repeat.json
"$script_dir/run_logged.sh" logs/phase1-triality44-repeat-bash.log -- \
    "$wolframscript_command" -file scripts/verify_triality44.wls -- build/phase1/triality44-repeat.json
"$script_dir/run_logged.sh" logs/phase1-cl44-independent-bash.log -- \
    python scripts/check_cl44_fixture.py
"$script_dir/run_logged.sh" logs/phase1-split-octonion-independent-bash.log -- \
    python scripts/check_split_octonion_fixture.py
"$script_dir/run_logged.sh" logs/phase1-triality44-independent-bash.log -- \
    python -u scripts/check_triality44_fixture.py
"$script_dir/run_logged.sh" logs/phase1-python-tests-bash.log -- \
    python -m unittest discover -s tests -v

pairs=(
    "artifacts/exact/cl44-seed.json:build/phase1/cl44-seed-repeat.json"
    "artifacts/exact/split-octonion.json:build/phase1/split-octonion-repeat.json"
    "artifacts/exact/triality44.json:build/phase1/triality44-repeat.json"
)
for pair in "${pairs[@]}"; do
    primary="${pair%%:*}"
    repeat="${pair#*:}"
    primary_hash="$(sha256sum "$primary" | cut -d' ' -f1)"
    repeat_hash="$(sha256sum "$repeat" | cut -d' ' -f1)"
    if [[ "$primary_hash" != "$repeat_hash" ]]; then
        printf 'ERROR: repeated exact generation changed bytes: %s\n' "$primary"
        exit 1
    fi
    printf '%s_sha256=%s\n' "$primary" "$primary_hash"
done

printf '%s\n' 'phase1_exact_verification=OK'