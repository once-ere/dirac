[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

if (-not (Get-Command pdflatex.exe -ErrorAction SilentlyContinue)) {
    $miktexBin = Join-Path $env:ProgramFiles "MiKTeX\miktex\bin\x64"
    if (-not (Test-Path -LiteralPath (Join-Path $miktexBin "pdflatex.exe"))) {
        throw "pdflatex.exe was not found on PATH or in $miktexBin"
    }
    $env:Path = "$miktexBin;$env:Path"
}

$generated = @(
    "refinement/phase7-x0-x7/evidence.json",
    "provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex",
    "provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf",
    "provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex",
    "provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf"
)
$existing = @($generated | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase7-backup-generated.log" `
        -Command ("python scripts/backup_files.py " + ($existing -join " "))
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$buildDirectories = @(
    "build\phase7\components-pdf-a",
    "build\phase7\components-pdf-b",
    "build\phase7\numerics-pdf-a",
    "build\phase7\numerics-pdf-b"
)
Remove-Item $buildDirectories -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "build\phase7\evidence-repeat.json" -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $buildDirectories -Force | Out-Null

$steps = @(
    @("logs/phase7-check-components.log", "python refinement/phase7-x0-x7/verify_component_claims.py"),
    @("logs/phase7-build-evidence.log", "python refinement/phase7-x0-x7/build_evidence.py"),
    @("logs/phase7-build-evidence-repeat.log", "python refinement/phase7-x0-x7/build_evidence.py --output build/phase7/evidence-repeat.json"),
    @("logs/phase7-check-exact-model.log", "python scripts/check_einstein_spinor_model.py"),
    @("logs/phase7-check-numerical-output.log", "python scripts/check_einstein_spinor_44.py"),
    @("logs/phase7-check-reports.log", "python scripts/check_phase7_x0_x7_reports.py"),
    @("logs/phase7-tests.log", "python -m unittest tests.test_phase7_x0_x7_refinement tests.test_curved_spin_publications -v"),
    @("logs/phase7-build-components-tex.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md --output provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex"),
    @("logs/phase7-build-components-tex-repeat.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md --output build/phase7/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7-repeat.tex"),
    @("logs/phase7-build-numerics-tex.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md --output provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex"),
    @("logs/phase7-build-numerics-tex-repeat.log", "python scripts/build_dissertation_tex.py --strip-heading-numbers --input provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md --output build/phase7/EINSTEIN_SPINOR_44_NUMERICS_X0_X7-repeat.tex")
)
foreach ($step in $steps) {
    & "$PSScriptRoot\run_logged.ps1" -LogPath $step[0] -Command $step[1]
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

for ($pass = 1; $pass -le 3; $pass++) {
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase7-components-pdf-a$pass.log" `
        -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=EINSTEIN_SPINOR_44_COMPONENTS_X0_X7 -output-directory=build/phase7/components-pdf-a provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase7-components-pdf-b$pass.log" `
        -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=EINSTEIN_SPINOR_44_COMPONENTS_X0_X7 -output-directory=build/phase7/components-pdf-b build/phase7/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7-repeat.tex"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase7-numerics-pdf-a$pass.log" `
        -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=EINSTEIN_SPINOR_44_NUMERICS_X0_X7 -output-directory=build/phase7/numerics-pdf-a provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & "$PSScriptRoot\run_logged.ps1" `
        -LogPath "logs\phase7-numerics-pdf-b$pass.log" `
        -Command "pdflatex -interaction=nonstopmode -halt-on-error -jobname=EINSTEIN_SPINOR_44_NUMERICS_X0_X7 -output-directory=build/phase7/numerics-pdf-b build/phase7/EINSTEIN_SPINOR_44_NUMERICS_X0_X7-repeat.tex"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

& "$PSScriptRoot\run_logged.ps1" `
    -LogPath "logs\phase7-check-components-pdf.log" `
    -Command "python scripts/check_provenance_pdf.py --edition einstein-spinor-44-components-x0-x7 build/phase7/components-pdf-a/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf --repeat build/phase7/components-pdf-b/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& "$PSScriptRoot\run_logged.ps1" `
    -LogPath "logs\phase7-check-numerics-pdf.log" `
    -Command "python scripts/check_provenance_pdf.py --edition einstein-spinor-44-numerics-x0-x7 build/phase7/numerics-pdf-a/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf --repeat build/phase7/numerics-pdf-b/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$pairs = @(
    @("refinement\phase7-x0-x7\evidence.json", "build\phase7\evidence-repeat.json"),
    @("provenance\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex", "build\phase7\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7-repeat.tex"),
    @("provenance\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex", "build\phase7\EINSTEIN_SPINOR_44_NUMERICS_X0_X7-repeat.tex"),
    @("build\phase7\components-pdf-a\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf", "build\phase7\components-pdf-b\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf"),
    @("build\phase7\numerics-pdf-a\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf", "build\phase7\numerics-pdf-b\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf")
)
foreach ($pair in $pairs) {
    $first = (Get-FileHash -LiteralPath $pair[0] -Algorithm SHA256).Hash
    $second = (Get-FileHash -LiteralPath $pair[1] -Algorithm SHA256).Hash
    if ($first -ne $second) {
        throw "generated artifact changed bytes: $($pair[0])"
    }
}

$warningPattern = "^!|LaTeX Warning|Package .* Warning|"
$warningPattern += "Overfull|Underfull|Undefined control sequence"
$issues = Select-String -Path `
    "build\phase7\components-pdf-a\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.log", `
    "build\phase7\components-pdf-b\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.log", `
    "build\phase7\numerics-pdf-a\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.log", `
    "build\phase7\numerics-pdf-b\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.log" `
    -Pattern $warningPattern
if ($issues) {
    $issues | ForEach-Object { Write-Output $_.Line }
    throw "Phase 7 LaTeX warnings remain"
}

Copy-Item "build\phase7\components-pdf-a\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf" `
    "provenance\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf" -Force
Copy-Item "build\phase7\numerics-pdf-a\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf" `
    "provenance\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf" -Force

Write-Output "components_md_sha256=$((Get-FileHash provenance\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "components_tex_sha256=$((Get-FileHash provenance\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "components_pdf_sha256=$((Get-FileHash provenance\EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "numerics_md_sha256=$((Get-FileHash provenance\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "numerics_tex_sha256=$((Get-FileHash provenance\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "numerics_pdf_sha256=$((Get-FileHash provenance\EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "evidence_sha256=$((Get-FileHash refinement\phase7-x0-x7\evidence.json -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "phase7_x0_x7_reports_verification=OK"
exit 0
