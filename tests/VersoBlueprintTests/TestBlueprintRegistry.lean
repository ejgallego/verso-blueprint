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
open Lean

structure CuratedTestBlueprint where
  slug : String
  title : String
  category : String
  summary : String
  doc : Doc.VersoDoc Genre.Manual

def manualImpls : ExtensionImpls := extension_impls%

def curatedTestBlueprints : Array CuratedTestBlueprint := #[
  {
    slug := "hover-link"
    title := "Hover Link Doc"
    category := "Inline Hovers"
    summary := "Inline reference and bibliography hover coverage."
    doc := Verso.VersoBlueprintTests.BlueprintLinkHover.hoverLinkDoc
  },
  {
    slug := "hover-uses-dedup"
    title := "Hover Uses Dedup Doc"
    category := "Inline Hovers"
    summary := "Repeated uses-links against the same target without duplicate templates."
    doc := Verso.VersoBlueprintTests.BlueprintLinkHover.hoverUsesDedupDoc
  },
  {
    slug := "hover-cite-only"
    title := "Hover Cite Only Doc"
    category := "Inline Hovers"
    summary := "Bibliography-only inline hover coverage."
    doc := Verso.VersoBlueprintTests.BlueprintLinkHover.hoverCiteOnlyDoc
  },
  {
    slug := "widget-preview"
    title := "Blueprint Widget Preview"
    category := "Preview Runtime"
    summary := "Widget-side TeX prelude and preview rendering checks."
    doc := Verso.VersoBlueprintTests.BlueprintTexMacros.widgetPreviewDoc
  },
  {
    slug := "metadata-panel"
    title := "Blueprint Metadata Panel"
    category := "Summary And Metadata"
    summary := "Owner, tags, effort, priority, and PR metadata rendering."
    doc := Verso.VersoBlueprintTests.BlueprintMetadataPanel.metadataPanelDoc
  },
  {
    slug := "direct-imported-duplicates"
    title := "Direct Imported Duplicates"
    category := "Imports And Providers"
    summary := "Duplicate imported node, group, and author diagnostics."
    doc := Verso.VersoBlueprintTests.BlueprintImportedDuplicates.Direct.directImportedDuplicateDoc
  },
  {
    slug := "transitive-imported-duplicates"
    title := "Transitive Imported Duplicates"
    category := "Imports And Providers"
    summary := "Duplicate imported diagnostics through a reexport chain."
    doc := Verso.VersoBlueprintTests.BlueprintImportedDuplicates.Transitive.transitiveImportedDuplicateDoc
  },
  {
    slug := "imported-preview-source"
    title := "Imported Preview Source"
    category := "Imports And Providers"
    summary := "Imported preview bodies and cross-module preview source coverage."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewSource.Provider.importedPreviewSourceDoc
  },
  {
    slug := "state-showcase"
    title := "Blueprint Graph State Showcase"
    category := "Preview Runtime"
    summary := "Complete graph-state matrix with graph and summary pages."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.StateShowcase.stateShowcaseDoc
  },
  {
    slug := "external-summary-links"
    title := "External Summary Links"
    category := "Summary And Metadata"
    summary := "Summary links for external Lean declarations."
    doc := Verso.VersoBlueprintTests.BlueprintSummaryLinks.Shared.externalSummaryLinksDoc
  },
  {
    slug := "summary-blockers"
    title := "Summary Blockers"
    category := "Summary And Metadata"
    summary := "Missing declarations and incomplete Lean declarations in summary views."
    doc := Verso.VersoBlueprintTests.BlueprintSummaryLinks.Shared.summaryBlockersDoc
  },
  {
    slug := "summary-triage"
    title := "Summary Triage"
    category := "Summary And Metadata"
    summary := "Summary rollups by owner, tags, parent, and triage metadata."
    doc := Verso.VersoBlueprintTests.BlueprintSummaryLinks.Shared.summaryTriageDoc
  },
  {
    slug := "preview-wiring"
    title := "Blueprint Preview Wiring"
    category := "Preview Runtime"
    summary := "Core graph and summary preview runtime wiring."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.previewWiringDoc
  },
  {
    slug := "used-by-preview"
    title := "Blueprint Used-By Preview Wiring"
    category := "Relationship Panels"
    summary := "Used-by chips and preview panel behavior."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.usedByPreviewDoc
  },
  {
    slug := "used-by-single-preview"
    title := "Blueprint Used-By Single Preview Wiring"
    category := "Relationship Panels"
    summary := "Single reverse-dependency used-by rendering."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.usedBySinglePreviewDoc
  },
  {
    slug := "lean-status-chip"
    title := "Blueprint Lean Status Chip Wiring"
    category := "Summary And Metadata"
    summary := "Lean status chip rendering for proved, sorry, axiom, and absent code."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.leanStatusChipDoc
  },
  {
    slug := "lean-code-link-preview"
    title := "Blueprint Lean Code Link Preview Wiring"
    category := "Inline Hovers"
    summary := "Inline Lean declaration preview links inside the summary."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.leanCodeLinkPreviewDoc
  },
  {
    slug := "group-preview"
    title := "Blueprint Group Preview Wiring"
    category := "Relationship Panels"
    summary := "Declared group chips and group preview panel interactions."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.groupPreviewDoc
  },
  {
    slug := "missing-group-preview"
    title := "Blueprint Missing Group Preview Wiring"
    category := "Relationship Panels"
    summary := "Fallback behavior for undeclared groups."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.missingGroupPreviewDoc
  },
  {
    slug := "single-declared-group"
    title := "Blueprint Single Declared Group Wiring"
    category := "Relationship Panels"
    summary := "Declared group with only one member."
    doc := Verso.VersoBlueprintTests.BlueprintPreviewWiring.Shared.singleDeclaredGroupDoc
  }
]

def findCuratedTestBlueprint? (slug : String) : Option CuratedTestBlueprint :=
  curatedTestBlueprints.find? (·.slug == slug)

structure CuratedTestBlueprintMeta where
  slug : String
  title : String
  category : String
  summary : String
deriving ToJson

def CuratedTestBlueprint.meta (doc : CuratedTestBlueprint) : CuratedTestBlueprintMeta :=
  { slug := doc.slug, title := doc.title, category := doc.category, summary := doc.summary }

end Verso.VersoBlueprintTests.TestBlueprintRegistry
