# Audit: SUNDIALS_7_8_Rust_port_for_Windows11-main

Review status: complete for all 24 required Markdown artifacts. Every document
was read completely and checked against the frozen manifest. No source was
modified, built, or executed. Current source properties were checked
statically; historical build and numerical claims remain pending clean rerun.

## Artifact Findings

| Path | Finding | Disposition |
|---|---|---|
| `ARCHITECTURE.md` | Defines the handle, callback, aliasing, copy-back, formatting, and return-code contracts needed by the CVODE applications. Thirteen accepted deviations include unexercised and invalid-input paths. | Reuse pattern |
| `c-results/EXCLUSIONS.md` | Gives the exact 20 serial KLU/SuperLU exclusions and broader backend scope. It corrects earlier false absence claims, but installed oneMKL, Intel MPI, and Fortran support were never enabled in the recorded build. | Historical evidence |
| `c-results/README.md` | Records the native C baseline commands and checksums. Only 114 of 180 C sources built, four LAPACK examples used substituted solvers, and one exit-zero run printed a solver error. | Historical evidence |
| `c-results/RESULTS.md` | Useful per-variant C outcome inventory. It is a generated historical table and many backend rows have no executable. | Historical evidence |
| `CLAUDE.md` | Strong fidelity, logging, callback, arithmetic-order, and cumulative-gate rules. Policy statements are not verification and some status text predates later evidence. | Reuse pattern |
| `current_status.md` | Best high-level platform and floating-point limitation summary. Its build and parity statements are historical, and the library input bytes are not linked to the recorded Rust build. | Independently verify |
| `differences/ANALYSIS.md` | Useful three-way Windows C, Rust, and shipped-reference comparison with error-text scanning. The native C and Rust builds deliberately use different math implementations. | Historical evidence |
| `differences/BY-EXAMPLE.md` | Provides direct per-variant comparison lookup, including CVODE and CVODES. Missing-backend rows require separate interpretation. | Historical evidence |
| `differences/README.md` | Documents symmetric normalization and comparison method. It calls 238 variants comparable while its own table gives 179. | Independently verify |
| `differences/SUMMARY.md` | Compact directory-level counts. Its denominator includes missing programs, so the 153/238 headline is not a direct runnable-pair parity fraction. | Independently verify |
| `evidence/linux-x86_64-glibc239/README.md` | Indexes inherited Linux evidence that adjudicates 26 reference divergences against pristine C. It is not a Windows or target-application run. | Historical evidence |
| `evidence/windows-x86_64-ucrt/README.md` | Indexes Windows gate and math investigation logs. Its statement that no native Windows C build existed is superseded elsewhere. | Independently verify |
| `examples/arkode/CXX_xbraid/README.md` | Documents external MPI/XBraid examples outside the serial CVODE and dependency-free target. | Unrelated |
| `port_SUNDIALS-7-8_to_pure_rust.md` | Detailed original scope, API, phase, and verification specification. It is aspirational and its clean-room wording does not describe the inherited crate history. | Reuse pattern |
| `POW_FMA_EXACTNESS.md` | Useful deterministic-power differential method and explicit platform bounds. The evidence is empirical and scoped to one math implementation, FMA behavior, and floating-point environment. | Reuse pattern |
| `PROGRESS.md` | Valuable defect and translation journal. Completion language coexists with entries still marked as building or unexercised. | Independently verify |
| `README.md` | Concise project map, platform contract, and mixed-license warning. The claim of zero port defects is broader than the exercised example and error-path coverage. | Historical evidence |
| `rust-results/EXCLUSIONS.md` | Exact duplicate of the C-side exclusions document; useful placement but not independent evidence. It also says vector modules are absent although source files now exist for both named implementations. | Historical evidence |
| `rust-results/README.md` | Records Rust build flags, lockfile, binary hashes, and output hashes. Input hashes cover examples but omit the library modules that implement the solver. | Historical evidence |
| `rust-results/RESULTS.md` | Useful per-variant Rust outcome inventory with 179 recorded output hashes. Excluded sparse rows can still say ported, and no-binary rows do not establish parity. | Historical evidence |
| `STATUS.md` | Preserves inherited platform history and unexercised-path notes. It is intentionally stale for the Windows repository. | Historical evidence |
| `sundials.md` | Useful public API and ownership guide with a complete Robertson CVODE call sequence. Some platform paths, adjoint notes, and math-library statements are stale and signatures require source confirmation. | Reuse pattern |
| `VERIFICATION.md` | Most detailed cross-platform variant and root-cause record. It retains obsolete no-Windows-C text and labels divergences as Windows-only while later sections trace the same set on Linux. | Independently verify |
| `VERIFY.md` | Best reusable checksum, build, and output-audit procedure. It says both 66 and 62 of 180 C files failed and does not hash the Rust library modules as build inputs. | Reuse pattern |

## Current-Byte Checks

- The manifest contains exactly 24 required documents in this root, and every
  one is byte-identical to a document under `sundials_rs/` in the larger
  `rustSolveIt_Win11_SUNDIALS_7_8_0-main` root.
- The only internal duplicate pair is `c-results/EXCLUSIONS.md` and
  `rust-results/EXCLUSIONS.md`.
- A read-only scan covered 268 Rust files. The seven occurrences of the word
  `unsafe` are documentation comments; no active unsafe block, C ABI block, or
  `libc::` use was found.
- Cargo manifests contain only six workspace path dependencies on
  `sundials_core`; the lockfile records seven workspace packages and no
  external package.
- Current source contains `nvector_openmp.rs` and `nvector_manyvector.rs`, so
  claims that those modules do not exist are stale. The ten missing Rust
  example counterparts remain a real coverage gap.

## Evidence Boundary

- Static inspection establishes the current no-unsafe, no-FFI, and
  no-external-package properties.
- The recorded warning-free build is historical because its source checksums
  omit solver library modules.
- CVODE evidence covers 24 declared variants: 18 reference-identical, three
  divergent, and three excluded. It does not cover every public API state,
  error path, preconditioner path, or reentrant callback behavior.
- Across the full 199-variant scoped set, 153 outputs are identical only after
  documented carriage-return and timing normalization; 15 differ only in
  whitespace, 11 differ in content, and 20 are excluded.
- The application must vendor or reference a separately hash-pinned solver
  tree without modifying these source bytes. New behavior belongs in the
  application crate.

Reviewed: 24 of 24 required artifacts.