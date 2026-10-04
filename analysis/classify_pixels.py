import glob
import os
import sys

import numpy as np
import rawpy


def load(path):
    with rawpy.imread(path) as raw:
        return raw.raw_image_visible.copy()


def robust_sigma(values):
    median = np.median(values)
    mad = np.median(np.abs(values - median))
    return 1.4826 * mad


if len(sys.argv) != 3:
    print("usage: python3 analysis/classify_pixels.py <dark_folder> <master_out.npy>",
          file=sys.stderr)
    sys.exit(1)

folder = sys.argv[1]
out_path = sys.argv[2]

paths = sorted(glob.glob(os.path.join(folder, "*.dng")))
n = len(paths)
if n < 2:
    print(f"found {n} .dng files in {folder}; need at least 2", file=sys.stderr)
    sys.exit(1)

# --- Load all frames into one preallocated 3D array, keeping running totals ---
first = load(paths[0])
rows, cols = first.shape
stack = np.empty((n, rows, cols), dtype=np.uint16)
total = np.zeros((rows, cols), dtype=np.float64)
total_sq = np.zeros((rows, cols), dtype=np.float64)

for i, path in enumerate(paths):
    frame = first if i == 0 else load(path)
    stack[i] = frame
    f = frame.astype(np.float64)
    total += f
    total_sq += f * f

print(f"loaded {n} frames, stack shape {stack.shape}")

# --- Per-pixel statistics across frames ---
master = total / n
variance = (total_sq - n * master**2) / (n - 1)
pixel_std = np.sqrt(np.maximum(variance, 0.0))
lowest = stack.min(axis=0)
highest = stack.max(axis=0)
spread = highest.astype(np.int32) - lowest.astype(np.int32)

temporal = np.median(pixel_std)
print(f"\ntemporal noise per pixel: median {temporal:.3f} DN, "
      f"mean {pixel_std.mean():.3f} DN")

fixed_center = np.median(master)
fixed_sigma = robust_sigma(master)
print(f"master dark: median {fixed_center:.2f} DN, "
      f"robust spread {fixed_sigma:.3f} DN, plain std {master.std():.3f} DN")

# --- Classify ---
dead = highest == 0
hot_threshold = fixed_center + 10 * fixed_sigma
hot = master > hot_threshold
flicker_threshold = 10 * temporal
flicker = (spread > flicker_threshold) & ~dead

print(f"\ndead (0 in every frame):        {np.count_nonzero(dead)}")
print(f"hot (master > {hot_threshold:.1f} DN):     {np.count_nonzero(hot)}")
print(f"flickering (spread > {flicker_threshold:.1f} DN): {np.count_nonzero(flicker)}")
print(f"both hot and flickering:        {np.count_nonzero(hot & flicker)}")

print("\ndead pixels:")
for row, col in np.argwhere(dead):
    print(f"  ({row:4}, {col:4})")

print("\nhot pixels (first 20):")
for row, col in np.argwhere(hot)[:20]:
    print(f"  ({row:4}, {col:4})  master={master[row, col]:5.1f}  "
          f"min={lowest[row, col]:3}  max={highest[row, col]:3}")

print("\nflickering pixels, value:frames (random sample of 10):")
rng = np.random.default_rng(seed=0)
locations = np.argwhere(flicker)
picks = rng.choice(len(locations), size=10, replace=False)
for row, col in locations[picks]:
    values, counts = np.unique(stack[:, row, col], return_counts=True)
    levels = "  ".join(f"{v}:{c}" for v, c in zip(values, counts))
    print(f"  ({row:4}, {col:4})  {levels}")

per_row = np.count_nonzero(flicker, axis=1)
per_col = np.count_nonzero(flicker, axis=0)
print(f"\nflickering per row: median {np.median(per_row):.0f}, "
      f"row 0: {per_row[0]}, last row: {per_row[-1]}")
print(f"flickering per col: median {np.median(per_col):.0f}, "
      f"col 0: {per_col[0]}, last col: {per_col[-1]}")

print("rows with the most flickering pixels:")
for r in np.argsort(per_row)[-5:][::-1]:
    print(f"  row {r:4}: {per_row[r]}")
print("columns with the most flickering pixels:")
for c in np.argsort(per_col)[-5:][::-1]:
    print(f"  col {c:4}: {per_col[c]}")

np.save(out_path, master.astype(np.float32))
print(f"\nmaster dark saved to {out_path}")
