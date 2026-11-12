# Graph editing and Caffe export

Install and enable the add-on using the [README](../README.md). The editor
writes graph data and Caffe definitions. Caffe execution requires a separate
installation, compatible layers, datasets and any trained weights.

## JSON interchange and export settings

**Export Neural Graph JSON** saves parameters, shared-weight names, layout, colors, socket names and connections. **Import Neural Graph** restores them. JSON contains data only and does not execute Python. **Validate Graph** detects cycles, missing inputs, duplicate output blobs and invalid names before Caffe export. Malformed JSON links, invalid socket indices and mismatched output names are rejected without keeping a partial graph.

**Export Caffe Solution** writes a deployment network, train/test network, solver and training shell script with quoted paths into the chosen directory. Set the Data node's deployment channels/height/width and data paths, and the Solver node's name and target Caffe executable directory. Exporting writes files; training runs separately in your own Caffe installation. Each Data node supplies the deployment shape for its image outputs, including secondary outputs consumed by inference layers. Use separate Data nodes when inputs need different shapes. The unsupported `multistep` learning-rate schedule is rejected; choose another schedule. Paths and shared-weight names are escaped for protobuf strings. The historical custom **Padding** layer requires the research Caffe fork or an equivalent implementation.

The composer includes 29 node types: convolution/deconvolution, pooling, padding, elementwise arithmetic, powers, exponentials, logs, normalization, activations, fully connected layers, concatenation/slicing, losses, data and solver settings. The operator graphs expose derivative, metric, flux, divergence and flow-update connections.

The compact demo illustrates that structure with 16 feature channels and 7×7 learnable convolution filters. It defines an architecture; no trained weights are bundled for this demo. The recovered graphs preserve historical architecture settings, including intermediate research variants; they are not replacements for the validated final 80-channel checkpoints in [Deep Patch-Beltrami](https://github.com/twerdster/deep-patch-beltrami).

## Background loading and export

Run this code inside Blender after enabling the installed add-on or adding the checkout root to `sys.path`. Use an
isolated background process for scripted checks to avoid modifying open scenes.

```python
import neural_operator_blender
from neural_operator_blender import composer, graph
neural_operator_blender.register()
tree = graph.load(composer.EXAMPLES / "patch_beltrami_multifilter.json")
composer.export_caffe(tree, "exports/five-stage")
```

## Validation scope

See [VALIDATION.md](VALIDATION.md) for the recorded editor, JSON round-trip
and protobuf parsing checks. Successful definition export does not validate
numerical execution, training convergence or denoising quality.
