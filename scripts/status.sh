#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/resolve_wolframscript.sh"
git_command="$(resolve_windows_command git.exe)"
cd -- "$repository_root"

branch="$("$git_command" branch --show-current | tr -d '\r')"
if head="$("$git_command" rev-parse --verify HEAD 2>/dev/null | tr -d '\r')"; then
    :
else
    head="unborn"
fi
phase_tag="$("$git_command" tag --list 'phase5-curved-spin-gravity-green' | tr -d '\r' | head -n 1)"
if [[ -z "$phase_tag" ]]; then
    phase_tag="$("$git_command" tag --list 'learn-dissertation-green' | tr -d '\r' | head -n 1)"
fi
if [[ -z "$phase_tag" ]]; then
    phase_tag="$("$git_command" tag --list 'final-release-green' | tr -d '\r' | head -n 1)"
fi
if [[ -z "$phase_tag" ]]; then
    phase_tag="$("$git_command" tag --list 'phase*' --sort=-creatordate | tr -d '\r' | head -n 1)"
fi
phase_tag="${phase_tag:-none}"
mapfile -t dirty < <("$git_command" status --short | tr -d '\r')

if [[ -f audit/source-manifest.json ]]; then
    if command -v sha256sum >/dev/null 2>&1; then
        manifest_hash="$(sha256sum audit/source-manifest.json | cut -d' ' -f1)"
    else
        manifest_hash="$(shasum -a 256 audit/source-manifest.json | cut -d' ' -f1)"
    fi
else
    manifest_hash="missing"
fi
next_action="$(grep -m 1 '^Next action:' PROGRESS.md | sed 's/^Next action:[[:space:]]*//')"
next_action="${next_action:-missing}"

printf 'repository=%s\n' "$repository_root"
printf 'branch=%s\n' "$branch"
printf 'head=%s\n' "$head"
printf 'dirty_count=%d\n' "${#dirty[@]}"
printf 'latest_phase_tag=%s\n' "$phase_tag"
printf 'source_manifest_sha256=%s\n' "$manifest_hash"
printf '%s\n' 'latest_verification=public phase5 release f9fef6a47b9cb5767c2f1150e9795798bfe8adef'
printf 'next_action=%s\n' "$next_action"
if ((${#dirty[@]} > 0)); then
    printf '%s\n' 'dirty_files_begin'
    printf '%s\n' "${dirty[@]}"
    printf '%s\n' 'dirty_files_end'
fi