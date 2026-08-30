from pathlib import Path
import json
import re
import shutil
import struct

workspace = Path(__file__).resolve().parent.parent
src = workspace / '3d models'
dst = workspace / 'app' / 'static' / 'models' / 'raigad'

def normalize_name(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', value.lower())

pairs = {
    'royalpalace': 'royal-palace.glb',
    'queenspalace': 'queens-palace.glb',
    'royalcomplex': 'royal-complex.glb',
    'marketplace': 'marketplace.glb',
    'manore': 'manore.glb',
    'pleasurepavilions': 'pleasure-pavilions.glb',
    'wadeshwartemple': 'wadeshwar-temple.glb',
    'khubladaburuj': 'khublada-buruj.glb',
}

source_candidates = sorted(src.glob('*.glb')) if src.exists() else []
for key, target_name in pairs.items():
    matched = None
    for candidate in source_candidates:
        candidate_norm = normalize_name(candidate.name)
        if key in candidate_norm:
            matched = candidate
            break

    if matched is None:
        print(f'missing {target_name} (no matching source file found for key: {key})')
        continue

    target = dst / target_name
    shutil.copy2(matched, target)
    print(f'copied {matched.name} -> {target_name}')

print('\nMaterial color check:')
for target_name in sorted(pairs.values()):
    path = dst / target_name
    if not path.exists():
        print(f'{target_name}: file missing')
        continue
    data = path.read_bytes()
    if data[:4] != b'glTF':
        print(f'{target_name}: not binary glTF')
        continue
    try:
        json_len, _ = struct.unpack('<II', data[12:20])
        chunk = data[20:20 + json_len]
        root = json.loads(chunk.decode('utf-8'))
        materials = root.get('materials') or []
        material_status = []
        for material in materials:
            pbr = material.get('pbrMetallicRoughness', {})
            base = pbr.get('baseColorFactor')
            if base and base != [1.0, 1.0, 1.0, 1.0]:
                material_status.append(f'color:{base}')
            elif pbr.get('baseColorTexture'):
                material_status.append('texture')
            else:
                material_status.append('default')
        print(f'{target_name}: {material_status[:3]} ... total {len(materials)} materials')
    except Exception as exc:
        print(f'{target_name}: unable to inspect material colors ({exc})')
