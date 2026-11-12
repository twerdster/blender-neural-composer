# Blender Neural Composer

Modern standalone continuation of the thesis Caffe-GUI-Tool by H. Tomkins,
Aaron Wetzler and Rom Hershkovitz. Six recovered research graphs are bundled
as sanitized JSON; their provenance/hashes and exact node/link counts are in
docs/recovery.json. The old public repository is preserved separately.

Version 1.0.0 supports 29 neural node types, current Blender RNA properties,
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

## README presentation (2026-11-12)

The README adds factual language, platform and existing-license badges while
preserving the original demonstration figures and all runtime, reproduction,
validation and attribution details. Keep badge claims aligned with these docs;
a presentation-only update does not establish a new build or runtime result.
