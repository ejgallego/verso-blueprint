import VersoManual
import VersoBlueprint.PreviewManifest
import VersoBlueprintTests.TestBlueprintRegistry
import Lean

open Verso.VersoBlueprintTests.TestBlueprintRegistry
open Lean

private def usage : IO UInt32 := do
  IO.eprintln "usage: lake exe blueprint-test-docs --list"
  IO.eprintln "   or: lake exe blueprint-test-docs --list-json"
  IO.eprintln "   or: lake exe blueprint-test-docs <slug> [verso render args]"
  pure 1

def main (args : List String) : IO UInt32 := do
  match args with
  | ["--list"] =>
    for doc in curatedTestBlueprints do
      IO.println doc.slug
    pure 0
  | ["--list-json"] =>
    IO.println <| Json.compress <| toJson <| curatedTestBlueprints.map (·.meta)
    pure 0
  | slug :: rest =>
    match findCuratedTestBlueprint? slug with
    | some doc =>
      Informal.PreviewManifest.manualMainWithSharedPreviewManifest
        doc.doc.toPart
        rest
        manualImpls
    | none =>
      IO.eprintln s!"unknown curated test blueprint `{slug}`"
      usage
  | [] => usage
