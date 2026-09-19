# Audit: Pre-Universe_with_Claude-main

Review status: complete for all 67 required artifacts: 15 Markdown files,
43 Wolfram sources, 3 notebooks, and 6 binary Wolfram states. No source was
modified or executed. Stored outputs are historical evidence; `.mx` files are
hash-only.

## Markdown

| Path | Finding | Disposition |
|---|---|---|
| `README.md` | Index with historical run claims and unsupported physical interpretation. | Historical evidence |
| `PROVENANCE-00-READING-THE-ORIGINAL-NOTEBOOK.md` | Useful extraction pattern, but box flattening is lossy and graphics are omitted. | Reuse pattern |
| `PROVENANCE-01-BUILDING-AND-RUNNING-THE-REFACTORED-NOTEBOOK.md` | Useful deterministic build pattern; mixes revision counts and is not independent proof. | Reuse pattern |
| `PROVENANCE-02-FRAME-FIELD-AND-CANONICAL-SPIN-CONNECTION.md` | Relevant geometry; confuses a local frame with coordinates and leaves free functions unspecified. | Independently reconstruct |
| `PROVENANCE-03-SPINOR-COVARIANT-DERIVATIVE.md` | Relevant chiral blocks; block diagonality alone does not prove irreducibility or inequivalence. | Independently reconstruct |
| `PROVENANCE-04-BRIDGE-1-BOOSTED-FRAME-COMPARED.md` | Local gauge change with inconsistent novelty wording. | Independently reconstruct |
| `PROVENANCE-05-BRIDGE-2-NULL-FRAME-COMPARED.md` | Constant basis change, not a new connection; physical interpretation is unsupported. | Independently reconstruct |
| `PROVENANCE-06-BRIDGE-3-OCTONIONIC-TORSION-COMPARED.md` | Fixed-spinor map is not full triality; contortion is an explicit ansatz. | Independently reconstruct |
| `PROVENANCE-07-PHYSICS-REPRODUCTION-AND-MX-FIDELITY.md` | Cached-state agreement is not correctness; generation claims are unsupported. | Historical evidence |
| `PROVENANCE-08-REPOSITORY-PUSH-AND-VERIFICATION.md` | Useful workflow history, but remote and object scans are incomplete or obsolete. | Historical evidence |
| `PROVENANCE-09-EVALUATING-THE-NOTEBOOK-AND-CHECKING-THE-OUTPUT.md` | Useful runner pattern; self-authored assertions and numeric witnesses are not proof. | Reuse pattern |
| `PROVENANCE-10-RENDER-CHECK.md` | Useful rendering pattern; selected cells and text needles do not cover the full document. | Reuse pattern |
| `PROVENANCE-11-REVIEW-AND-REFACTOR-OF-THE-OPUS-SOLUTION.md` | Valuable defect catalogue; deterministic bases and full triality remain unresolved. | Historical evidence |
| `PROVENANCE-12-FABLE-5.1-BRIDGE-COMPARED.md` | Standard teleparallel construction with convention, boundary, domain, and spinor-statistics caveats. | Independently reconstruct |
| `STUDENT-GUIDE-FABLE-5.1-BRIDGE.md` | Tutorial inherits the teleparallel and domain limitations above. | Independently reconstruct |

## Wolfram Sources

