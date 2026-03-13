/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: OpenAI Codex
-/

import VersoBlueprintTests.BlueprintPreviewWiring.Shared

namespace Verso.VersoBlueprintTests.BlueprintPreviewWiring.LeanStatus

open Verso.VersoBlueprintTests.Blueprint.Support
open Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared

/-- info: true -/
#guard_msgs in
#eval
  show IO Bool from do
    let out ← renderManualDocHtmlString manualImpls leanStatusChipDoc
    pure (
      hasSubstr out "bp_code_link_status_proved" &&
      hasSubstr out "bp_code_link_status_warning" &&
      hasSubstr out "bp_code_link_status_axiom" &&
      hasSubstr out "bp_code_link_status_absent" &&
      hasSubstr out ">✓</span>" &&
      hasSubstr out ">⚠</span>" &&
      hasSubstr out ">A</span>" &&
      hasSubstr out ">X</span>"
    )

end Verso.VersoBlueprintTests.BlueprintPreviewWiring.LeanStatus
