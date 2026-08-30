"""Export the supplied Raigad Blender reconstructions as browser-ready GLB files.

Run with Blender, not regular Python:
  blender --background --python scripts/export_raigad_models.py
"""

from pathlib import Path

import bpy


SOURCE_DIRECTORY = Path(r"C:\Users\user\Downloads\3d models\Raigad")
OUTPUT_DIRECTORY = Path(__file__).resolve().parents[1] / "app" / "static" / "models" / "raigad"

MODELS = {
    "Marketplace_final.blend": "marketplace.glb",
    "royalpalace_final.blend": "royal-palace.glb",
    "Manore_final.blend": "manore.glb",
    "Pleasure Pavilions_final.blend": "pleasure-pavilions.glb",
    "Wadeshwar_Temple_colour_final.blend": "wadeshwar-temple.glb",
    "Queens_palace_colour_final.blend": "queens-palace.glb",
    "Royal Complex_colour_final.blend": "royal-complex.glb",
    "khublada_buruj_coloured_final.blend": "khublada-buruj.glb",
}


def export_models() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for source_name, output_name in MODELS.items():
        source = SOURCE_DIRECTORY / source_name
        destination = OUTPUT_DIRECTORY / output_name
        if not source.is_file():
            raise FileNotFoundError(f"Model not found: {source}")
        bpy.ops.wm.open_mainfile(filepath=str(source))
        bpy.ops.export_scene.gltf(
            filepath=str(destination),
            export_format="GLB",
            export_apply=True,
            export_materials="EXPORT",
            export_yup=True,
        )
        print(f"Exported {destination.name}")


if __name__ == "__main__":
    export_models()
