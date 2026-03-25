/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Emilio J. Gallego Arias
-/

import VersoBlueprint
import VersoManual

open Lean
open Verso Genre Manual
open Informal

namespace Verso.VersoBlueprintTests.BlueprintTexSource

#docs (Manual) texSourceDoc "TeX Source" :=
:::::::
:::theorem "tex.source"
Statement body.
:::

```tex "tex.source"
\alpha + \beta
```
:::::::

/-- info: true -/
#guard_msgs in
#eval
  show CoreM Bool from do
    let state := Informal.Environment.informalExt.getState (← getEnv)
    let some node := state.data.get? (Name.mkSimple "tex.source")
      | pure false
    let storedSource :=
      match node.texSource with
      | some texSource => texSource.raw.trimAscii.toString
      | none => ""
    pure <|
      node.kind == .theorem &&
      node.statement.isSome &&
      storedSource == "\\alpha + \\beta"

end Verso.VersoBlueprintTests.BlueprintTexSource
