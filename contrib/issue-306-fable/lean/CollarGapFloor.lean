import Mathlib

/-!
# #306 collar-gap skeleton: uniform rate floor, commuting-color eigenvalue gap,
# and the no-uniform-floor countermodel

Staging artifact for OPH issue #306 ("Proof packet: Uniform Collar Projection
Gap").  Written to EXTEND the #544 collar chain lane (velvetmonkey's
`CollarLayer.lean` / `CollarStates*.lean` / `CollarModularT2.lean`,
commit `d007c5e6`), in the same `OPH` namespace and the same claim-discipline
style.  It is a standalone-buildable file intended for transplant into
`Lean/ObserverPatchHolography/Source/ObserverPatchHolography/`.

## Source grounding (repo file:line, local checkout)

* `extra/yang_mills_gap_clay_problem.tex:496-521` — Lemma `lem:floor`
  (Uniform active-collar rate floor): positive per-type rate + finite active
  collar-type set across the cofinal refinement family + refinement stability
  give `c_C >= c_* > 0` uniformly in the regulator `r`.
* `extra/yang_mills_gap_clay_problem.tex:525-574` — Proposition
  `prop:finite-gap` (Special commuting-color finite-stage repair gap): with a
  bounded-color decomposition and commuting color expectations, on the joint
  eigenbasis every nonconstant joint eigenvector has at least one color
  eigenvalue zero, so the Dirichlet eigenvalue is `>= c_*`.
* Issue #306 claim boundary: finite-range Gibbs mixing and collar-CMI decay do
  NOT by themselves give a uniform gap; positivity at each finite stage does
  not give a positive infimum across stages.

## What is and is not proved here (claim discipline)

This file proves the FINITE COMBINATORIAL/SPECTRAL SKELETON of the two source
lemmas, at the level of eigenvalue bookkeeping, together with two
hypothesis-removal countermodels in the same skeleton.  Concretely:

