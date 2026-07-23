import CollarGapFloor

/-!
# Axiom audit for the #306 collar-gap floor skeleton

Mirrors the repo precedent
`Lean/ObserverPatchHolography/Proofs/ObservableNormalForms/ObservableNormalForms/AxiomAudit.lean`.
Every theorem below should report at most the three standard Lean/Mathlib
axioms (`propext`, `Classical.choice`, `Quot.sound`) — no `sorryAx`, no
custom axioms.
-/

#print axioms OPH.CollarGapFloor.exists_uniform_floor
#print axioms OPH.CollarGapFloor.AdmissibleCollarTower.exists_uniform_floor
#print axioms OPH.CollarGapFloor.sum_broken_ge_floor
#print axioms OPH.CollarGapFloor.CommutingColorSpectrum.gap_of_floor
#print axioms OPH.CollarGapFloor.degenerateRate_pos
#print axioms OPH.CollarGapFloor.no_uniform_floor_of_degenerate_rates
#print axioms OPH.CollarGapFloor.IncompleteColorSpectrum.gap_collapse_of_incomplete_repair
#print axioms OPH.CollarGapFloor.incompleteWitness_collapses
