"""
KrushiSetu Leaf Authenticity & Foliage Validation Engine
Distinguishes real agricultural plant leaves from non-plant images such as
notebook pages, lined paper, text documents, screenshots, and random objects.
Uses botanical color gamut metrics (Excess Green, Chlorophyll/Carotenoid/Necrosis ratios),
neutral paper/monochrome detection, edge gradient regularity, and spatial coherence.
"""

import numpy as np
from PIL import Image

def validate_leaf_image(image_path: str) -> dict:
    """
    Analyzes an image to verify whether it contains an authentic plant leaf.
    
    Returns:
        dict: {
            "is_valid": bool,
            "reason": str,
            "botanical_pct": float,
            "neutral_pct": float,
            "mean_sat": float,
            "message": str,
            "instructions": list[str]
        }
    """
    try:
        with Image.open(image_path) as raw_img:
            img = raw_img.convert("RGB")
    except Exception as e:
        return {
            "is_valid": False,
            "reason": "unreadable_image",
            "botanical_pct": 0.0,
            "neutral_pct": 100.0,
            "mean_sat": 0.0,
            "message": f"Unable to read image file: {str(e)}",
            "instructions": [
                "Ensure the file is a valid image (JPG, PNG, WebP).",
                "Try capturing or saving the image again."
            ]
        }

    # Resize to standardized dimensions for fast, consistent analysis
    img_thumb = img.resize((256, 256), Image.Resampling.BILINEAR)
    arr = np.array(img_thumb, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    total_pixels = 256 * 256

    # 1. Neutral / Grayscale / Paper Test
    # Paper, notebook pages, document scans, and monochrome objects have minimal chromatic variance:
    # |R - G| < 14 and |G - B| < 14 and |R - B| < 14
    diff_rg = np.abs(r - g)
    diff_gb = np.abs(g - b)
    diff_rb = np.abs(r - b)
    neutral_mask = (diff_rg < 14) & (diff_gb < 14) & (diff_rb < 14)
    neutral_pct = float(np.sum(neutral_mask) / total_pixels * 100.0)

    # 2. HSV Saturation & Value
    hsv_arr = np.array(img_thumb.convert("HSV"), dtype=np.float32)
    sat = hsv_arr[:, :, 1]
    val = hsv_arr[:, :, 2]
    mean_sat = float(sat.mean())
    high_sat_pct = float(np.sum(sat > 40) / total_pixels * 100.0)

    # 3. Botanical Foliage Spectrum (Chlorophyll, Carotenoid, Necrotic Foliar Blight)
    # (a) Green Chlorophyll: G significantly higher than R and B, Excess Green (2G - R - B) > 15
    green_mask = (g > r + 5) & (g > b + 5) & ((2.0 * g - r - b) > 15)

    # (b) Foliar Yellow / Chlorosis: High R & G, low B (R > 85, G > 75, B < min(R, G) - 18)
    min_rg = np.minimum(r, g)
    yellow_mask = (r > 85) & (g > 75) & (b < (min_rg - 18))

    # (c) Necrotic Blight / Plant Brown / Scorch: Brown leaf tissue with earthy pigment
    # R > 65, G > 35, R > G, G > B + 12, R < 240
    brown_mask = (r > 65) & (g > 35) & (r > g) & (g > b + 12) & (r < 240)

    botanical_mask = green_mask | yellow_mask | brown_mask
    botanical_pct = float(np.sum(botanical_mask) / total_pixels * 100.0)

    # 4. Spatial Coherence & Natural Gradient vs Synthetic Noise / Line Patterns
    gray = np.array(img_thumb.convert("L"), dtype=np.float32)
    row_diff = np.abs(gray[1:, :] - gray[:-1, :])
    col_diff = np.abs(gray[:, 1:] - gray[:, :-1])
    mean_gradient = float((row_diff.mean() + col_diff.mean()) / 2.0)

    # Notebook line regularity
    mean_horiz = row_diff.mean(axis=1)
    line_peaks = int(np.sum(mean_horiz > (1.8 * mean_horiz.mean())))

    # Multi-Factor Rejection Heuristics
    is_valid = True
    reason = "valid_leaf"
    message = "Authentic crop leaf detected."

    # Condition 1: Dominantly neutral / paper / document / notebook page
    if neutral_pct >= 72.0 or (neutral_pct >= 55.0 and botanical_pct < 12.0):
        is_valid = False
        reason = "notebook_or_paper_detected"
        message = "Invalid image: Uploaded photo appears to be a notebook page, lined paper, or document rather than a real crop leaf."

    # Condition 2: Synthetic noise or extreme high-frequency disturbance
    elif mean_gradient > 38.0 and botanical_pct < 40.0:
        is_valid = False
        reason = "synthetic_noise_or_distortion"
        message = "Invalid image: Photo is noisy or distorted. Please upload a clear photo of an actual plant leaf."

    # Condition 3: Very low saturation / grayscale
    elif mean_sat < 15.0 and botanical_pct < 10.0:
        is_valid = False
        reason = "grayscale_or_achromatic"
        message = "Invalid image: Uploaded photo lacks botanical color pigmentation (black-and-white, screen, or document)."

    # Condition 4: Absence of botanical foliage / chlorophyll / leaf tissue
    elif botanical_pct < 8.0:
        is_valid = False
        reason = "no_foliage_detected"
        message = "Invalid image: No plant foliage or crop leaf features detected in the uploaded photo."

    # Condition 5: Notebook line pattern with low botanical content
    elif line_peaks > 35 and neutral_pct > 45.0 and botanical_pct < 15.0:
        is_valid = False
        reason = "notebook_lines_detected"
        message = "Invalid image: Detected notebook lines and paper background. Please upload a photo of a crop leaf."

    instructions = [
        "Take a direct close-up photo of a crop plant leaf (e.g. Tomato, Corn, Bell Pepper).",
        "Make sure the leaf covers the central frame of the camera.",
        "Ensure clear natural lighting without shadows, glare, or blur.",
        "Do not upload drawings, notebook pages, documents, or screenshots."
    ]

    return {
        "is_valid": is_valid,
        "reason": reason,
        "botanical_pct": round(botanical_pct, 2),
        "neutral_pct": round(neutral_pct, 2),
        "mean_sat": round(mean_sat, 2),
        "high_sat_pct": round(high_sat_pct, 2),
        "message": message,
        "instructions": instructions
    }
