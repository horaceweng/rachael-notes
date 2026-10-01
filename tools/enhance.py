import numpy as np
from PIL import Image, ImageFilter


def enhance(img: Image.Image) -> Image.Image:
    """Flatten uneven paper lighting, then stretch levels so the paper is white and ink is dark."""
    rgb = np.asarray(img.convert("RGB")).astype(np.float32)
    # Paper background estimate: downscale, max-filter (removes ink strokes), blur, upscale.
    small = img.convert("RGB").resize((img.width // 8, img.height // 8), Image.BILINEAR)
    bg = small.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(6))
    bg = np.asarray(bg.resize(img.size, Image.BILINEAR)).astype(np.float32)
    norm = np.clip(rgb / np.maximum(bg, 1) * 255, 0, 255)  # paper -> ~255, colour preserved
    # Levels: map [black, white] -> [0, 255] with gamma < 1 darkening mid-tones (pencil/ink).
    black, white, gamma = 40.0, 250.0, 1.8
    x = np.clip((norm - black) / (white - black), 0, 1) ** gamma
    return Image.fromarray((x * 255).astype(np.uint8))
