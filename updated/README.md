# Blender Neural Composer updates

## Updated and ported for modern hardware

The add-on adapts the historical Caffe-GUI-Tool node editor and exporter to
current Blender property APIs while preserving legacy node identifiers.
New graph interchange and validation code adds transactional JSON import,
saved-graph retention and safer Caffe configuration export; six recovered
graphs and an untrained compact example are bundled. Recorded checks cover
Blender 5.1.2 and 5.2.4 LTS on Apple silicon, editor operations and generated
files; the add-on does not execute networks or launch training.

### Code and setup

- [Add-on implementation](https://github.com/twerdster/blender-neural-composer/tree/main/neural_operator_blender): adapted node/export
  code and the modern graph/UI integration.
- [Install and use](../README.md#install-and-use) and
  [usage guide](../docs/USAGE.md): graph editing, deployment inputs,
  shared weights and background export.
- [Recovered graph provenance](../docs/recovery.json) and
  [source attribution](../NOTICE).

### Validation and limits

[Validation details](../docs/VALIDATION.md) distinguish editor compatibility,
JSON round trips and optional protobuf syntax checks. The
[background test](https://github.com/twerdster/blender-neural-composer/blob/main/tests/blender_test.py) exercises registration and export;
[package-installation evidence](https://github.com/twerdster/blender-neural-composer/blob/main/docs/installation-validation-1.0.1.json)
is recorded separately. Generated-definition parsing does not establish tensor
shapes, numerical inference or training. The custom Padding layer still needs
the historical research Caffe fork or an equivalent implementation.

[Project reference and licenses](../README.md#origins-and-citation)
