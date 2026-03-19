import Verso
import VersoManual
import VersoBlueprint

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Preview Relationships" =>

:::definition "used_target" (lean := "Nat.add")
Target statement with associated Lean code.
:::

:::lemma_ "used_statement"
Statement depends on {uses "used_target"}[].
:::

:::theorem "used_proof"
Statement facet marker for preview relationships.
:::

:::proof "used_proof"
Proof facet marker for preview relationships, depending on {uses "used_target"}[].
:::

:::theorem "preview_facets"
Statement facet marker for preview relationships.
:::

:::proof "preview_facets"
Proof facet marker for preview relationships.
:::
