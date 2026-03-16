# Verso Upstream TODO

Items to upstream to `verso` once the blueprint split is stabilized.

## Highest Priority

- [ ] Upstream the `VersoManual` manual-rendering extension hook used by
  `VersoBlueprint.PreviewManifest`, so downstream executables no longer need a
  blueprint-local workaround for shared preview-manifest emission.
  - preserved branch: `ejgallego/verso-manual-extra-step-upstream-20260313`
  - PR shortcut:
    `https://github.com/ejgallego/verso/pull/new/verso-manual-extra-step-upstream-20260313`

- [ ] Decide whether page-level KaTeX preludes belong in core `verso`, and if
  so upstream a generic hook instead of keeping a Blueprint-owned mechanism.

## Hover and Rendering Follow-Ups

- [ ] Upstream the `Verso.Code.Highlighted` docstring rerender needed for
  dynamic hover content, then drop the local copy.

- [ ] Upstream the separate hover robustness guards in
  `Verso.Code.Highlighted`, since those look like general hardening rather than
  Blueprint-specific behavior.

## Repository Split Follow-Ups

- [ ] Move Blueprint-owned CI, release, and deploy infrastructure into the
  standalone `verso-blueprint` repository when that split is finalized.
  - current workflow copies live in `.github/workflows/`
  - current helper scripts live in `deploy/`

- [ ] Revisit the bibliography formatting cleanup in
  `VersoManual/Bibliography.lean` and decide whether it belongs upstream or
  should remain Blueprint-local.
