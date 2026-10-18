# MOSS Layout Editor (ComfyUI node)

A proper bounding-box editor for **MOSS-Image** layout prompts.

## Install

1. Put the `comfyui-moss-layout-editor` folder in `ComfyUI/custom_nodes/`
2. **Restart ComfyUI**, then **refresh the browser page**
3. Add the node: double-click the canvas and search **"MOSS Layout Editor"** (category: MOSS-Image)

No extra Python packages needed.

## Wiring

| Output | Connect to |
|---|---|
| `layout_prompt` | your positive prompt's text input (CLIP Text Encode `text`) |
| `width` | Empty Latent `width` |
| `height` | Empty Latent `height` |

Connecting `width`/`height` to the Empty Latent means **the latent always matches the layout**.
Set the size on this node (or in the editor), not on the latent.

## Using the editor

Click **Open layout editor** (or double-click the preview).

| Do this | To |
|---|---|
| Drag on empty space | draw a new box (the description field is ready to type into) |
| Click a box | select it |
| **Click the selected box again** | pick the box underneath it (keeps cycling) |
| Click a row in the **Boxes** list | select any box, even fully hidden ones |
| Drag a box | move it |
| Drag an edge or corner | resize it |
| `Delete` / trash icon | delete the box |
| Eye icon | hide the box without deleting (hidden boxes aren't sent) |
| ▲ ▼ / Bring to front / Send to back | change which box is on top |
| Arrow keys | nudge 1 px (**Shift** = 16 px) |
| `Ctrl+D` | duplicate |
| `Ctrl+Z` / `Ctrl+Y` | undo / redo |
| `Tab` | select the next box |
| `Esc` | close the editor (changes are saved as you go) |

### Box fields

- **Name** — only for you, to tell boxes apart. *Not sent to the model* (unless the description is empty, then the name is used).
- **Type** — Object, Character or Text (the three labels MOSS-Image understands).
- **Description** — what it looks like. This is the `caption` the model reads.
- **Text to draw** — Text boxes only: the exact words to render in the image.
- **Position** — type exact pixel values if you want.

## Notes

- Boxes are stored as fractions of the image, so **changing the size stretches the layout to fit** instead of breaking it.
- Rotation isn't possible: MOSS-Image boxes only have 4 edges.
- Boxes with no description (and no name) are skipped, and the editor marks them with a **!**.
- With no boxes, the output is just the "Whole image" text.
- Output format (same maths as ComfyUI's built-in MOSS-Image Layout Prompt node):

```json
{"summary":{"caption":"..."},"items":[{"label":"object","caption":"...","bbox":[y_min,x_min,y_max,x_max]}],"bbox_coord_space":"abs_centralized","bbox_format":"yxyx"}
```
