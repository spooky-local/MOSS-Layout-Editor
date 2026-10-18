"""MOSS Layout Editor node.

The browser editor (web/moss_layout_editor.js) stores the boxes in the hidden
``layout_data`` widget as fractions of the canvas (0..1, top-left origin).
This node turns them into a MOSS-Image layout prompt at the chosen
resolution, using the same pixel maths as ComfyUI's own MOSS-Image Layout
Prompt node: [y_min, x_min, y_max, x_max], origin at the canvas centre.
"""

import json
import math

LABELS = ("object", "character", "text")
DEFAULT_DATA = '{"v":1,"nextId":1,"boxes":[]}'


def _snap16(value):
    """Round to the nearest multiple of 16 (MOSS-Image needs multiples of 16)."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 1024.0
    return max(16, int(math.floor(value / 16.0 + 0.5)) * 16)


def _clamp01(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(value):
        return 0.0
    return min(1.0, max(0.0, value))


def _edge(fraction, size, ceil):
    """Fraction of the canvas -> centred pixel edge (enclosing the box)."""
    pixels = round(fraction * size, 9)
    pixels = math.ceil(pixels) if ceil else math.floor(pixels)
    return pixels - size // 2


def _load_boxes(layout_data):
    try:
        data = json.loads(layout_data or DEFAULT_DATA)
    except (TypeError, ValueError):
        print("[MOSS Layout Editor] layout_data is not valid JSON; using no boxes.")
        return []
    boxes = data.get("boxes") if isinstance(data, dict) else None
    return boxes if isinstance(boxes, list) else []


def build_layout(summary, boxes, width, height):
    """Return (prompt_string, item_count)."""
    items = []
    for box in boxes:
        if not isinstance(box, dict) or box.get("enabled", True) is False:
            continue

        x0, x1 = sorted((_clamp01(box.get("x0")), _clamp01(box.get("x1"))))
        y0, y1 = sorted((_clamp01(box.get("y0")), _clamp01(box.get("y1"))))
        if x1 - x0 <= 0 or y1 - y0 <= 0:
            continue

        label = box.get("label") if box.get("label") in LABELS else "object"
        caption = str(box.get("caption") or "").strip() or str(box.get("name") or "").strip()
        text = str(box.get("text") or "").strip()

        # A box with nothing to say is skipped (the editor warns about it).
        if not caption and not (label == "text" and text):
            continue

        item = {"label": label, "caption": caption}
        if label == "text":
            item["text"] = text
        item["bbox"] = [
            _edge(y0, height, False),
            _edge(x0, width, False),
            _edge(y1, height, True),
            _edge(x1, width, True),
        ]
        items.append(item)

    summary = (summary or "").strip()
    if not items:
        # Same as the core node: no boxes -> plain prompt.
        return summary, 0

    layout = {
        "summary": {"caption": summary},
        "items": items,
        "bbox_coord_space": "abs_centralized",
        "bbox_format": "yxyx",
    }
    return json.dumps(layout, ensure_ascii=False, separators=(",", ":")), len(items)


class MossLayoutEditor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 1024, "min": 256, "max": 4096, "step": 16,
                    "tooltip": "Image width. Connect the 'width' output to your Empty Latent so they always match.",
                }),
                "height": ("INT", {
                    "default": 1024, "min": 256, "max": 4096, "step": 16,
                    "tooltip": "Image height. Connect the 'height' output to your Empty Latent so they always match.",
                }),
                "summary": ("STRING", {
                    "multiline": True, "default": "", "dynamicPrompts": False,
                    "tooltip": "Description of the whole image (summary.caption).",
                }),
                "layout_data": ("STRING", {
                    "default": DEFAULT_DATA, "multiline": False,
                    "tooltip": "Box data written by the editor. Edit it with 'Open layout editor'.",
                }),
            },
        }

    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("layout_prompt", "width", "height")
    OUTPUT_TOOLTIPS = (
        "MOSS-Image layout JSON. Connect to your positive prompt text input.",
        "Width rounded to a multiple of 16.",
        "Height rounded to a multiple of 16.",
    )
    FUNCTION = "build"
    CATEGORY = "MOSS-Image"
    DESCRIPTION = "Draw, name and delete bounding boxes, then output a MOSS-Image layout prompt."

    def build(self, width, height, summary, layout_data):
        width, height = _snap16(width), _snap16(height)
        prompt, count = build_layout(summary, _load_boxes(layout_data), width, height)
        print(f"[MOSS Layout Editor] {count} box(es) at {width}x{height}")
        return (prompt, width, height)


NODE_CLASS_MAPPINGS = {"MossLayoutEditor": MossLayoutEditor}
NODE_DISPLAY_NAME_MAPPINGS = {"MossLayoutEditor": "MOSS Layout Editor"}
