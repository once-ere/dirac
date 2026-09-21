# Implementation progress

Status: Phase 6 content commit
`369df0a80a9738b50880ea3f20846eebb6249a28` is verified from an anonymous
public recursive clone. Release-metadata commit and tagged release
verification are pending.

## Verified checkpoint

- Target: `C:\Users\nsh\Developer\code\vscode\dirac`.
- Git repository is synchronized on branch `main` with all phase and release
  tags pushed to `origin`.
- The local-only `prompt.txt` has frozen hash/size provenance and is ignored;
  the authoritative `19sep26.txt` remains tracked with matching provenance.
- Seven configured source roots contain 5,991 files and 371,942,252 bytes.
- Content-aware classification identifies 209 required Markdown or
  Wolfram-family artifacts; two `.m` files are verified MATLAB sources.
- An independent PowerShell walk matches the manifest file and byte totals.
- All 66 Wolfram sources and notebooks parse without evaluation, failures,
  messages, hash drift, or size drift.
- All 203 text artifacts have complete line and word-stream indexes; six
  Wolfram binary artifacts are hash-only by design.
- The compact `Pre-Universe-GPT5_6_Sol-main` root has a complete human review:
  8 of 8 required artifacts are classified with evidence and disposition.
- The `Pre-Universe_with_Claude-main` root has a complete human review: 67 of
  67 required artifacts are classified without executing or modifying source.
- The `Pre-Universe-main` root has a complete human review: all 8 required
  artifacts are classified, including explicit duplicate and notebook-lineage
  evidence.
- The `Dirac_Matrices-main` root has a complete human review: both required
  artifacts are classified, and the dimensional obstruction to its central
  notebook claim is explicit.
- The `Eternal-DEFLATION-Inflation-main` root has a complete human review: all
  9 required artifacts are classified with notebook-overlap, dependency, and
  self-consistency evidence.
- Every required Markdown or Wolfram artifact in the five Mathematica-heavy
  roots is now human-reviewed; 94 of 209 total audit artifacts are complete.
- All 24 required documents in `SUNDIALS_7_8_Rust_port_for_Windows11-main`
  are reviewed. Current bytes establish no active unsafe code, no FFI, and no
  external Cargo packages; build and numerical parity still require rerun.
- All 91 required documents in `rustSolveIt_Win11_SUNDIALS_7_8_0-main` are
  reviewed: 24 inherited by exact hash and 67 read independently.
- All 209 required audit artifacts now have complete human reviews.
- Every parsed notebook now has a deterministic held authored-cell inventory
  with style, size, SHA-256, and bounded preview; notebook code is not run.
- Eleven fixture tests pass for streaming hashes, content-aware classification,
  deterministic rendering, structural merging, ledger coverage, and atomic
  output replacement.
- Python diagnostics report no errors.
- The complete Phase 0 rebuild passes from frozen inputs: 11 tests, 5,991
  source files, 209 audit artifacts, 66 parsed Wolfram artifacts, 209 complete
  human reviews, and zero parse, message, hash, size, or structural failures.
- The exact-real `Cl(4,4)` seed passes 23 Wolfram checks and 24 independent
  checks: full algebra rank 256, even algebra rank 128, rank-eight half-spin
  projectors, scalar half-spin commutants, and no cross intertwiner.
- Split-octonion multiplication passes 17 Wolfram and 17 independent checks:
  exact unit, conjugation, norm composition, alternativity, 64 integral
  structure constants, and nondegenerate ordinary and para-product tensors.
- Split-real triality passes 25 Wolfram and 24 independent checks: related-
  triple dimension 28, three irreducible pairwise-inequivalent eight-
  dimensional modules, an invariant trilinear form, a six-element outer
  action, and an invertible link to the canonical Clifford representation.
- Fourteen Python tests pass, and two successive generations of every exact
  JSON fixture are byte-identical.
- The solver engine is a read-only submodule pinned to
  `d1836e6a279d63a90fe2839a0020123245487e76`; all 1,713 tracked files match
  the audited solver copy.
