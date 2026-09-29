import rawpy
import numpy as np

with rawpy.imread("camera-data/first.dng") as raw:
    data = raw.raw_image_visible.copy()
    pattern = raw.raw_pattern
    colors = raw.color_desc
    black = raw.black_level_per_channel
    white = raw.white_level

print("shape:", data.shape, "dtype:", data.dtype)
print("pattern:\n", pattern, "\ncolors:", colors)
print("black level:", black, "white level:", white)

positions = {"top-left": (0, 0), "top-right": (0, 1),
             "bottom-left": (1, 0), "bottom-right": (1, 1)}

for name, (r, c) in positions.items():
    ch = data[r::2, c::2]
    print(f"{name:13} min={ch.min():5} max={ch.max():5} "
          f"mean={ch.mean():7.1f} std={ch.std():6.1f}")
