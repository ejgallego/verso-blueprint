/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Emilio J. Gallego Arias
-/

import VersoBlueprint
import VersoBlueprintTests.Blueprint.Support
import VersoManual

open Lean
open Verso Genre Manual
open Informal
open Verso.VersoBlueprintTests.Blueprint.Support

namespace Verso.VersoBlueprintTests.BlueprintTexSource

#docs (Manual) texSourceDoc "TeX Source" :=
:::::::
:::theorem "tex.source"
Statement body.
:::

```tex "tex.source"
\begin{theorem}\label{thm:tex-source}
For every natural number $n$, adding zero on the right leaves it unchanged.
\end{theorem}
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
      hasSubstr storedSource "\\begin{theorem}" &&
      hasSubstr storedSource "\\label{thm:tex-source}" &&
      hasSubstr storedSource "\\end{theorem}"

/-- info: true -/
#guard_msgs in
#eval
  show IO Bool from do
    let out ← renderManualDocHtmlString extension_impls% texSourceDoc
    pure <|
      !hasSubstr out "\\begin{theorem}" &&
      !hasSubstr out "thm:tex-source" &&
      !hasSubstr out "adding zero on the right leaves it unchanged"

end Verso.VersoBlueprintTests.BlueprintTexSource
