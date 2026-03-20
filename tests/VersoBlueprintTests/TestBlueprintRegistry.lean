/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Emilio J. Gallego Arias
-/

import VersoBlueprintTests.BlueprintImportedDuplicates.Direct
import VersoBlueprintTests.BlueprintImportedDuplicates.Transitive
import VersoBlueprintTests.BlueprintLinkHover
import VersoBlueprintTests.BlueprintMetadataPanel
import VersoBlueprintTests.BlueprintPreviewSource.Provider
import VersoBlueprintTests.BlueprintPreviewWiring.Shared
import VersoBlueprintTests.BlueprintPreviewWiring.StateShowcase
import VersoBlueprintTests.BlueprintSummaryLinks.Shared
import VersoBlueprintTests.BlueprintTexMacros

namespace Verso.VersoBlueprintTests.TestBlueprintRegistry

open Verso
open Verso.Genre.Manual

structure CuratedTestBlueprint where
  slug : String
  doc : Doc.VersoDoc Genre.Manual

def manualImpls : ExtensionImpls := extension_impls%

def curatedTestBlueprints : Array CuratedTestBlueprint := #[
  { slug := "hover-link", doc := Verso.VersoBlueprintTests.BlueprintLinkHover.hoverLinkDoc },
  { slug := "hover-uses-dedup", doc := Verso.VersoBlueprintTests.BlueprintLinkHover.hoverUsesDedupDoc },
  { slug := "hover-cite-only", doc := Verso.VersoBlueprintTests.BlueprintLinkHover.hoverCiteOnlyDoc },
  { slug := "widget-preview", doc := Verso.VersoBlueprintTests.BlueprintTexMacros.widgetPreviewDoc },
  { slug := "metadata-panel", doc := Verso.VersoBlueprintTests.BlueprintMetadataPanel.metadataPanelDoc },
  { slug := "direct-imported-duplicates", doc := Verso.VersoBlueprintTests.BlueprintImportedDuplicates.Direct.directImportedDuplicateDoc },
  { slug := "transitive-imported-duplicates", doc := Verso.VersoBlueprintTests.BlueprintImportedDuplicates.Transitive.transitiveImportedDuplicateDoc },
  { slug := "imported-preview-source", doc := Verso.VersoBlueprintTests.BlueprintPreviewSource.Provider.importedPreviewSourceDoc },
  { slug := "state-showcase", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.StateShowcase.stateShowcaseDoc },
  { slug := "external-summary-links", doc := Verso.VersoBlueprintTests.BlueprintSummaryLinks.Shared.externalSummaryLinksDoc },
  { slug := "summary-blockers", doc := Verso.VersoBlueprintTests.BlueprintSummaryLinks.Shared.summaryBlockersDoc },
  { slug := "summary-triage", doc := Verso.VersoBlueprintTests.BlueprintSummaryLinks.Shared.summaryTriageDoc },
  { slug := "preview-wiring", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.previewWiringDoc },
  { slug := "used-by-preview", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.usedByPreviewDoc },
  { slug := "used-by-single-preview", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.usedBySinglePreviewDoc },
  { slug := "lean-status-chip", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.leanStatusChipDoc },
  { slug := "lean-code-link-preview", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.leanCodeLinkPreviewDoc },
  { slug := "group-preview", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.groupPreviewDoc },
  { slug := "missing-group-preview", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.missingGroupPreviewDoc },
  { slug := "single-declared-group", doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.singleDeclaredGroupDoc }
]

def findCuratedTestBlueprint? (slug : String) : Option CuratedTestBlueprint :=
  curatedTestBlueprints.find? (·.slug == slug)

end Verso.VersoBlueprintTests.TestBlueprintRegistry
