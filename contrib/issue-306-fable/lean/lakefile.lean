import Lake
open Lake DSL

require "leanprover-community" / "mathlib" @ git "v4.29.1"

package «CollarGapFloorStaging» where
  leanOptions := #[
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩,
    ⟨`pp.unicode.fun, true⟩
  ]

@[default_target]
lean_lib «CollarGapFloor» where
  srcDir := "."