- The application-owned 24-state triality transport study builds and lints
  warning-free, passes three Rust tests and 15 output checks, and produces
  byte-identical repeated CSV and JSON runs in PowerShell and WSL.
- The 18-state real homogeneous nonlinear-spinor cosmology builds and lints
  warning-free, passes three Rust tests and 17 output checks, and produces
  byte-identical 1,201-row background histories in PowerShell and WSL.
- The standalone WolframScript report passes all 69 exact and numerical
  checks without failures.
- The generated Mathematica notebook has 22 fixed cells and 14 executable
  input cells; fresh-kernel execution has zero failures, zero messages, and
  five passing notebook checks.
- The deterministic Jupyter notebook has ten fixed-ID cells and five executed
  code cells; all 12 structural, result, canonical-hash, and replay checks pass.
- The 598-line Markdown dissertation generates a complete 571-line LaTeX
  source and a warning-free, 13-page letter-sized PDF. Independent builds are
  byte-identical in PowerShell and WSL.
- Both Phase 4 publication gates pass, including six PDF structure and hash
  checks and all 21 Python tests.
- The parallel Learn edition contains 25 chapters, 16 worked examples,
  16 misconception checks, 18 exercises with 18 complete solutions, 47
  glossary entries, a notation index, reference capsules, and a
  claim-to-evidence map. Its 18 content checks and six PDF checks pass.
- The Learn edition's 2,825-line Markdown source generates a deterministic
  2,394-line standalone LaTeX document and a warning-free, 62-page
  letter-sized PDF. Both isolated three-pass builds are byte-identical.
- The expanded Python suite contains 27 tests. Local PowerShell and Bash/WSL
  gates pass for Phases 0 through 4 and the focused Learn publication gate.
- The exact curved `(4,4)` fixture defines the rank-16 real spinor bundle and
  records `eta`, `e`, `g=e eta e^T`, 21 Christoffel symbols, and 14 nonzero
  lowered spin-connection components. Its generator passes 12 checks, the
  independent Wolfram derivation passes 11, and the independent Python
  derivation passes 16.
- The canonical derivative uses
  `D_mu=partial_mu+(1/8)omega_muab[gamma^a,gamma^b]` with both ordered tangent
  indices summed. The full vielbein postulate and the homogeneous contraction
  `gamma^4(partial_t+7H/2)` are verified exactly.
- The application-owned Einstein-spinor study has 18 real states, no scalar
  field, and no cosmological constant. Four independent exact checks derive
  the action stress tensor and full Einstein tensor, including all
  off-diagonal components. It also passes four Rust tests and 24 release
  output checks, including five-point finite differences for all state
  equations, deterministic replay, and comparison with a tighter solve.
- The selected potential `V(S)=S/20+(19/20)S^(1/5)` separates a dust-like
  term from a negative-pressure term. The run uses 1,372 CVODE steps and 1,486
  right-hand-side evaluations; maximum relative condensate, density, and
  Friedmann errors are below `7.5e-9`.
- The standalone curved-bundle and Einstein-spinor provenance sources generate
  warning-free, letter-sized 16-page and 21-page PDFs. Independent three-pass
  builds are byte-identical in PowerShell and Bash.
- The expanded Python suite contains 33 tests. Both complete local Phase 5
  gates pass with zero failed checks and preserve all prior canonical hashes.
- The Dirac-Weitzenböck geometry generator passes 15 exact checks. Independent
  Python and Wolfram reconstructions pass 20 and 15 checks, respectively:
  metric compatibility, the full vielbein postulate, zero curvature, nonzero
  torsion, the contortion decomposition, `T=42 H^2`, `R_LC=-T+B`, and the
  homogeneous spinor-operator identity.
- The Weitzenböck spinor model passes 13 exact rational action and
  field-equation checks, seven Rust tests, and 34 numerical-output checks.
  Its application-owned RHS and CVODE integration have no dependency on the
  Phase 5 application; exact state agreement is an external result. Its 171-row
  canonical run uses 1,372 CVODE steps and 1,486 RHS evaluations; deterministic
  replay is byte-identical and the refined solution differs by at most
  `6.310776406656671e-10` in normalized state values.
