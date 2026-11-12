"""Build a dependency-free Blender add-on ZIP from an explicit source allowlist."""
from pathlib import Path
import zipfile
ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'neural_operator_blender'
output = ROOT / 'dist' / 'blender-neural-composer-1.0.0.zip'
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(PACKAGE.rglob('*')):
        if file.is_file() and file.suffix in {'.py', '.json', '.prototxt'}:
            archive.write(file, str(file.relative_to(ROOT)))
    for relative in ['LICENSE', 'LICENSES/Unlicense.txt', 'NOTICE', 'README.md']:
        archive.write(ROOT / relative, 'neural_operator_blender/' + relative)
print(output)
