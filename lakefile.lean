import Lake
open Lake DSL

-- While the split is in progress, the extracted blueprint package depends on
-- the parent repo root, which remains a checkout of Verso.
-- require verso from "../verso"
require verso from git "https://github.com/leanprover/verso"@"main"

-- Blueprints depend directly on Mathlib.
require mathlib from git "https://github.com/leanprover-community/mathlib4"@"v4.29.0-rc6"

package VersoBlueprint where
  precompileModules := false
  leanOptions := #[⟨`experimental.module, true⟩]

-- Blueprint core library.
@[default_target]
lean_lib VersoBlueprint where
  srcDir := "src"
  roots := #[`VersoBlueprint]

-- An example of a "math blueprint" project built in Verso.
lean_lib Noperthedron where
  srcDir := "test-projects/Noperthedron"
  roots := #[`Authors, `Contents, `Chapters, `Noperthedron, `Bibliography, `Macros]

@[default_target]
lean_exe noperthedron where
  srcDir := "test-projects/Noperthedron"
  root := `Main
  supportInterpreter := true

-- Port of the Sphere Packing TeX blueprint to Verso Blueprints.
lean_lib SpherePackingBlueprint where
  srcDir := "test-projects/Sphere-Packing-Lean"
  roots := #[`SpherePackingBlueprint]

@[default_target]
lean_exe spherepackingblueprint where
  srcDir := "test-projects/Sphere-Packing-Lean"
  root := `SpherePackingBlueprintMain
  supportInterpreter := true

@[default_target]
lean_lib VersoBlueprintTests where
  srcDir := "tests"
  roots := #[`VersoBlueprintTests]

@[test_driver]
lean_exe «verso-blueprint-tests» where
  root := `BlueprintTestMain
  srcDir := "tests"
  supportInterpreter := true