- The generated Mathematica notebook now has 29 fixed cells and 20 executable
  inputs. Fresh-kernel execution has zero failures, zero messages, and nine
  passing checks spanning both connection choices and all four numerical
  summaries.
- The standalone Weitzenböck provenance Markdown generates deterministic
  LaTeX and a warning-free, letter-sized 19-page PDF. Independent three-pass
  builds are byte-identical and pass all six PDF checks.
- The expanded Python suite contains 38 tests. The complete local Phase 6
  PowerShell gate passes with zero failed checks.

## Phase checkpoints

### Phase 0: source audit and repository bootstrap

- Commit: `763b1734512adf196ccf1465a77875a1a20c21b6`
- Tag: `phase0-source-audit-green`
- Result: 5,991 files and 371,942,252 bytes frozen; 209 of 209 required
  artifacts reviewed; 66 of 66 parseable Wolfram artifacts imported without
  evaluation; 11 tests passed; zero parse, message, hash, size, or structural
  failures.
- Logs: `logs/phase0-verify-tests.log`,
  `logs/phase0-verify-manifest.log`, `logs/phase0-verify-wolfram.log`,
  `logs/phase0-verify-structural.log`, and `logs/phase0-verify-check.log`.
- Next action: construct and verify the exact-real 16-by-16 `Cl(4,4)` seed.

### Phase 1: exact algebra and split-real triality

- Commit: `07ed08d46d194f72e4fbea89df6fdeedfa61eafe`
- Tag: `phase1-exact-triality-green`
- `artifacts/exact/cl44-seed.json` SHA-256:
  `0660e436fdcf90ed0f0481c9a828e92659987f5820084ccbf5e1dfc96866cc54`.
- `artifacts/exact/split-octonion.json` SHA-256:
  `25044ea194c1e18e40341da1f0098b80bfeb9f4bcb6e7665a32d03f55ac360ca`.
- `artifacts/exact/triality44.json` SHA-256:
  `5985f5c0fdd6656c3c9f572ef1a5d06eee21aabe44cc9bf33747bb79b5e181dd`.
- Verification: `scripts/verify_phase1.ps1` or
  `scripts/verify_phase1.sh`.
- Provenance: `provenance/CL44_SEED.md` and
  `provenance/SPLIT_OCTONION_TRIALITY.md`.
- Next action: build the application-owned 24-state triality transport study
  against the hash-pinned, read-only CVODE engine.

### Phase 2: 24-state triality transport

- Commit: `1b7ba925c1bb8b830494a70d0dba3e7fd467991b`
- Tag: `phase2-triality-transport-green`
- Solver commit:
  `d1836e6a279d63a90fe2839a0020123245487e76`.
- Generated constants SHA-256:
  `932cc651e4212b35064f0419763ee9145f4c67fc7ba45f3f59ee7f90dbb03edc`.
- Trajectory SHA-256:
  `ee5ad82ee604f072f04bed8ef20cdd856bb02ba80e16c3973b10c6c43f972b9c`.
- Summary SHA-256:
  `61b8fe5a8a72e48d40d40d6850a6c559e2dd06ccfa9de97982590d35a82044fb`.
- Result: 41 samples, 237 CVODE steps, 251 RHS evaluations, and all four
  invariant drifts below `3.1e-12`.
- Verification: `scripts/verify_phase2_transport.ps1` or
  `scripts/verify_phase2_transport.sh`.
- Provenance: `provenance/TRIALITY_TRANSPORT.md`.
- Next action: implement the real homogeneous nonlinear-spinor cosmology
  study with independent analytic background checks.

### Phase 3: real homogeneous nonlinear-spinor cosmology

- Commit: `e6d149a061a087f55621ed95ce0203738bcae932`
- Tag: `phase3-spinor-cosmology-green`
- Generated constants SHA-256:
  `cc2131fc739b0bdc4ae9e9146ccb57e47e7ed12aadabcef42ef1263df3de9c7b`.
- Background SHA-256:
  `8a6f7ace34949d82d4022a9b5a660733ed018c91b2b931d934aab7793b5585c2`.
