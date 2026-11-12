# Validation

The source and installable add-on were checked with official **Blender 5.2.4 LTS** (2026-11-10 release) and installed **Blender 5.1.2** on Apple silicon. The isolated 5.2.4 download was checked against Blender's official SHA-256 list; the system Blender installation and unrelated scenes were preserved.

The historical add-on could register its classes, but a newly created convolution's `num_output` was a `_PropertyDeferred` object rather than an editable integer. The port registers current annotated RNA properties, including inherited shared-weight settings and nested parameter groups.

The checks cover:

- All 29 node types register; declared parameters have usable values and are editable.
- All six recovered research graphs retain declared node parameters, layout, colors, socket names and connections through exact JSON round trips. Their original source checksums are in [recovery.json](recovery.json).
- All seven bundled graphs and each of 27 independent processing/loss node configurations export without changing their graphs.
- All **114 generated prototxt files** parse with `protoc` against the original research Caffe fork's schema, including its custom Padding parameters.
- Tiny float values survive export. Quoted/backslash paths and shared-weight names retain their exact values through protobuf encode/decode for three data backends.
- Edited graphs declare secondary Data outputs consumed by deployment layers. Unsupported multistep schedules fail before creating files.
- Cyclic/incomplete/unknown-type graphs, duplicate destination links, invalid socket indices, missing references and mismatched output counts are rejected without retaining partial imports.
- The add-on can be disabled and re-enabled cleanly. A built ZIP was installed into a fresh isolated Blender 5.2 add-on directory, enabled, and used to load the compact demo, then disabled after removing its temporary graph.
- The README image is an actual isolated Blender 5.2.4 UI screenshot of the bundled untrained operator demo. No rendered simulation or generated UI mockup is used.

Machine-readable outcomes are [5.1](validation-5.1.json) and [5.2](validation-5.2.json). The public test accepts an optional external schema for the stronger protobuf syntax check:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python tests/blender_test.py -- result.json --caffe-proto /path/to/caffe.proto
```

These checks validate the composer, data interchange and generated definitions. They do not run Caffe training or establish numerical parity for intermediate research architectures. Deployment input dimensions and dataset/executable paths are editable values. Final trained Deep Patch-Beltrami inference is validated separately in its own repository.

## Documentation package 1.0.1

The implementation checks above were recorded on 1.0.0. Version 1.0.1 changes
prose, version metadata and the package file list. All ten bundled
documentation/license files match source. A rebuilt ZIP was extracted into an
isolated add-on directory, enabled with Blender 5.1.2, used to load the
13-node/16-link demo, and disabled after removing that temporary graph.
The [package check](https://github.com/twerdster/blender-neural-composer/blob/main/docs/installation-validation-1.0.1.json) is installation evidence,
not a new Caffe execution, numerical-parity or training result. The current
[release pin](https://github.com/twerdster/blender-neural-composer/blob/main/docs/release.json) and [original 1.0.0 pin](https://github.com/twerdster/blender-neural-composer/blob/main/docs/release-1.0.0.json) are separate.