* PROVED (machine-checked below):
  - `exists_uniform_floor` : a positive rate function on a finite nonempty
    type set has a positive uniform lower bound (the minimum).  This is the
    final step of the `lem:floor` proof ("Taking the minimum of `c_C` over the
    finite active type list gives `c_* > 0`", tex:519-520).
  - `AdmissibleCollarTower.exists_uniform_floor` : the same floor is uniform
    across an arbitrary stage-indexed tower whose collar types stay inside one
    fixed finite type set — the exact uniformity SHAPE demanded by #306
    ("one modulus uniform across locations, boundary conditions, system size,
    and refinement"), given the finite-type hypothesis.
  - `CommutingColorSpectrum.gap_of_floor` : in the simultaneously-diagonalized
    picture of `prop:finite-gap`, every nonconstant joint eigenlabel with at
    least one broken color has Dirichlet eigenvalue `>= c_*` (the union-bound
    step `I - prod E_C <= sum (I - E_C)` at eigenvalue level, tex:563-572).
  - `no_uniform_floor_of_degenerate_rates` : COUNTERMODEL 1 (finite-type
    hypothesis removed).  The rate family `c_n = 1/(n+1)` is positive at every
    stage yet admits no positive uniform floor: per-stage gap positivity does
    not give a uniform gap.  This is the #306 claim boundary in miniature.
  - `gap_collapse_of_incomplete_repair` : COUNTERMODEL 2 (repair-completeness
    hypothesis removed).  A nonconstant eigenlabel fixed by every color has
    Dirichlet eigenvalue 0, so no positive gap bound can hold.

* NOT proved here (open, tracked by #306/#294/#295):
  - Nothing here constructs the collar operator, the heat-bath projections
    `E_C`, or the simultaneous diagonalization; the `CommutingColorSpectrum`
    structure ASSUMES the diagonalized picture that `prop:finite-gap` derives
    from commuting color expectations.  The operator-level statement
    `L_r^Rep >= c_* (I - P_{0,r})` is not formalized.
  - Nothing here derives the finite active-type set from "finite local
    combinatorial type + branch homogeneity + refinement stability"; that
    derivation (tex:511-518) is assumed as the `typeOf` map of the tower.
  - No claim about the physical compact-gauge source, OS regularity,
    transfer/vacuum, or noncollapse obligations (gated under #294/#295).

In short: this file machine-checks the finite bookkeeping that the #306 proof
packet's gap certificate rests on, and machine-checks that BOTH nontrivial
hypotheses (finite type set, repair completeness) are individually
load-bearing.  It does not close, and does not claim to close, any operator-
analytic or physical obligation.
-/

namespace OPH
namespace CollarGapFloor

/-! ## S1 : uniform rate floor from a finite active collar-type set

Skeleton of `lem:floor` (tex:496-521).  The analytic content of the source
lemma is the REDUCTION to a finite type list; the floor itself is the minimum
over that list.  Here we machine-check the floor step and its tower-uniform
transfer, taking the finite type set as hypothesis. -/

/-- The final step of `lem:floor`: a strictly positive rate function on a
finite nonempty collar-type set has a strictly positive uniform lower bound,
namely its minimum (tex:519-520). -/
theorem exists_uniform_floor {T : Type*} [Fintype T] [Nonempty T]
    (rate : T → ℝ) (hpos : ∀ t, 0 < rate t) :
    ∃ cStar : ℝ, 0 < cStar ∧ ∀ t, cStar ≤ rate t := by
  refine ⟨Finset.univ.inf' Finset.univ_nonempty rate, ?_, ?_⟩
  · exact (Finset.lt_inf'_iff _).mpr fun t _ => hpos t
  · exact fun t => Finset.inf'_le rate (Finset.mem_univ t)

/-- An admissible collar tower in the sense needed by #306's uniformity
clause: a stage-indexed family of collars (stages abstract over location,
boundary condition, system size, and refinement depth simultaneously) whose
active collar types land in one FIXED finite nonempty type set `T`, with a
per-type rate.  The finiteness of `T` across all stages is exactly the
refinement-stability output of `lem:floor` (tex:515-518), taken here as a
hypothesis, not derived. -/
structure AdmissibleCollarTower (T : Type*) [Fintype T] [Nonempty T] where
  /-- The collars present at stage `r` (an arbitrary index type per stage;
  no finiteness of the per-stage collar family is needed for the floor). -/
  Collar : ℕ → Type*
  /-- The active collar type of each collar.  Refinement stability =
  this lands in the fixed finite `T` at every stage. -/
  typeOf : ∀ r, Collar r → T
  /-- The local Euclidean repair rate, a function of active collar type only
  (branch homogeneity, tex:513-515). -/
  rate : T → ℝ
  /-- Every active collar type relaxes at a strictly positive rate
  (activity, tex:511-513). -/
  rate_pos : ∀ t, 0 < rate t

namespace AdmissibleCollarTower

variable {T : Type*} [Fintype T] [Nonempty T]

/-- Uniform floor across the whole tower: ONE modulus `c_* > 0` bounding every
collar's rate at every stage.  This is the uniformity SHAPE of #306
("uniform across locations, boundary conditions, system size, and
refinement"), conditional on the finite-type hypothesis packaged in the
structure. -/
theorem exists_uniform_floor (W : AdmissibleCollarTower T) :
    ∃ cStar : ℝ, 0 < cStar ∧ ∀ (r : ℕ) (C : W.Collar r),
      cStar ≤ W.rate (W.typeOf r C) := by
  obtain ⟨cStar, hpos, hfloor⟩ :=
    CollarGapFloor.exists_uniform_floor W.rate W.rate_pos
  exact ⟨cStar, hpos, fun r C => hfloor (W.typeOf r C)⟩

end AdmissibleCollarTower

/-! ## S2 : the commuting-color eigenvalue gap step

Skeleton of `prop:finite-gap` (tex:525-574).  After simultaneous
diagonalization of the commuting color expectations `E_{r,a}`, the modified
generator `Ltilde_r = sum_a c_* (I - E_{r,a})` acts on each joint eigenlabel
`x` by the scalar `sum over broken colors of the rate`.  Repair completeness
(tex:551-556, eq. (7)) says a label with NO broken color is constant.  The
gap step is then pure bookkeeping: a nonempty sub-sum of rates bounded below
by `c_* >= 0` is itself `>= c_*`.  We machine-check exactly that bookkeeping;
the diagonalization itself is ASSUMED via the structure below, not derived. -/

/-- The union-bound step at eigenvalue level: if every rate over the color set
`A` is `>= cStar >= 0` and the broken set `B ⊆ A` is nonempty, then the
Dirichlet eigenvalue `sum over B of the rates` is `>= cStar`
(tex:563-572: "Every nonconstant joint eigenspace has at least one color
eigenvalue zero"). -/
theorem sum_broken_ge_floor {ι : Type*} {A B : Finset ι} (hBA : B ⊆ A)
    (hB : B.Nonempty) (rates : ι → ℝ) {cStar : ℝ} (hc : 0 ≤ cStar)
    (hfloor : ∀ i ∈ A, cStar ≤ rates i) :
    cStar ≤ ∑ i ∈ B, rates i := by
  obtain ⟨i₀, hi₀⟩ := hB
  calc cStar ≤ rates i₀ := hfloor i₀ (hBA hi₀)
    _ ≤ ∑ i ∈ B, rates i :=
        Finset.single_le_sum
          (fun i hi => le_trans hc (hfloor i (hBA hi))) hi₀

/-- The simultaneously-diagonalized picture of `prop:finite-gap`: joint
eigenlabels `Λ` of the commuting color expectations, the set of colors broken
at each label, and repair completeness.  The existence of this picture is the
CONCLUSION of the commuting-family argument in the source (tex:544-556); here
it is a hypothesis container, and this file makes no claim to derive it. -/
structure CommutingColorSpectrum (ι Λ : Type*) where
  /-- The finite color set of the bounded-color decomposition (tex:526-531). -/
  colors : Finset ι
  /-- Per-color rate (in the source, the constant `c_*`; kept general). -/
  rates : ι → ℝ
  /-- The joint eigenlabels on which every color eigenvalue is one
  correspond to constants; `isConstant` marks them. -/
  isConstant : Λ → Prop
  /-- The colors whose eigenvalue at label `x` is zero. -/
  broken : Λ → Finset ι
  /-- Broken colors are colors. -/
  broken_subset : ∀ x, broken x ⊆ colors
  /-- Repair completeness, eq. (7) of the source (tex:551-556): a label fixed
  by every color is constant.  Contrapositive form. -/
  repair_complete : ∀ x, ¬ isConstant x → (broken x).Nonempty

namespace CommutingColorSpectrum

variable {ι Λ : Type*}

/-- The scalar by which the modified generator `Ltilde_r` acts on the joint
eigenlabel `x` (tex:560-562). -/
def dirichletEigenvalue (S : CommutingColorSpectrum ι Λ) (x : Λ) : ℝ :=
  ∑ i ∈ S.broken x, S.rates i

/-- The finite-stage gap certificate at eigenvalue level (skeleton of
tex:563-572, hence of eq. (5)-(6)): if the rates over the color set have the
uniform floor `cStar >= 0`, every nonconstant joint eigenlabel has Dirichlet
eigenvalue `>= cStar`. -/
theorem gap_of_floor (S : CommutingColorSpectrum ι Λ) {cStar : ℝ}
    (hc : 0 ≤ cStar) (hfloor : ∀ i ∈ S.colors, cStar ≤ S.rates i)
    (x : Λ) (hx : ¬ S.isConstant x) :
    cStar ≤ S.dirichletEigenvalue x :=
  sum_broken_ge_floor (S.broken_subset x) (S.repair_complete x hx)
    S.rates hc hfloor

end CommutingColorSpectrum

/-! ## S3 : countermodel 1 — finite-type hypothesis removed

The #306 claim boundary in miniature: per-stage positivity of the rate does
NOT give a uniform floor once the active collar-type set is allowed to grow
without bound along the tower (refinement stability removed).  The degenerate
tower has one fresh type per stage with rate `1/(n+1)`. -/

/-- Rate of the fresh collar type introduced at stage `n` of the degenerate
tower. -/
noncomputable def degenerateRate (n : ℕ) : ℝ := 1 / ((n : ℝ) + 1)

/-- Every stage of the degenerate tower has a strictly positive rate: each
FINITE stage passes the `lem:floor` activity hypothesis.  (Matches the
source's own caveat, tex:586-588: finite repair completeness gives a positive
constant at fixed regulator; uniformity is a separate receipt.) -/
theorem degenerateRate_pos (n : ℕ) : 0 < degenerateRate n := by
  unfold degenerateRate
  positivity

/-- COUNTERMODEL 1: the degenerate tower admits NO positive uniform floor.
Removing the finite active-type set (refinement stability) from `lem:floor`
kills the uniform gap even though every finite stage is gapped.  This
machine-checks the #306 claim boundary: finite-stage mixing data alone do not
give a uniform modulus. -/
theorem no_uniform_floor_of_degenerate_rates :
    ¬ ∃ cStar : ℝ, 0 < cStar ∧ ∀ n : ℕ, cStar ≤ degenerateRate n := by
  rintro ⟨cStar, hc, hfloor⟩
  obtain ⟨n, hn⟩ := exists_nat_one_div_lt hc
  exact absurd (hfloor n) (not_le.mpr hn)

/-! ## S4 : countermodel 2 — repair-completeness hypothesis removed

If some nonconstant joint eigenlabel is fixed by every color (repair
completeness fails, i.e. eq. (7) of the source is dropped), its Dirichlet
eigenvalue is 0 and no positive gap bound holds.  In the source this is the
locality/completeness leg of the acceptance criterion ("failure when each
mixing or locality hypothesis is removed"). -/

/-- A spectrum-shaped container identical to `CommutingColorSpectrum` but
WITHOUT the repair-completeness field: the structure obtained by deleting
hypothesis (7). -/
structure IncompleteColorSpectrum (ι Λ : Type*) where
  colors : Finset ι
  rates : ι → ℝ
  isConstant : Λ → Prop
  broken : Λ → Finset ι
  broken_subset : ∀ x, broken x ⊆ colors

namespace IncompleteColorSpectrum

variable {ι Λ : Type*}

/-- Dirichlet eigenvalue, as before. -/
def dirichletEigenvalue (S : IncompleteColorSpectrum ι Λ) (x : Λ) : ℝ :=
  ∑ i ∈ S.broken x, S.rates i

/-- COUNTERMODEL 2 (generic form): a nonconstant label with empty broken set
has Dirichlet eigenvalue exactly 0, so no `cStar > 0` gap bound over
nonconstant labels can hold. -/
theorem gap_collapse_of_incomplete_repair (S : IncompleteColorSpectrum ι Λ)
    {x : Λ} (hx : ¬ S.isConstant x) (hempty : S.broken x = ∅) :
    ¬ ∃ cStar : ℝ, 0 < cStar ∧
      ∀ y : Λ, ¬ S.isConstant y → cStar ≤ S.dirichletEigenvalue y := by
  rintro ⟨cStar, hc, hgap⟩
  have h0 : S.dirichletEigenvalue x = 0 := by
    unfold dirichletEigenvalue
    rw [hempty, Finset.sum_empty]
  have := hgap x hx
  rw [h0] at this
  exact absurd this (not_le.mpr hc)

end IncompleteColorSpectrum

/-- A concrete finite instance of countermodel 2: two labels, no colors, the
label `false` nonconstant and fixed by every (i.e. no) color.  Witnesses that
`IncompleteColorSpectrum` with a nonconstant fully-fixed label is inhabited,
so the collapse theorem is not vacuous. -/
def incompleteWitness : IncompleteColorSpectrum Unit Bool where
  colors := ∅
  rates := fun _ => 1
  isConstant := fun x => x = true
  broken := fun _ => ∅
  broken_subset := fun _ => Finset.Subset.refl _

theorem incompleteWitness_collapses :
    ¬ ∃ cStar : ℝ, 0 < cStar ∧
      ∀ y : Bool, ¬ incompleteWitness.isConstant y →
        cStar ≤ incompleteWitness.dirichletEigenvalue y :=
  incompleteWitness.gap_collapse_of_incomplete_repair
    (x := false) (by simp [incompleteWitness]) rfl

end CollarGapFloor
end OPH