| Path | Finding | Disposition |
|---|---|---|
| `claude-fable/attribute_certs.wls` | Diagnostic instrumentation replays the system under test. | Reuse pattern |
| `claude-fable/cells_part1.wl` | Useful setup and chiral-block construction; the `tau` blocks are not full Clifford generators. | Reuse pattern |
| `claude-fable/cells_part2.wl` | Relevant 16D action and product table; lacks rank-256, half-spin, and full-triality proofs. | Reuse pattern |
| `claude-fable/cells_part3.wl` | Historical PDE/Maple/plane material with unsupported physical claims. | Historical evidence |
| `claude-fable/cells_part4.wl` | Useful connection patterns; boost/null are gauge or basis changes and torsion is an ansatz. | Reuse pattern |
| `claude-fable/cells_part5.wl` | Useful standard Weitzenböck pattern, not a novel geometry. | Reuse pattern |
| `claude-fable/check_deltas.wls` | Partial historical replay without decisive failure status. | Historical evidence |
| `claude-fable/cmp_mx.wls` | Compares opaque, version-dependent state. | Historical evidence |
| `claude-fable/ConvertMapleToMathematicaV2.wl` | Disclaimed incomplete parser that may silently skip input and then evaluates it. | Historical evidence |
| `claude-fable/EtoExp.wl` | Disclaimed helper with self-tests coupled to implementation. | Historical evidence |
| `claude-fable/extract/extract_original.wls` | Useful non-evaluating extractor with lossy box conversion. | Reuse pattern |
| `claude-fable/mx_fidelity2.wls` | Historical binary-state comparison susceptible to stale symbols. | Historical evidence |
| `claude-fable/nb_section_map.wls` | Useful structural index, not semantic validation. | Reuse pattern |
| `claude-fable/probe2.wls` | Fixed-spinor diagnostic, not full triality. | Historical evidence |
| `claude-fable/probe3.wls` | Basis diagnostic, not a triality action. | Historical evidence |
| `claude-fable/probe4.wls` | Peripheral complex 3+1 probe. | Unrelated |
| `claude-fable/probe_sig.wls` | Experimental signature probe with acknowledged broken method. | Historical evidence |
| `claude-fable/probe_sig2.wls` | Conditional frame-signature check with unstated domains. | Reuse pattern |
| `claude-fable/prov02_frame_and_connection.wls` | Replays the canonical frame calculation rather than independently deriving it. | Independently reconstruct |
| `claude-fable/prov03_covariant_derivative.wls` | Omits half-spin irreducibility and inequivalence. | Independently reconstruct |
| `claude-fable/prov04_bridge1.wls` | Gauge covariance test, not a new connection. | Historical evidence |
| `claude-fable/prov05_bridge2.wls` | Constant basis check, not a new connection. | Historical evidence |
| `claude-fable/prov06_bridge3.wls` | Torsion ansatz and fixed-spinor map require independent triality reconstruction. | Independently reconstruct |
| `claude-fable/prov07_mx_fidelity.wls` | Binary-state comparison cannot be source proof. | Historical evidence |
| `claude-fable/prov07_physics.wls` | Historical model replay with unsupported interpretation. | Historical evidence |
| `claude-fable/render-check/check_out.wls` | Secondary output-string scan only. | Reuse pattern |
| `claude-fable/render-check/fe_full.wls` | Useful front-end runner needing fail-fast hashes and assertions. | Reuse pattern |
| `claude-fable/render-check/findpage.wls` | One-phrase PDF diagnostic. | Unrelated |
| `claude-fable/render-check/pdf.wls` | Partial PDF text check without all-page visual validation. | Reuse pattern |
| `claude-fable/render-check/probe.wls` | Syntax/renderability probe, not semantic validation. | Reuse pattern |
| `claude-fable/render-check/probe_prefix.wls` | Small-prefix debugging artifact. | Unrelated |
| `claude-fable/render-check/shots.wls` | Selected-cell rasterization only. | Reuse pattern |
| `claude-fable/report_results.wls` | Same-system result summary without fail-fast behavior. | Historical evidence |
| `claude-fable/run_all.wls` | Generated monolith with missing faithfulness/triality proofs and numeric probes. | Generated |
| `claude-fable/run_all_12.wls` | Stale generated snapshot with unstable basis ordering. | Generated |
| `claude-fable/run_from_clone.wls` | Useful runner shell requiring source hashes and nonzero failure exits. | Reuse pattern |
| `claude-fable/run_from_nb.wls` | Useful runner shell requiring fail-fast assertions. | Reuse pattern |
| `claude-fable/runner_header.wl` | Timing/message harness that retains state and does not abort. | Reuse pattern |
| `claude-fable/student_fable51.wls` | Model-specific teleparallel replay with domain assumptions. | Historical evidence |
| `claude-fable/verify_nb.wls` | Structural parser check that does not execute or verify results. | Reuse pattern |
| `ConvertMapleToMathematicaV2.wl` | Byte duplicate of the incomplete disclaimed parser. | Historical evidence |
| `Dirac-Lord-Nash_4+4.wl` | Legacy package with representation conflation and broken indexing/tests. | Independently reconstruct |
| `EtoExp.wl` | Byte duplicate of the disclaimed helper. | Historical evidence |

## Notebooks And Binary State

| Path | Finding | Disposition |
|---|---|---|
| `2026-02-20-Pre-U-mmM4p.nb` | Large dated scratch derivative with stored messages, graphics, and outputs. | Historical evidence |
| `claude-fable/claude-fable_Einstein-Rosen-2-Planes.nb` | Generated 238-cell notebook exactly represented by the five cell manifests; contains no stored outputs. | Generated |
| `Pre-gravityPre-Big_Bang_M6=3-Generations_of_Einstein-Rosen-2-Planes.nb` | Original scratch notebook with cached state, helper-path dependencies, and unsupported physical claims. | Historical evidence |
| `2026-02-20-Pre-U-mmM4p-eLa.mx` | Opaque companion state; contents not inferred. | Hash-only |
| `2026-02-20-Pre-U-mmM4p-eLazt.mx` | Opaque companion state; contents not inferred. | Hash-only |
| `claude-fable/claude-fable_Einstein-Rosen-2-Planes-eLa.mx` | Opaque companion state; contents not inferred. | Hash-only |
| `claude-fable/claude-fable_Einstein-Rosen-2-Planes-eLazt.mx` | Opaque companion state; contents not inferred. | Hash-only |
| `Pre-gravityPre-Big_Bang_M6=3-Generations_of_Einstein-Rosen-2-Planes-eLa.mx` | Opaque companion state; contents not inferred. | Hash-only |
| `Pre-gravityPre-Big_Bang_M6=3-Generations_of_Einstein-Rosen-2-Planes-eLazt.mx` | Opaque companion state; contents not inferred. | Hash-only |

## Corrections And Dependencies

- `Cl(4,4)` has a real 16-dimensional irreducible module, while its
  restriction to `Spin(4,4)` is `S+` direct-sum `S-`, with two inequivalent
  real 8-dimensional half-spin modules.
- The 8-dimensional `tau` arrays are chiral Clifford blocks, not standalone
  representations of the full Clifford algebra.
- A fixed-spinor isometry does not establish triality. Full triality requires
  the three representations, an invariant trilinear form, and the outer `S3`
  action.
- Boosted and null presentations are gauge or basis descriptions of the
  Levi-Civita connection. The octonionic contortion is an ansatz.
- The Weitzenböck construction is standard and inherits domain/sign/boundary
  assumptions from the chosen frame.
- The safest reusable patterns are the five cell manifests, the held notebook
  extractor, section mapper, hardened runner concepts, and render probes.
- The two helper pairs are byte duplicates. The three notebooks share lineage,
  not independent confirmation.

Reviewed: 67 of 67 required artifacts.