- Summary SHA-256:
  `8f1e45a37c14cc10c7c6b6469ceca7c65e7b9ffc08b3c9dd5bfc518065c590db`.
- Result: 1,201 samples, 711 CVODE steps, 783 RHS evaluations, and maximum
  relative errors below `7.8e-9` for condensate dilution, analytic density,
  potential reconstruction, and Friedmann closure.
- Verification: `scripts/verify_phase3_cosmology.ps1` or
  `scripts/verify_phase3_cosmology.sh`.
- Provenance: `provenance/SPINOR_COSMOLOGY.md`.
- Next action: generate and execute standalone Mathematica and deterministic
  Jupyter notebooks from the verified exact and numerical artifacts.

### Phase 4: notebooks and publication artifacts

- Commit: `ab030d78a60d220f69f30aa7a9d587785e4c6f52`
- Tag: `phase4-publication-green`
- Standalone report SHA-256:
  `22df4baa803043179ad141472d7308a0977d6016e05f16583b3901bd53d93356`.
- Mathematica notebook SHA-256:
  `e1c69e86982dd2ce9b887e5ad0e0e27e4dc78ff4550e568c63cb41764ddcdba1`.
- Jupyter source notebook SHA-256:
  `5813727a077a9afcc881e86928e7e48376056d48ce31409fb5c28e00d0844411`.
- Executed Jupyter notebook SHA-256:
  `2d998c596ac81be060562ed0d9a324c937b5069521320d95372f6a2dbce6b169`.
- Dissertation Markdown SHA-256:
  `47d280353a02c37778775720cf2459b9866510bc89ddb1bbb83c6da2d3504b97`.
- Dissertation LaTeX SHA-256:
  `414b966295ae8f5092553c1af5f339683a67bf8ed77844eb118751713795bfd0`.
- Dissertation PDF SHA-256:
  `a2a6e366817cb17d4b4ba936a98f5e495a8ca9c0bc012540021bc548847073f3`.
- Result: standalone Wolfram evaluation, fresh-kernel Mathematica execution,
  deterministic Jupyter execution, deterministic LaTeX generation, and two
  isolated three-pass PDF builds pass in PowerShell and WSL; the PDF has 13
  pages, one letter-sized media box, its canonical hash, and no TeX warnings
  or errors.
- Checkout attributes pin each generated text artifact to its writer's
  deterministic line endings, preventing `core.autocrlf` from changing hashes.
- The root `prompt.txt` is local-only and ignored; Phase 0 validates its tracked
  pre-bootstrap hash record and any available local backup bytes without
  requiring the private root file in fresh clones.
- Phase 0 serializes repository-relative configuration provenance and pins
  audit outputs to LF, so a full audit rebuild is checkout-location independent.
- Verification: `scripts/verify_phase4_publication.ps1` or
  `scripts/verify_phase4_publication.sh`.
- Provenance: `provenance/WOLFRAMSCRIPT.md`,
  `provenance/MATHEMATICA_NOTEBOOK.md`,
  `provenance/JUPYTER_NOTEBOOK.md`, and `provenance/DISSERTATION.md`.
- Next action: run every phase gate from a fresh recursive clone, compare all
  canonical artifact hashes, and freeze the final verified release.

### Final release verification

- Verified commit: `f18d12fb3a798917edd132d9d57ea10653228b51`.
- Tag: `final-release-green`.
- A new recursive clone passed every Phase 0 through Phase 4 gate against the
  pinned solver submodule at
  `d1836e6a279d63a90fe2839a0020123245487e76`.
- Phase 0 regenerated all six audit outputs with zero tracked drift: 5,991
  source files, 371,942,252 bytes, 209 reviewed audit artifacts, and 66
  message-free Wolfram parses.
- Phase 1 passed 23+24 Clifford, 17+17 split-octonion, and 25+24 triality
  checks with zero failures.
- Phases 2 and 3 passed six Rust tests, 32 numerical-output checks, and
  deterministic replay of both canonical studies.
- Phase 4 passed 69 standalone Wolfram checks, five Mathematica notebook
  checks, 12 Jupyter checks, six PDF checks, and all 21 Python tests.
