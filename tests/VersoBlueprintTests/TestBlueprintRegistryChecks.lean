/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Emilio J. Gallego Arias
-/

import VersoBlueprintTests.TestBlueprintRegistry

namespace Verso.VersoBlueprintTests.TestBlueprintRegistryChecks

open Verso.VersoBlueprintTests.TestBlueprintRegistry

/-- info: true -/
#guard_msgs in
#eval
  let metas := curatedTestBlueprints.map (·.meta)
  let categories := metas.map (·.category)
  !metas.isEmpty &&
    categories.all (fun c => c.trimAscii.toString.length > 0) &&
    categories.contains "Inline Hovers" &&
    categories.contains "Preview Runtime" &&
    categories.contains "Relationship Panels" &&
    categories.contains "Summary And Metadata" &&
    categories.contains "Imports And Providers"

end Verso.VersoBlueprintTests.TestBlueprintRegistryChecks
