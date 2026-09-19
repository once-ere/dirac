#!/usr/bin/env bash

resolve_wolframscript() {
    local executable
    local windows_path
    local shell_command

    if executable="$(command -v wolframscript 2>/dev/null)"; then
        printf '%s\n' "$executable"
        return 0
    fi

    for shell_command in powershell.exe pwsh.exe; do
        command -v "$shell_command" >/dev/null 2>&1 || continue
        windows_path="$(
            "$shell_command" -NoProfile -NonInteractive -Command \
                '(Get-Command wolframscript -ErrorAction Stop).Source' |
                tr -d '\r' |
                tail -n 1
        )"
        [[ -n "$windows_path" ]] || continue
        if command -v wslpath >/dev/null 2>&1; then
            executable="$(wslpath -u "$windows_path")"
        elif command -v cygpath >/dev/null 2>&1; then
            executable="$(cygpath -u "$windows_path")"
        else
            executable="$windows_path"
        fi
        if [[ -f "$executable" ]]; then
            printf '%s\n' "$executable"
            return 0
        fi
    done

    printf '%s\n' 'ERROR: wolframscript was not found' >&2
    return 1
}