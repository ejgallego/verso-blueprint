/- 
Copyright (c) 2026 Lean FRO LLC. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Author: Emilio J. Gallego Arias
-/

import VersoManual
import VersoBlueprint.Commands.Common
import VersoBlueprint.StyleSwitcher

namespace Informal.BlockAssets

def codeCssAssets (blockCss : String) : List String :=
  Informal.Commands.withBlueprintCssAssets [blockCss, Verso.Genre.Manual.docstringStyle]

def blockCssAssets (blockCss : String) : List String :=
  Informal.Commands.withPreviewPanelInlinePreviewCssAssets
    [blockCss, Informal.StyleSwitcher.css, Verso.Genre.Manual.docstringStyle]

def blockJsAssets : List String :=
  Informal.Commands.withInlinePreviewJsAssets
    []
    [Informal.Commands.codeSummaryPreviewJs, Informal.Commands.usedByPanelJs, Informal.StyleSwitcher.jsInteractive]

end Informal.BlockAssets