- All 15 canonical exact, numerical, notebook, report, dissertation, and PDF
  artifacts matched the source checkout byte-for-byte; the rebuilt checkout
  had zero tracked changes.
- The remote tree contains all four files under `wolfram/` and no
  `prompt.txt`.

### Self-contained Learn dissertation

- Verified content commit:
  `b96355c73121c3a79ded52a1594a3704957c5081`.
- Verified release commit:
  `b4646d80ca9764b6bb2cd5c2ae9d9298da3c8360`.
- Annotated tag: `learn-dissertation-green`; remote tag object
  `0ea232b13dc07b83fd4246b8aee33f26b48b3bc9` peels to the verified release
  commit.
- The teaching edition is parallel to the original and does not replace it.
  The original Markdown, LaTeX, and PDF retain their frozen SHA-256 values:
  `47d280353a02c37778775720cf2459b9866510bc89ddb1bbb83c6da2d3504b97`,
  `414b966295ae8f5092553c1af5f339683a67bf8ed77844eb118751713795bfd0`,
  and `a2a6e366817cb17d4b4ba936a98f5e495a8ca9c0bc012540021bc548847073f3`.
- `dissertation/Learn_dirac-triality.md` SHA-256:
  `a8cf09e1ea1860bdbef3125ef01dbf3bc0c5f5a3e9a7adc4fe6c92f534abce58`.
- `dissertation/Learn_dirac-triality.tex` SHA-256:
  `ee325930f4f45540957c9bc6dd166e4c610aa479291273e8636d87382464405f`.
- `dissertation/Learn_dirac-triality.pdf` SHA-256:
  `134bd5dba9751e7972463c17a6074a3ac440d031c1a4a9ae44212a8d8fbcf521`.
- The source has 85,702 bytes, 2,825 newline-terminated lines, and 13,146
  checker-counted words. The generated TeX has 99,832 bytes and 2,394
  newline-terminated lines. The PDF has 669,155 bytes, 62 pages, and one
  `612 x 792` point media box.
- The content checker recomputes the Clifford chirality coordinates,
  split-octonion products and associator, cyclic para-product value, triality
  ranks, and both numerical summaries from canonical fixtures. All 18 checks
  pass, including complete exercise/solution parity and self-containment.
- A separate mathematical review found no high-severity issue. The final text
  incorporates precise global `Pin`/`Spin` scope, algebraic highest-weight
  scope, the exact reflection and intertwiner conventions, the transport
  generator signs, the specified odd cosmology generator, and the dependence
  of the Friedmann diagnostic on the density comparison.
- Two isolated three-pass builds are byte-identical and have zero TeX errors,
  warnings, overfull boxes, underfull boxes, or undefined controls. Extracted
  text and representative rendered pages from the beginning, middle,
  exercises, and conclusion were inspected successfully.
- A local recursive clone at the content commit passed every PowerShell
  Phase 0 through Phase 4 gate against solver submodule commit
  `d1836e6a279d63a90fe2839a0020123245487e76`. All six dissertation hashes
  matched, and the clone had zero tracked drift after regeneration. Its only
  untracked outputs were six hash-verified backup-manifest directories created
  by the gates.
- An anonymous recursive clone from `https://github.com/once-ere/dirac.git`
  resolved to the verified release commit and the same pinned solver commit.
  It passed all five PowerShell phase gates: Phase 0 checked 5,991 source
  files, 209 audited artifacts, 66 Wolfram artifacts, and 27 Python tests;
  Phases 1 through 3 reproduced the exact fixtures and both CVODE studies;
  Phase 4 passed the standalone Wolfram, Mathematica, Jupyter, original
  dissertation, and Learn dissertation checks. All six dissertation hashes
  matched and `git diff --exit-code` reported zero tracked drift after every
  phase.
- The final anonymous clone also passed the complete Bash/WSL and PowerShell
  Phase 4 publication gates at the same commit. Shell scripts were pinned to
  LF for fresh Windows checkouts, and adjacent Jupyter streams were
  canonicalized before serialization; both shells reproduced the same
  executed-notebook, original-PDF, and Learn-PDF hashes.
