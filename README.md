# ComfyUI-Clean-Alpha

A ComfyUI custom node for cleaning alpha channels on individual RGB/RGBA images.

> **AI Disclaimer:** This project and its documentation were created with the assistance of AI. The code should be reviewed, tested, and validated by the user before use in production workflows.

## Inputs

- **Image** — RGB or RGBA image.
- **Maximum** — Alpha values above this threshold are set to `255`.
  - Default: `250`
  - Range: `0–255`
  - Set to `255` to disable.
- **Minimum** — Alpha values below this threshold are set to `0`.
  - Default: `5`
  - Range: `0–255`
  - Set to `0` to disable.
- **Convert to RGB** — If enabled, removes the alpha channel when every pixel is fully opaque (`255`).

## Behavior

- **RGB images:** Passed through unchanged.
- **RGBA images:** The alpha channel is cleaned using the Maximum and Minimum thresholds.
- If the resulting alpha channel is completely opaque and **Convert to RGB** is enabled, the output is converted to RGB.
- Otherwise, the output remains RGBA.
- The node is intended for **single-image use**.

## Output

- **Image** — Cleaned RGB or RGBA image.
