import Verso
import VersoManual
import VersoBlueprint

open Verso.Genre
open Verso.Genre.Manual
open Informal

namespace PreviewRuntimeShowcase.CodePanelDecls

def previewExternalDefinition : Nat := 0

theorem previewExternalTheorem : True := by
  trivial

theorem previewExternalSorry : True := by
  sorry

end PreviewRuntimeShowcase.CodePanelDecls

#doc (Manual) "Code Panels" =>

:::definition "panel_external_definition" (lean := "PreviewRuntimeShowcase.CodePanelDecls.previewExternalDefinition")
External definition panel sample.
:::

:::theorem "panel_external_theorem" (lean := "PreviewRuntimeShowcase.CodePanelDecls.previewExternalTheorem")
External theorem panel sample.
:::

:::theorem "panel_external_warning" (lean := "PreviewRuntimeShowcase.CodePanelDecls.previewExternalSorry")
External theorem panel with a sorry-backed declaration.
:::

:::definition "panel_inline_progress"
Inline code panel sample with mixed declaration health.
:::

```lean "panel_inline_progress"
def panelInlineOk : Nat := 0

theorem panelInlineSorry : True := by
  sorry
```