- Jupyter stream output is canonicalized by merging adjacent fragments from
  the same channel. Two public-clone executions now reproduce the normalized
  hash `2d998c596ac81be060562ed0d9a324c937b5069521320d95372f6a2dbce6b169`
  byte-for-byte under both PowerShell and Bash/WSL publication gates.
- Verification: `scripts/verify_learn_dissertation.ps1` or
  `scripts/verify_learn_dissertation.sh`.
- Provenance: `provenance/LEARN_DISSERTATION.md`.
- Result: `main` and `learn-dissertation-green` are published; the tag points
  to the release commit verified from the public clone.

### Phase 5: curved spin bundle and Einstein-spinor gravity

- Publicly verified content commit:
  `88ce2220c144fa9487243f8d47e961f95f27461e`.
- Verified release commit:
  `f9fef6a47b9cb5767c2f1150e9795798bfe8adef`.
- Annotated tag: `phase5-curved-spin-gravity-green`; remote tag object
  `84e2954a47b0e3297c26b38e58b754447062b445` peels to the verified release
  commit.
- Curved geometry fixture SHA-256:
  `6b5eab6b001d69c5face7b179af8a27e3cfe254cf80bc740cdcb7a2855fcdf67`.
- Independent Wolfram geometry report SHA-256:
  `f81a902f7efc2a36bef1bacdbc4682a278f4907383970a8383f565efd602dc38`.
- Generated spinor constants SHA-256:
  `fa3aba370c1039f17b83fe86a65d75e45be6448aa7bd025dc0db6d0e79e61f60`.
- Einstein-spinor history SHA-256:
  `9553b36f201ef43a92c7de3fe2f46457a592e55285e6220d8aa7af6e36a26f9c`.
- Einstein-spinor summary SHA-256:
  `6b15d084178d01aaed37b84b4bcf8f5246a6941bbe8366ad9c0c3db099eea0f1`.
- Curved-bundle Markdown, LaTeX, and PDF SHA-256 values:
  `83bb78934b9b4986d8ae755319d9fb654e1c68dfc5f05ab6217839689e4184f7`,
  `55b94966a83b007c37543a6875210a83594165efad024f3e52571d7d4370469c`,
  and `588a83a2a5d7f66c5c11f0aeb682f3b32f3e314f9ea73cc16876790bb3a257be`.
- Einstein-spinor Markdown, LaTeX, and PDF SHA-256 values:
  `0a38c49921735b27dc82e72acb8fa69ecb7f5e79c08d195a690dd00049c6fc5e`,
  `58d55a27362add0a73b35e5561b0500c0a2fbfe20cd17a5891c789aee5877c6c`,
  and `3bb9fb215135852f4f2f8f444686de69665ee28ea5198705104d2b46c4801251`.
- Verification: `scripts/verify_phase5_curved_spin_gravity.ps1` or
  `scripts/verify_phase5_curved_spin_gravity.sh`.
- Provenance: `provenance/CURVED_SPIN_BUNDLE.md` and
  `provenance/EINSTEIN_SPINOR_44.md`.
- Public verification: anonymous recursive clones of both the content commit
  and release commit passed every PowerShell Phase 0 through Phase 5 gate,
  the focused Learn gate, and the Phase 5 Bash gate. They reproduced all
  canonical hashes against solver commit
  `d1836e6a279d63a90fe2839a0020123245487e76`, had zero tracked drift, and left
  only nine gate-created backup manifests untracked.
- Result: `main` and `phase5-curved-spin-gravity-green` are public; the tag
  points to the release commit verified from the final anonymous clone.

### Phase 6: Weitzenböck spin connection and dark-sector dynamics

- Publicly verified content commit:
  `369df0a80a9738b50880ea3f20846eebb6249a28`.
- Verified release commit and tag: pending public fresh-clone verification.
- Weitzenböck geometry fixture SHA-256:
  `804f00f31ffa4247fc1e30d8e89df3ea7ddbd7c8d9fe795317bd57155c93774c`.
