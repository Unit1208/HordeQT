import os
from pathlib import Path

from PIL import Image


def convert_icon(icon_path, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the original icon image
    icon = Image.open(icon_path)

    # Define output sizes
    sizes = [16, 32, 64, 128, 256, 512]

    # Convert to PNGs at different sizes
    for size in sizes:
        resized_icon = icon.resize((size, size), Image.Resampling.BICUBIC)
        resized_icon.save(os.path.join(output_dir, f"icon-{size}.png"))

    # Convert to .icns (macOS icon format)
    if icon.mode != "RGBA":
        icon = icon.convert("RGBA")  # Ensure the icon has an alpha channel
    icon.save(os.path.join(output_dir, "icon.icns"), format="ICNS")

    # Convert to .ico (Windows icon format)
    icon.save(
        os.path.join(output_dir, "icon.ico"),
        format="ICO",
        sizes=[(size, size) for size in sizes],
    )


if __name__ == "__main__":
    convert_icon("../src/hordeqt/resources/Icon.png", "../src/hordeqt/resources/icons")
