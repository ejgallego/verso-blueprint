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

axiom previewExternalAxiom : True

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

:::definition "panel_external_missing" (lean := "PreviewRuntimeShowcase.CodePanelDecls.previewExternalMissing")
External declaration panel with a missing declaration.
:::

:::theorem "panel_external_axiom" (lean := "PreviewRuntimeShowcase.CodePanelDecls.previewExternalAxiom")
External theorem panel with an axiom-like declaration.
:::

:::definition "panel_inline_proved"
Inline code panel sample with complete Lean code.
:::

```lean "panel_inline_proved"
def panelInlineOnlyOk : Nat := 0
```

:::definition "panel_inline_warning"
Inline code panel sample with a sorry-backed declaration.
:::

```lean "panel_inline_warning"
theorem panelInlineOnlySorry : True := by
  sorry
```

:::definition "panel_inline_progress"
Inline code panel sample with mixed declaration health.
:::

```lean "panel_inline_progress"
def panelInlineOk : Nat := 0

theorem panelInlineSorry : True := by
  sorry
```

:::definition "panel_inline_axiom"
Inline code panel sample with an axiom-like declaration.
:::

```lean "panel_inline_axiom"
axiom panelInlineAxiom : True
```

:::definition "panel_no_code"
Statement without associated Lean code.
:::
