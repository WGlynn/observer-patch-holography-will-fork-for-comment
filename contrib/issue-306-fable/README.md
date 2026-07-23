# OPH #306 — machine-checked confirm-and-extend (countermodels + Lean skeleton)

Confirm-and-extend contribution to issue #306 ("Proof packet: Uniform Collar Projection Gap"),
pinned to the proof packet on `origin/main` at `ae6eccd1`. Two independently-machine-checked pieces:

- **`countermodels/`** — finite countermodels for the #306 acceptance item ("a finite countermodel
  demonstrates failure when each mixing or locality hypothesis is removed"), as data + `verify.py`
  (`python verify.py` -> 5/5 PASS, exit 0). CM1 replaces the repo's vacuous `0==0` no-mixing test
  with an exact char-poly identity; CM2 extends the single-Fourier-mode gray-cycle test to a
  full-spectrum minimal-eigenvalue check + exact operator identity + nonlocality witness + a
  locality-restored positive control; CM3/CM3b exercise the vendored certificate validator
  fail-closed and show the arithmetic layer alone cannot certify the gap — locality lives in
  source-signature (`rooted_neighborhood`) faithfulness. Provenance of vendored blobs in
  `countermodels/vendored/PROVENANCE.md` (byte-identical to `ae6eccd1`).

- **`lean/`** — a Lean 4 formalization of the finite eigenvalue-bookkeeping SKELETON:
  `lake build CollarGapFloor` compiles clean (same toolchain/mathlib as the repo's Lean project),
  axiom audit shows only `[propext, Classical.choice, Quot.sound]` (no `sorryAx`, no custom axioms).
  Scope is honest and stated in the source: the diagonalized/commuting spectral picture is ASSUMED
  via the `structure`, not derived; the file proves the floor-given-structure plus the two
  gap-collapse countermodels (degenerate rates, incomplete repair). It does NOT prove the analytic
  gap. Build details in `lean/BUILD_RECEIPT.md`.

## Honest scope
Nothing here closes #306, #294, or #295. The physical source/continuum/transfer/OS/noncollapse
obligations remain gated. This bundle machine-checks the finite combinatorial core and the required
countermodels, and locates the load-bearing open hypothesis (source-signature faithfulness).

Generated with Fable 5 reasoning agents, adversarially verified (each machine-check independently
re-run), fabrication-floor gated: only Lean-green and reproducible-computation artifacts are here;
one analytic-bound draft was held back as not-yet-proven.
