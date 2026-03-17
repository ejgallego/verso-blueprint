import Verso
import VersoManual
import VersoBlueprint

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Addition" =>

:::group "addition.core"
Core statements about addition on natural numbers.
:::

:::author "starter.author" (name := "Project Author")
:::

:::definition "addition.spec" (parent := "addition.core")
We write $`a + b`$ for the result of adding $`b`$ to $`a`$.
This starter Blueprint begins with the most basic sanity checks around that
operation.
:::

:::theorem "addition.zero_right" (parent := "addition.core") (owner := "starter.author") (tags := "starter, arithmetic") (effort := "small") (priority := "high")
For every natural number $`n`$, adding zero on the right leaves it unchanged:
$`n + 0 = n`$.
This is the first sanity check for {uses "addition.spec"}[].
:::

:::proof "addition.zero_right"
Induct on $`n`$. The base case is immediate and the inductive step unfolds one
successor on each side.
:::

```lean "addition.zero_right"
theorem addition_zero_right (n : Nat) : n + 0 = n := by
  simp
```

:::theorem "addition.assoc" (parent := "addition.core") (lean := "Nat.add_assoc")
For all natural numbers $`a`$, $`b`$, and $`c`$, addition is associative:
$`(a + b) + c = a + (b + c)`$.
This is another consequence of {uses "addition.spec"}[].
:::

:::proof "addition.assoc"
Lean already provides this theorem as `Nat.add_assoc`, so this Blueprint entry
links to an existing declaration instead of restating the code locally.
:::
