# Maintain Blender Neural Composer

Read SUMMARY.md then README.md, NOTICE and docs/recovery.json before changes.
Keep SUMMARY.md and this file synchronized before commits.

The installable module is neural_operator_blender. caffe_nodes.py and
caffe_export.py adapt the historical Unlicense project; composer.py contains
the current Blender UI/export orchestration, graph.py the portable data format.
Keep fake users on newly created/imported graphs so they survive .blend saves.
Preserve legacy CaffeNodeTree and node/socket IDs. Register socket/property
groups before nodes and unregister in reverse. New RNA properties use class
annotations. Shared-weight mixin properties must be registered on concrete nodes.

Run tests/blender_test.py with an isolated `--background --factory-startup`
Blender process. Test both supported versions after API changes. Compare all
six recovered examples exactly through JSON roundtrip and verify Caffe export
does not mutate graph parameters. Test invalid graphs/imports and clean
unregister/register. Check quoted paths/shared names through external protobuf
encode/decode, secondary deployment inputs, and malformed JSON/socket-count cases.
All text fields use caffe_export.proto_string; all consumed Data outputs need
deployment declarations. Inputs with different shapes need separate Data nodes.
Unsupported multistep schedules must fail before writing. Never operate on unrelated open Blender scenes.

Build the release ZIP with `python3 tools/build_addon.py`; the allowlist includes
source, JSON graphs, operator coefficient files and license/readme notices.
No training data, trained weights, compiled dependencies or .blend files belong
in this package. The compact example is illustrative and untrained; preserve
that label. Caffe graph export is separate from external runtime/training tests.
Do not claim the intermediate recovered architectures equal final published
checkpoint graphs. Maintain upstream H. Tomkins and Rom Hershkovitz attribution.

## Documentation maintenance

Read SUMMARY.md, then this file, README, linked setup/validation records and
relevant source before revising claims. Write concrete inputs, operations and
outputs; keep current implementation, historical aims and recorded evidence
separate. Label synthetic/untrained figures and schematics. Keep metric units,
implementation, hardware, sample count and measurement scope with the claim.
Source inspection or file export does not establish numerical execution or
training. Preserve original attribution, licenses and validation limitations.

Rebuild distributions when README metadata or bundled guides change; compare
installed documentation with source. For substantial prose revisions, request
an actual Claude review if directed, verify its factual suggestions and review
the revision again. Never claim a review or runtime check that did not complete.
Review and synchronize both context files before every commit.

## Modern update navigation

Keep the local New! badge and exact “Updated and ported for modern hardware”
link immediately below the root README title. Put the brief change description
and further update links in `updated/README.md` under the matching heading;
retain the existing reference body and implementation paths. Check the badge,
relative links and README body preservation after navigation-only changes.
Do not reinterpret historical validation as a new runtime check.

The add-on ZIP must include `updated/README.md` and `updated/assets/new-badge.svg`
so the installed README navigation remains available. Keep those two explicit
documentation entries in the package allowlist and verify their extracted bytes.
