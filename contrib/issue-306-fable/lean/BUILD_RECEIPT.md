# Build receipt — #306 collar-gap floor skeleton (staging)

Date: 2026-07-23 (build ran 2026-07-22 local time)
Machine: Windows 10, Ryzen 5 1600, toolchain `leanprover/lean4:v4.29.1`
(same toolchain as `observer-patch-holography/Lean/lean-toolchain`),
mathlib rev `5e932f97dd25535344f80f9dd8da3aab83df0fe6` (same as
`observer-patch-holography/Lean/lake-manifest.json`), package cache reused via
directory junction `.lake/packages ->
C:/Users/Will/observer-patch-holography/Lean/.lake/packages`.

## Command 1 — library build

```
cd C:/Users/Will/oph-fable-staging/lean && lake build CollarGapFloor
```

Result (verbatim tail):

```
[8248/8249] Built CollarGapFloor (190s)
Build completed successfully (8249 jobs).
```

Exit code 0. (8248 of the 8249 jobs are the reused, already-built mathlib
dependency graph; the one new job is `CollarGapFloor`.)

## Command 2 — axiom audit

```
cd C:/Users/Will/oph-fable-staging/lean && lake env lean AxiomAudit.lean
```

Result: all eight audited theorems report exactly
`[propext, Classical.choice, Quot.sound]` — no `sorryAx`, no custom axioms.
Verbatim output captured in `axiom_audit_output.txt`.

## Command 3 — token scan

`grep -n "sorry\|admit\|axiom \|native_decide" CollarGapFloor.lean` matches
only the English word "admits" in two doc comments (lines 51, 223). No proof
uses `sorry`, `admit`, `axiom`, or `native_decide`.

## Caveat (hidden-hypothesis disclosure)

Machine-checking establishes exactly the statements as written. The two
structures `AdmissibleCollarTower` and `CommutingColorSpectrum` are hypothesis
containers: the finite-type set and the simultaneously-diagonalized picture
are ASSUMED there, mirroring (not discharging) the corresponding derivations
in `extra/yang_mills_gap_clay_problem.tex` (`lem:floor` tex:511-518,
`prop:finite-gap` tex:544-556). This is stated in the file header and README;
no theorem in this packet claims the operator-level #306 gap.
