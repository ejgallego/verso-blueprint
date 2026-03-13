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

- [ ] Upstream the `Verso.Code.Highlighted` docstring rerender for dynamic hover content:
  - current local copy lives in `src/verso/Verso/Code/Highlighted.lean`
  - blueprint motivation: `VersoBlueprint.DocGenNameRender` emits local hover payloads containing `<pre class="docstring">...</pre>`
  - without rerendering docstrings after hover content is inserted, blueprint declaration hovers would regress to raw docstring blocks
  - keep the local copy until the upstream version lands

- [ ] Upstream the `Verso.Code.Highlighted` hover robustness guards as a separate change:
  - current local copy lives in `src/verso/Verso/Code/Highlighted.lean`
  - guards `tactic` hovers when `.tactic-state` is missing
  - guards missing `parentElement` when reading `data-verso-links`
  - this looks like general core hardening rather than blueprint-specific behavior, so it should be reviewed independently from the docstring feature

- [ ] Split out blueprint-owned CI / release / deploy infrastructure for the future standalone `verso-blueprint` repository:
  - current local copies live in `.github/workflows/{ci,merge-main-nightly,update-nightly,overlay,release-tag,upload-snapshots}.yml`
  - current helper scripts live in `deploy/{build.sh,generate.sh,overlay.py,prep.sh,release.py,release_utils.py}`
  - this is not core `verso` drift to upstream; it should move with the future `verso-blueprint` repository
  - remember to carry the local composite action `./.github/actions/install-texlive`
  - rebrand/reconfigure standalone deployment details:
    - canonical base URL in `deploy/overlay.py`
    - Netlify site id / hosting secrets in `upload-snapshots.yml`
    - artifact naming assumptions in `deploy/generate.sh`
