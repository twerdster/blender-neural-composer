# Blender Neural Composer

Python add-on adapting Caffe-GUI-Tool, originally by H. Tomkins and extended
by Aaron Wetzler and Rom Hershkovitz. Six recovered research graphs are bundled
as sanitized JSON; their provenance/hashes and exact node/link counts are in
docs/recovery.json. The old public repository is preserved separately.

The 1.0.0 implementation, retained in package 1.0.1, supports 29 neural node types, current Blender RNA properties,
shared-weight settings, JSON import/export with saved-graph retention, graph validation, and Caffe
train/test/deployment/solver/script export. It writes definitions and does
not launch training. The illustrative compact operator has untrained weights.
The final trained Deep Patch-Beltrami models live in their separate repository.

Validation targets are Blender 5.2.4 LTS and 5.1.2 on Apple silicon. Commands:
`blender --background --factory-startup --python-exit-code 1 --python tests/blender_test.py`
and `python3 tools/build_addon.py`. The installable ZIP is under ignored dist/.
Public validation JSON and an actual isolated Blender 5.2 screenshot are in docs/.

The core adaptation keeps original node identifiers to load legacy .blend
files after registering the add-on. It fixes outdated property declarations,
modern layout calls, graph-cycle errors, low-precision scalar serialization,
MVN/Exp parameter export, protobuf string escaping, secondary deployment inputs,
safe script quoting and export mutation. Malformed JSON links/output counts are
rejected transactionally; unsupported multistep schedules fail before writing. JSON
interchange contains data only. Dataset/checkpoint/executable paths in examples
are editable placeholders. Caffe execution and custom Padding support require
an external Caffe installation and are not end-to-end training validation.

New code is MIT; adapted historical code/graphs/coefficient assets retain the
Unlicense. Read NOTICE and both license texts. Do not publish original .blend
files, private backup paths, manuscript sources or machine-specific credentials.

Root review reran the full5.2.4 suite with the original Caffe schema after
whitespace normalization. Release asset size/hash are pinned in docs/release.json.

## Maintainer documentation and package 1.0.1 — 2026-11-12

The README explains graph editing, JSON interchange and Caffe file export.
The screenshot is the untrained 13-node/16-link architecture, not an executed
denoising result. Detailed settings and background examples moved to
`docs/USAGE.md`. The 114-file count is optional protobuf syntax checking,
not numerical execution, shape validation or training. Original author and
MIT/Unlicense boundaries remain explicit.

Package 1.0.1 changes documentation, version metadata and the builder file
allowlist. It includes the README-relative guides, evidence and actual UI
image. All ten bundled documentation/license files were compared with source;
the rebuilt ZIP was extracted into a task-isolated add-on directory and enabled
in Blender 5.1.2. Its compact graph loaded with 13 nodes/16 links, then the
temporary graph and add-on were removed. This is packaging/registration evidence;
1.0.0 functional checks remain the source of the broader editor/export claims.
`docs/installation-validation-1.0.1.json` records this distinction. The original
release pin remains in `docs/release-1.0.0.json`; `docs/release.json` pins 1.0.1.

Actual Claude reviews of the draft and substantial revision completed, with
factual suggestions checked against JSON and source. No numerical operator,
graph, coefficient, exporter behavior or original license was changed.
