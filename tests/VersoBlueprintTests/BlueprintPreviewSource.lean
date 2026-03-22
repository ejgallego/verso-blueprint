/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Emilio J. Gallego Arias
-/

import VersoBlueprintTests.Blueprint.Support
import VersoBlueprintTests.BlueprintPreviewSource.Provider

open Lean
open Informal
open Verso.VersoBlueprintTests.Blueprint.Support

namespace Verso.VersoBlueprintTests.BlueprintPreviewSource

/-- info: true -/
#guard_msgs in
#eval
  show CoreM Bool from do
    let some preview := Informal.PreviewSource.fromEnvironment? (← getEnv) (Name.mkSimple "preview.imported")
      | return false
    pure <| !preview.blocks.isEmpty && preview.stxs.isEmpty

/-- info: true -/
#guard_msgs in
#eval
  show IO Bool from do
    let (_out, st) ← renderManualDocHtmlStringAndState extension_impls%
      Verso.VersoBlueprintTests.BlueprintPreviewSource.Provider.proofFallbackPreviewSourceDoc
    let label := Name.mkSimple "preview.proof_fallback"
    let entry? := Informal.PreviewSource.traversalEntry? st label
    let lookupKey? := Informal.PreviewSource.traversalLookupKey? st label
    pure <|
      match entry?, lookupKey? with
      | some entry, some lookupKey =>
        entry.facet == .proof &&
        !entry.blocks.isEmpty &&
        lookupKey == PreviewCache.key label .proof
      | _, _ => false

end Verso.VersoBlueprintTests.BlueprintPreviewSource