- Independent Wolfram geometry report SHA-256:
  `4faa10f831727e8142c9137f50ebec416eb2286f6adb74148ad318fa1a05b517`.
- Generated Rust constants SHA-256:
  `98aefc8d785bef34dc801a75b03f07f67bde77422afd4867de2709ae05a4ab4a`.
- Numerical history SHA-256:
  `c88ed61cafa59ea0d7693da41527c7b4486ded7cc09ac680b4f20f893d42b62a`.
- Numerical summary SHA-256:
  `d03a90539887702ad6bdbe0ee3a5d783094b052609fc0e4d2b761a12b97fa6c8`.
- Mathematica notebook SHA-256:
  `5c80d2d9367610db9835f4c570966dba1751cad77ae30f42dc0987bc917505e2`.
- Provenance Markdown, LaTeX, and PDF SHA-256 values:
  `cdffe26dd1d3bc67a656769d7defb2eb991da6cc34231bfad4d55876e98ee7fc`,
  `735576ec52eb30477a6d1dc15ed5e0109ee47bafd389871075256554237046d0`,
  and `7d14521cf34debb25d277e4db75d3b47bce55ad24ddd30b2b56d65bc9dfa7cd6`.
- Verification: `scripts/verify_phase6_weitzenbock_spinor.ps1` or
  `scripts/verify_phase6_weitzenbock_spinor.sh`.
- Provenance: `provenance/WEITZENBOCK_SPINOR_44.md`.
- Scientific boundary: the mass and self-interaction terms are homogeneous
  dust-like and negative-pressure analogies. TEGR torsion rewrites gravity
  and is not an extra dark fluid. No observational identification is claimed.
- Public content verification: an anonymous recursive clone passed every
  PowerShell Phase 0 through Phase 6 gate, the focused Learn gate, and the
  Phase 6 Bash gate. It reproduced all canonical hashes against solver commit
  `d1836e6a279d63a90fe2839a0020123245487e76`, had zero tracked/staged drift,
  and both Git object databases passed `git fsck --full --strict`.

## Evidence

- `backups/pre-bootstrap/manifest.json`
- `audit/source-manifest.json`
- `audit/source-manifest.csv`
- `audit/SHA256SUMS`
- `audit/audit-ledger.md`
- `audit/wolfram-structure.json`
- `audit/structural-audit.json`
- `audit/reviews/pre-universe-gpt56-sol.md`
- `audit/reviews/pre-universe-with-claude.md`
- `audit/reviews/pre-universe.md`
- `audit/reviews/dirac-matrices.md`
- `audit/reviews/eternal-deflation-inflation.md`
- `audit/reviews/sundials-7-8-rust-port-win11.md`
- `audit/reviews/rust-solveit-win11-sundials-7-8-0.md`
- `provenance/LEARN_DISSERTATION.md`
- `provenance/CURVED_SPIN_BUNDLE.md`
- `provenance/EINSTEIN_SPINOR_44.md`
- `provenance/WEITZENBOCK_SPINOR_44.md`
- `logs/phase0-verify-tests.log` (local, ignored)
- `logs/phase0-verify-manifest.log` (local, ignored)
- `logs/phase0-verify-wolfram.log` (local, ignored)
- `logs/phase0-verify-structural.log` (local, ignored)
- `logs/phase0-verify-check.log` (local, ignored)
- `logs/phase0-cross-check-manifest.log` (local, ignored)
- `logs/phase0-test-source-manifest-after-format.log` (local, ignored)
- `logs/phase0-git-init-ignore-check.log` (local, ignored)

## Constraints carried forward

- Public mathematical and numerical outputs remain real-valued.
- Historical notebook output is not accepted as proof.
- The 16-dimensional real Clifford module restricts to two inequivalent
  8-dimensional half-spin modules of `Spin(4,4)`.
- Vendored SUNDIALS source will remain byte-identical and read-only.
- Every existing file is backed up and hash-verified before modification.

Next action: commit and push this public-verification record, verify that
release commit from an anonymous recursive clone, then create and push the
annotated `phase6-weitzenbock-spinor-green` tag.
