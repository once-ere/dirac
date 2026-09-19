# Audit: rustSolveIt_Win11_SUNDIALS_7_8_0-main

Review status: complete for all 91 required Markdown artifacts. The 24 files
under `sundials_rs/` are byte-identical to the separately reviewed solver root;
their findings are inherited only after path, size, and SHA-256 equality. The
other 67 files were read completely. No source was modified, built, or run.

## Coverage And Inheritance

| Set | Files | Bytes | Lines |
|---|---:|---:|---:|
| Required Markdown corpus | 91 | 2,424,828 | 42,298 |
| Hash-inherited `sundials_rs/` subset | 24 | 434,250 | 6,369 |
| Unique documents reviewed here | 67 | 1,990,578 | 35,929 |

All 91 files match the frozen manifest. Every inherited path has exactly one
matching path in `SUNDIALS_7_8_Rust_port_for_Windows11-main`. The only internal
duplicate is the expected pair of solver exclusion documents.

## Unique Artifact Findings

| Path | Finding | Disposition |
|---|---|---|
| `ARCHITECTURE.md` | Strong application-owned state, CVODE lifecycle, JSONL, and dataset boundaries. Statements that added solver families are unused are stale. | Reuse pattern |
| `box_of_shapes_m32.md` | Collision stress record showing that reporting cadence must not alter dynamics. The model and outputs are unrelated historical evidence. | Historical evidence |
| `CLAUDE.md` | Strong read-only vendor, borrow, error-flag, formatting, and command-logging rules; dated success records remain historical. | Reuse pattern |
| `CLEANROOM_PROVENANCE.md` | Useful independent-derivation, structural-test, and history-hygiene pattern. Historical clean-room claims need repository-history verification. | Reuse pattern |
| `collision_detection.md` | Reusable root-event, analytic event-time, and invariant-test patterns. Its rigid-collision equations are unrelated. | Reuse pattern |
| `dataset_tools/README.md` | Stable SQLite/JSONL protocol, WAL, and no-timestamp patterns. The schema is rigid-body-specific and adds external packages plus C-built SQLite. | Reuse pattern |
| `DATASETS_COMPLETE.md` | Useful data-first workflow and exact batch commands. Completion statements and superseded rerun wording are historical. | Reuse pattern |
| `dynamic_notebooks/MANIFEST.md` | Exact source-to-session inventory and headless invocation. Stored PASS rows are not current evidence. | Historical evidence |
| `dynamic_notebooks/README.md` | Stateful session launcher pattern. The interface is GUI-oriented and mechanics-specific. | Reuse pattern |
| `EXPORT_PROVENANCE.md` | Useful tracked-only export, source-map, hash, and exclusion pattern. It describes an older solver tree. | Historical evidence |
| `grammar.md` | Precise machine, batch, notebook, dataset, and error contracts. The language is mechanics-specific and its comparison-operator statement is stale. | Reuse pattern |
| `gui/README.md` | Preserves engine/renderer separation. Repeated step requests cold-restart the solver and the GUI is unrelated to canonical studies. | Unrelated |
| `index_data/DIVERGENCES.md` | Useful code-authoritative probes and bidirectional documentation gates. This is a dated resolution record. | Reuse pattern |
| `jupyter/README.md` | Exact kernel setup, JSONL protocol, and protocol checks. It lacks source/environment hashes and supports only one outstanding request. | Reuse pattern |
| `MACOS_PORT_COMPLETE.md` | Complete historical command ledger for another platform. | Historical evidence |
| `NOTEBOOKS.md` | Correctly distinguishes REPL, script, notebook, and machine modes. Captures mix canonical and superseded historical runs. | Historical evidence |
| `notebooks/README.md` | Exact regenerate, execute, and audit pipeline with UTF-8 handling. Parallel runs and skipped interactive cells weaken canonical reproducibility. | Reuse pattern |
| `physical_object_simulator.md` | Useful direct-CVODE application and run-report pattern. Its old architecture, counts, and state packing are not reusable as-is. | Reuse pattern |
| `PLAN.md` | Useful solver-only integration boundary and application-owned state plan. It predates most current functionality. | Historical evidence |
| `PLANET_MERCURY_PROVENANCE.md` | Closest long-running CVODE precedent: roots, stages, restart files, manifests, and notebook audit. Equations and values are model-specific. | Reuse pattern |
| `planet_Mercury/INSTRUCTIONS_FOR_TEACHERS_AND_STUDENTS.md` | Complete build, headless notebook, checker, database, and display commands. The long model run remains historical. | Reuse pattern |
| `planet_Mercury/plan/00_PLAN_OVERVIEW.md` | Useful small phase gates and artifact inventory. It is a pre-build plan with stale platform details. | Historical evidence |
| `planet_Mercury/plan/01_PHYSICS_AND_MATH.md` | Useful dimensional and timescale audit method. The unrelated model claims require independent verification. | Independently verify |
| `planet_Mercury/plan/02_ARCHITECTURE_AND_ENGINE.md` | Useful vector tolerances, roots, reinitialization, statistics, and teardown sequence. Plan-era text and platform metadata are stale. | Reuse pattern |
| `planet_Mercury/plan/03_NOTEBOOK_INSTRUCTIONS.md` | Useful self-contained lesson and audit design. It is a superseded platform-specific draft. | Reuse pattern |
| `planet_Mercury/plan/04_DATABASE_SCHEMA.md` | Useful units, run IDs, events, targets, and provenance joins. It omits source/executable hashes and is model-specific. | Reuse pattern |
| `planet_Mercury/plan/05_VERIFICATION_PLAN.md` | Strong analytic expectations, fail-loudly runs, and independent-review gates. Numerical tolerances require reconstruction. | Reuse pattern |
| `planet_Mercury/plan/06_BUILD_ORCHESTRATION.md` | Useful compute/data/notebook/provenance gates. Tool and platform counts are historical. | Reuse pattern |
| `planet_Mercury/plan/07_PROVENANCE_AND_DEVIATIONS.md` | Useful explicit errata, failed assumptions, and as-built corrections. Proposal and retrospective material are mixed. | Historical evidence |
| `planet_Mercury/SOURCE_SPECIFICATION.md` | Useful explicit source chain and equation errata. The secondary model consolidation is unrelated and unverified. | Independently verify |
| `PORT_7.8.0_PROVENANCE.md` | Useful exact solver API migration and ownership notes. Its usage status is dated. | Reuse pattern |
| `PORT_MACOS_PROVENANCE.md` | Useful separation of engine-deterministic and host-math paths. Evidence is platform-specific history. | Historical evidence |
| `PORT_WIN11_PROVENANCE.md` | Useful exact toolchain, gate, divergence, and merge record. Execution claims are historical. | Historical evidence |
| `PROJECT_STATUS.md` | Candid historical limitation and retired-claim list. Many capabilities are superseded. | Historical evidence |
| `README.md` | Complete operational map and entry commands. Broad completion claims require a fresh rerun. | Historical evidence |
| `REBOUND_PROVENANCE_dynamic_bouncing_ball_restitution.md` | Exact notebook recipe for unrelated collision physics. | Unrelated |
| `REBOUND_PROVENANCE_dynamic_routh_p1_geometric_progression.md` | Analytic sequence and notebook pairing for unrelated collision physics. | Unrelated |
| `REBOUND_PROVENANCE_dynamic_spinning_target.md` | Independent conservation anchors for unrelated collision physics. | Unrelated |
| `REBOUND_PROVENANCE_rust_bouncing_ball_restitution.md` | Self-checking binary/notebook pairing for unrelated collision physics. | Unrelated |
| `REBOUND_PROVENANCE_solveit_04_restitution_ladder.md` | Exact transcript and notebook commands for unrelated collision physics. | Unrelated |
| `REBOUND_REBOUNDX_MACOS_PROVENANCE.md` | Useful raw-bit comparison pattern, but historical, platform-specific, and GPL-covered. | Historical evidence |
| `REBOUND_REBOUNDX_WIN11_PROVENANCE.md` | Useful raw-state, archive-interchange, and gate pattern. Scope is limited to enumerated GPL harnesses. | Historical evidence |
| `rebound_rust/logs/win11_c_reference_gates_20260909.md` | Exact historical commands and artifact distinctions with concurrent-worktree caveats. | Historical evidence |
| `rebound_rust/README.md` | API and citation map for an unrelated GPL integrator stack; one tolerance statement exceeds its own evidence. | Unrelated |
| `rebound_rust/rebound_rust.md` | Useful file accounting, raw-bit gates, and defect case studies. GPL scope and stale lint status prevent direct reuse. | Historical evidence |
| `rebound_rust/reboundx_port_test.md` | Same-platform tests for an unrelated integrator and effects package. | Unrelated |
| `rebound_rust/shearing_sheet_port_test.md` | Useful divergence-localization method for an unrelated GPL collision system. | Unrelated |
| `reboundx_rust/README.md` | Safe index-based replacement pattern for an unrelated GPL package. | Unrelated |
| `reboundx_rust/reboundx_port_test.md` | Limited same-platform acceptance record for unrelated effects. | Unrelated |
| `recorder/docs/FRAME_FORMAT.md` | Useful solver-time, static-metadata, schema-version, and invariant pattern. The rigid-body schema is not reusable directly. | Reuse pattern |
| `recorder/README.md` | Useful manifest, parameter, workspace, and byte-check pattern. Repeated step calls restart the solver and are unsuitable for canonical trajectories. | Reuse pattern |
| `REFINE_PROVENANCE.md` | Useful adversarial review, refutation, mutation, and regression-test pattern. Historical results do not validate target mathematics. | Reuse pattern |
| `scene_info.md` | Browser event-routing and engine/view separation for an unrelated interface. | Unrelated |
| `SolveIt_Notebooks_for_rust/ENCYCLOPEDIA.md` | Useful canonical-source map and player commands. PASS status may be taken from stale logs. | Historical evidence |
| `SolveIt_Notebooks_for_rust/README.md` | Exact generation, execution, capture, and verification commands. Log ordering can select stale or foreign verdicts. | Reuse pattern |
| `SolveIt.md` | Useful batch/machine commands and analytic-check style. Its grammar cannot express the target systems. | Reuse pattern |
| `SPECIAL_FUNCTIONS_PROVENANCE.md` | Useful structural identities, convergence, and mutation testing. Its non-real-order support statements conflict. | Independently verify |
| `special_functions.md` | Exact-domain errors and independent identities for functions not needed by the exact algebra core; provenance remains a concern. | Unrelated |
| `SQLITE_DATASETS_PROVENANCE.md` | Useful deterministic schema, no-timestamp, alignment, and command pattern. Results are historical and the schema is model-specific. | Reuse pattern |
| `StageNbks/README.md` | Exact REPL/script/notebook distinction. These sessions are not a deterministic Jupyter lifecycle. | Reuse pattern |
| `StageNbks/STAGENBKS_PROVENANCE.md` | Useful source-to-documentation trace with untested browser behavior called out. | Historical evidence |
| `THIRD_PARTY.md` | Useful dependency inventory, but it incorrectly summarizes the mixed-license solver subtree and leaves one vendored provenance issue open. | Independently verify |
| `TUNNELING_RESULTS.md` | Useful negative-result and convergence-reporting pattern for unrelated physics. | Unrelated |
| `vendor/spec_math/README.md` | Brief roadmap for unrelated functions without adequate license/provenance evidence. | Unrelated |
| `VERIFICATION_MACOS.md` | Useful pinned-divergence method for another platform. | Historical evidence |
| `VERIFICATION_WIN11.md` | Exact Windows commands and bounded divergence inventory. Finalization text conflicts with its own completed matrix. | Historical evidence |
| `WINDOWS_PORT_COMPLETE.md` | Consolidated Windows command catalogue. All success counts remain historical pending fresh-clone rerun. | Historical evidence |

