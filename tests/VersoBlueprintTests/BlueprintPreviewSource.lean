/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Emilio J. Gallego Arias
-/

import VersoBlueprintTests.BlueprintPreviewSource.Provider

open Lean
open Informal

namespace Verso.VersoBlueprintTests.BlueprintPreviewSource

/-- info: true -/
#guard_msgs in
#eval
  show CoreM Bool from do
    let some preview := Informal.PreviewSource.fromEnvironment? (← getEnv) (Name.mkSimple "preview.imported")
      | return false
    pure <| !preview.blocks.isEmpty && preview.stxs.isEmpty

end Verso.VersoBlueprintTests.BlueprintPreviewSource
