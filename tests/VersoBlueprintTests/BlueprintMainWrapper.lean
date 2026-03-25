/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Emilio J. Gallego Arias
-/

import VersoBlueprint.PreviewManifest

namespace Verso.VersoBlueprintTests.BlueprintMainWrapper

open Verso.Genre.Manual

/-- info: true -/
#guard_msgs in
#eval
  let cfg : RenderConfig := {}
  let cfg := Informal.PreviewManifest.withBlueprintAssets cfg
  let jsFiles := cfg.toHtmlConfig.toHtmlAssets.extraJsFiles.toArray.map (·.filename)
  let cssFiles := cfg.toHtmlConfig.toHtmlAssets.extraCssFiles.toArray.map (·.filename)
  jsFiles.contains "popper.min.js" &&
    jsFiles.contains "tippy-bundle.umd.min.js" &&
    cssFiles.contains "tippy-border.css"

/-- info: true -/
#guard_msgs in
#eval
  let customJs : JS := "console.log('custom');"
  let cfg : RenderConfig := {
    toHtmlConfig := {
      extraJs := [customJs]
    }
  }
  let cfg := Informal.PreviewManifest.withBlueprintAssets cfg
  cfg.toHtmlConfig.extraJs.toArray.any (·.js.contains "custom")

end Verso.VersoBlueprintTests.BlueprintMainWrapper
