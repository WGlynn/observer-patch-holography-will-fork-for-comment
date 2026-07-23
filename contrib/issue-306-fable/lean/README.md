# #306 Lean sub-lemma staging: collar-gap floor skeleton

Angle 3 (Lean-formalized bounded sub-lemma) staging artifact for OPH issue
#306 "Proof packet: Uniform Collar Projection Gap".
Author identity for integration: WGlynn <willglynn123@gmail.com>.

## What this is

`CollarGapFloor.lean` machine-checks the finite combinatorial/spectral
SKELETON of the two load-bearing finite lemmas behind the #306 gap
certificate, plus two hypothesis-removal countermodels in the same skeleton:

| Lean name | Status | Source grounding |
|---|---|---|
| `OPH.CollarGapFloor.exists_uniform_floor` | newly-proved-here-with-machine-check | final step of Lemma `lem:floor`, `extra/yang_mills_gap_clay_problem.tex:496-521` (min over the finite active type list is a positive uniform floor) |
| `OPH.CollarGapFloor.AdmissibleCollarTower.exists_uniform_floor` | newly-proved-here-with-machine-check | uniformity shape of #306 (one modulus over all stages), conditional on the finite-type hypothesis |
| `OPH.CollarGapFloor.sum_broken_ge_floor` | newly-proved-here-with-machine-check | eigenvalue-level union-bound step of Proposition `prop:finite-gap`, tex:563-572 |
| `OPH.CollarGapFloor.CommutingColorSpectrum.gap_of_floor` | newly-proved-here-with-machine-check | eigenvalue form of eq. (5)-(6), tex:525-574, ASSUMING the diagonalized picture |
| `OPH.CollarGapFloor.no_uniform_floor_of_degenerate_rates` | newly-proved-here-with-machine-check | countermodel: finite-type/refinement-stability removed => per-stage gap positive but no uniform floor (the #306 claim boundary in miniature; cf. tex:586-588) |
| `OPH.CollarGapFloor.IncompleteColorSpectrum.gap_collapse_of_incomplete_repair` + `incompleteWitness_collapses` | newly-proved-here-with-machine-check | countermodel: repair completeness (eq. (7), tex:551-556) removed => eigenvalue 0 on a nonconstant label |

## What this is NOT (honest boundary)

- NOT an operator-level proof of `L_r^Rep >= c_* (I - P_{0,r})`. The
  simultaneous diagonalization of the commuting color expectations is ASSUMED
  via the `CommutingColorSpectrum` structure, exactly where the source derives
  it (tex:544-556). Formalizing that derivation (finite-dimensional commuting
  self-adjoint projections are simultaneously diagonalizable, and the operator
  inequality transfer) is the next bounded step; see PLAN below.
- NOT a derivation of the finite active-type set from "finite local
  combinatorial type + branch homogeneity + refinement stability"
  (tex:511-518). That reduction is the genuinely physical part of `lem:floor`
  and is taken as a hypothesis (`AdmissibleCollarTower.typeOf`).
- NOT a formalization of the closing proof packet's `delta_* = c_*(1-eta_*)`
  bound. That formula (quoted in the #306 closing comment) was not found in
  the local checkout (searched `*.tex`, `*.md` on the current branch and
  `main` at r1551); no claim about it is made here.
- No claim about the physical compact-gauge source, OS regularity,
  transfer/vacuum, or noncollapse obligations (#294/#295 remain gated).

## Lane discipline

velvetmonkey owns the Lean collar chain (#544: `CollarLayer.lean`,
`CollarStates.lean`, `CollarStatesT1.lean`, `CollarModularT2.lean`, commit
`d007c5e6`, on `main`). That chain targets the collar-CLAUSE independence
(T0/T2), not the #306 gap floor; this file is a sibling brick, written in the
same `OPH` namespace and claim-discipline style, intended for transplant into
`Lean/ObserverPatchHolography/Source/ObserverPatchHolography/CollarGapFloor.lean`
next to their files (plus a `PROOF_INDEX.md` addendum in their format).
No file of theirs is duplicated or rivaled. Note: the current repo working
tree is on branch `fix/oph-542-tex-warnings`, which predates the #544
transplant; the collar chain lives on `main`.

## Build (machine check)

Standalone Lake project pinned to the repo toolchain (`leanprover/lean4:v4.29.1`)
and the repo's mathlib rev (`5e932f97dd25535344f80f9dd8da3aab83df0fe6`), reusing
the repo's already-built package cache via a directory junction:

```
.lake/packages -> C:/Users/Will/observer-patch-holography/Lean/.lake/packages   (junction)
lake build CollarGapFloor
```

Zero `sorry` / `admit` / `axiom` in `CollarGapFloor.lean` (grep-verifiable).
The build result is recorded by the orchestrator report; if the transcript
does not show a completed `lake build` success, treat the file as
draft-pending-build, not lean-green.

## PLAN: next bounded Lean steps toward the #306 target

1. **Simultaneous diagonalization brick**: for a commuting finite family of
   orthogonal projections on a finite-dimensional inner product space,
   `Matrix.IsHermitian.spectral_theorem` + pairwise commutation gives a joint
   eigenbasis; instantiate `CommutingColorSpectrum` from it, discharging the
   S2 hypothesis container. Mathlib has the one-operator spectral theorem;
   the commuting-family version needs assembly (moderate effort).
2. **Operator inequality transfer**: `I - prod E_C <= sum (I - E_C)` for
   commuting orthogonal projections, as a `ContinuousLinearMap.IsPositive`
   statement, then `L_tilde <= L^Rep` and the gap bound eq. (5). This crosses
   the "no C*-analysis" rail of velvetmonkey's `CollarLayer.lean`; per their
   T0 precedent the analytic content belongs in a separate state-side file.
3. **Interval-certified floor**: once the packet's atomic collar types and
   per-type rates are source-defined as data (issue acceptance bullet 1),
   replace the abstract `rate_pos` hypothesis with computed rational interval
   bounds and get `c_*` as an explicit outward-rounded rational, matching the
   packet's "interval certification allowed" clause.
