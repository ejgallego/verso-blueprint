import Lake
open Lake DSL

-- While the split is in progress, the extracted blueprint package depends on
-- the parent repo root, which remains a checkout of Verso.
-- require verso from "../verso"
require verso from git "https://github.com/leanprover/verso"@"main"
require proofwidgets from git "https://github.com/leanprover-community/ProofWidgets4"@"v0.0.92"

package VersoBlueprint where
  precompileModules := false
  leanOptions := #[⟨`experimental.module, true⟩]

-- Blueprint core library.
@[default_target]
lean_lib VersoBlueprint where
  srcDir := "src"
  roots := #[`VersoBlueprint]

@[default_target]
lean_lib VersoBlueprintTests where
  srcDir := "tests"
  roots := #[`VersoBlueprintTests]

@[test_driver]
lean_exe «verso-blueprint-tests» where
  root := `BlueprintTestMain
  srcDir := "tests"
  supportInterpreter := true