## Reusable Boundaries

### CVODE Applications

Use the application pattern, not the rigid-body model: application-owned state,
vector absolute tolerances, root events, one continuous integration segment,
solver statistics, and ordered teardown. Keep `sundials_rs/` byte-identical and
place both target studies in new application crates. Nothing in this root
establishes the target equations, invariants, or initial data.

### Deterministic Jupyter

The best complete command chains are in `jupyter/README.md`,
`notebooks/README.md`, `SolveIt_Notebooks_for_rust/README.md`, and the Mercury
student/provenance documents. Reuse sequential generation, execution, and
post-run checking. Do not reuse parallel canonical runs, stale-log verdict
selection, in-process unbounded Python execution, or rigid-body grammar.

### Data And Provenance

Reuse stable run IDs, solver-reported times, explicit schema versions, fixed
ordering, UTF-8/LF output, no wall-clock fields, hash-pinned inputs, and
write-on-success runners. Define target-specific state, invariant, event, and
solver-statistic tables. Do not generate canonical trajectories through
repeated cold-start step requests.

## Licensing Boundary

- The solver subtree combines BSD-3-Clause, MIT, and LGPL-2.1-or-later code;
  binaries using its deterministic math modules must meet the LGPL terms.
- REBOUND and REBOUNDx material is GPL-3.0-or-later and remains separate.
- The dataset sidecar adds external packages and compiled SQLite.
- `vendor/spec_math` has unresolved source-license provenance and is not reused.
- Non-redistributable and copyleft mathematical sources are evidence only;
  required target mathematics is reconstructed independently.

## Corrections Carried Forward

- The current Mercury manifest hard-codes a different platform label and omits
  source, executable, and configuration hashes.
- Existing machine and notebook protocols have no request IDs, discard backend
  diagnostics, and do not provide per-cell isolation or timeout control.
- The canonical wrapper will be target-specific, sequential, hash-pinned, and
  write results only after all assertions pass.

Reviewed: 91 of 91 required artifacts.