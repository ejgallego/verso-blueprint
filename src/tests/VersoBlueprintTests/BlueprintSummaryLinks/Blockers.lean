/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: OpenAI Codex
-/

import VersoBlueprintTests.BlueprintSummaryLinks.Shared

namespace Verso.VersoBlueprintTests.BlueprintSummaryLinks.Blockers

open Verso.VersoBlueprintTests.Blueprint.Support
open Verso.VersoBlueprintTests.BlueprintSummaryLinks.Shared

/-- info: true -/
#guard_msgs in
#eval
  show IO Bool from do
    let out ← renderManualDocHtmlString manualImpls summaryBlockersDoc
    pure (
      hasSubstr out "Blockers (2)" &&
      hasSubstr out "Missing external Lean declarations (1)" &&
      hasSubstr out "Incomplete Lean declarations (1)" &&
      !hasSubstr out "Incomplete details ("
    )

end Verso.VersoBlueprintTests.BlueprintSummaryLinks.Blockers
