# Blender Neural Composer

[![New!](updated/assets/new-badge.svg)](updated/README.md#updated-and-ported-for-modern-hardware) **[Updated and ported for modern hardware](updated/README.md#updated-and-ported-for-modern-hardware)**

[![Checked: Blender 5.2.4 LTS and 5.1.2](https://img.shields.io/badge/checked-5.2.4%20LTS%20%7C%205.1.2-E87D0D?logo=blender&logoColor=white)](docs/VALIDATION.md)
[![Blender add-on in Python](https://img.shields.io/badge/add--on-Python-3776AB?logo=python&logoColor=white)](https://github.com/twerdster/blender-neural-composer/tree/main/neural_operator_blender)
[![License: MIT and Unlicense](https://img.shields.io/badge/license-MIT%20%2B%20Unlicense-green)](NOTICE)

![Blender 5.2.4 showing the untrained compact operator graph](docs/composer-blender-5.2.png)

Blender Neural Composer is a Python add-on for editing neural-network graphs
and exporting Caffe network, solver and training-script files. Edit layer
parameters, connect branches, configure shared weights, and save graphs as
JSON or in a Blender file. Export writes definitions; the add-on does not
execute the network or launch training.

It adapts Caffe-GUI-Tool, originally by H. Tomkins and extended by Aaron
Wetzler and Rom Hershkovitz, to current Blender property APIs. It preserves the old node
identifiers so Blender can read legacy graphs after the add-on is registered.
The tested editor versions are Blender 5.2.4 LTS and 5.1.2 on Apple silicon.

The screenshot is an actual Blender capture of the bundled compact example.
Its 13 nodes and 16 links illustrate derivative, metric, flux, divergence
and update connections. It defines an architecture with no trained weights.
The six recovered research graphs preserve
intermediate architecture settings, not the final trained 80-channel
[Deep Patch-Beltrami checkpoints](https://github.com/twerdster/deep-patch-beltrami).

## Install and use

1. Download `blender-neural-composer-1.0.1.zip` from [Releases](https://github.com/twerdster/blender-neural-composer/releases/latest).
2. In Blender, open **Edit → Preferences → Add-ons → Install from Disk…** using the menu at the top right. Select the ZIP and enable **Neural Operator Composer**. Disable the old Caffe Nodes add-on first: both register the same node identifiers.
3. Open the editor-type selector at the left of any editor header and choose **Neural Operator Composer**.
4. Press **N** to show the sidebar. Open **Composer** and choose **Compact Operator Demo** or a recovered Patch-Beltrami network.
5. Use **Add → Neural Operators** to add layers. Expand a collapsed node to edit its settings; normal Blender selection, duplication, movement and linking work as usual.

Build the installable ZIP from a checkout with Python 3:

```bash
python3 tools/build_addon.py
```

The output is `dist/blender-neural-composer-1.0.1.zip`. No dependency installation is required.

## Graph operations and output

The add-on registers 29 node types covering processing, loss, data and solver
settings. JSON export retains parameters, shared-weight names, layout, colors,
sockets and links. Import restores those values; the JSON contains data only.
Graph validation rejects cycles, missing inputs and duplicate output names
before export; JSON import rejects malformed links transactionally.

**Export Caffe Solution** writes train/test, deployment and solver `.prototxt`
files plus a shell script. Set data paths and deployment dimensions on Data
nodes and the Caffe executable path on the Solver node. Those paths are
placeholders in the bundled examples. The [usage guide](docs/USAGE.md)
explains deployment inputs, shared weights, export settings and background use.

## Recovered research graphs

All six original graphs were opened read-only and converted to portable JSON. Machine-specific data and executable paths were replaced with editable placeholders. The converted JSON retains parameters, layout, sockets and links through exact round trips. Files are bundled under `examples/`.

| Original graph | Nodes | Links |
| --- | ---: | ---: |
| Base | 31 | 42 |
| Grayscale | 303 | 442 |
| Multifilter / five stages | 162 | 235 |
| Single grayscale | 30 | 43 |
| Color | 96 | 137 |
| Single color | 38 | 51 |

The Composer sidebar offers the main grayscale, color and five-stage graphs. Import the other JSON files directly. To open your own legacy `.blend` file, enable this add-on **before opening the file** so Blender can resolve its `CaffeNodeTree` and original node types. Save a new copy after checking external data paths.

## Validation and limitations

The [validation record](docs/VALIDATION.md) distinguishes editor compatibility,
JSON interchange and generated-definition parsing. Recorded checks cover all
29 node types, exact round trips for six recovered graphs, export of seven
bundled graphs and 27 processing/loss node configurations, invalid imports,
and clean registration/unregistration. The optional `protoc` check parsed
114 generated `.prototxt` files against the original research fork's schema.
That count is exported files checked for syntax, not 114 numerical or training
experiments. Parsing does not check runtime layer registration, blob shapes
or network construction.

Version 1.0.1 changes documentation, version metadata and the package file
list. The add-on implementation is unchanged from 1.0.0, which the functional
records describe.

From a source checkout, run the public background checks in an isolated Blender process:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python tests/blender_test.py
```

The stronger protobuf check additionally needs `protoc` and the external Caffe
schema; its command is in the validation guide. Caffe execution, training
convergence and final denoising metrics were not established by these editor
checks. The custom Padding layer requires the historical research Caffe fork
or an equivalent implementation. The `multistep` learning-rate schedule is
unsupported and rejected before writing files. Legacy Blender files may also
refer to external assets that this add-on does not supply.

## Origins and citation

The thesis describes the visual editor in §4.5.2 and Figure 4.17, printed pages 63–64, and cites the [2015 Caffe-GUI-Tool](https://github.com/twerdster/caffe-gui-tool). That project is a fork of [H. Tomkins' original](https://github.com/hctomkins/caffe-gui-tool), extended by Aaron Wetzler and Rom Hershkovitz. See [NOTICE](NOTICE) for source provenance and licensing.

```bibtex
@phdthesis{wetzler2017topics,
  author = {Aaron Wetzler},
  title = {Topics in Computational Geometric Vision},
  school = {Technion -- Israel Institute of Technology},
  year = {2017},
  month = {August}
}
```

Modern interface/interchange code is MIT licensed. Adapted historical node/export code and recovered research graphs retain the Unlicense; both texts are included. Blender is distributed separately under its own license.
