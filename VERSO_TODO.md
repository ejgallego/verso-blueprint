# VERSO_TODO

Items to upstream to `verso` once the blueprint split is stabilized.

- [ ] Upstream the `VersoManual` manual-rendering extension hook:
  - global `registerExtraStep` / `registeredExtraSteps`
  - exported render-option parser for blueprint preview tooling
  - motivation: `VersoBlueprint.PreviewManifest` currently needs a blueprint-local workaround to attach the shared preview manifest emission step without modifying every downstream executable by hand
  - preserved branch: `ejgallego/verso-manual-extra-step-upstream-20260313`
  - PR shortcut: `https://github.com/ejgallego/verso/pull/new/verso-manual-extra-step-upstream-20260313`
  - target: land this in `verso` soon, then remove the blueprint-local workaround in `VersoBlueprint/PreviewManifest.lean`

- [ ] Consider upstreaming a generic page-level KaTeX prelude registry / renderer hook to `verso`:
  - current blueprint workaround restores root `static-web/math.js` to base and uses `verso-blueprint/static-web/math.js`
  - blueprint pages inject one `bpTexPreludeTable` entry once per page and math nodes carry `data-bp-tex-prelude-id`
  - if `verso` wants local math preludes generally, this should become a generic core mechanism rather than a blueprint-owned fork
