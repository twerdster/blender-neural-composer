"""Build a dependency-free Blender add-on ZIP from an explicit source allowlist."""
from pathlib import Path
import zipfile
ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'neural_operator_blender'
output = ROOT / 'dist' / 'blender-neural-composer-1.0.1.zip'
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(PACKAGE.rglob('*')):
        if file.is_file() and file.suffix in {'.py', '.json', '.prototxt'}:
            archive.write(file, str(file.relative_to(ROOT)))
    for relative in ['LICENSE', 'LICENSES/Unlicense.txt', 'NOTICE', 'README.md']:
        archive.write(ROOT / relative, 'neural_operator_blender/' + relative)
    # Keep README-relative guides, evidence and the real UI figure available
    # in the installed package; none of these files is executable content.
    for relative in ['updated/README.md', 'updated/assets/new-badge.svg',
                     'docs/USAGE.md', 'docs/VALIDATION.md',
                     'docs/recovery.json', 'docs/validation-5.1.json',
                     'docs/validation-5.2.json', 'docs/composer-blender-5.2.png']:
        archive.write(ROOT / relative, 'neural_operator_blender/' + relative)
print(output)
