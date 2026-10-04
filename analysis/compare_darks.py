import sys
import numpy as np
import rawpy


def load(path):
    with rawpy.imread(path) as raw:
        return raw.raw_image_visible.astype(np.float64)


if len(sys.argv) != 3:
    print("usage: python3 analysis/compare_darks.py <dark1.dng> <dark2.dng>",
          file=sys.stderr)
    sys.exit(1)

a = load(sys.argv[1])
b = load(sys.argv[2])

# --- Noise: split one frame's noise into temporal and fixed-pattern ---
diff = a - b
temporal = diff.std() / np.sqrt(2)
total = a.std()
fixed = np.sqrt(max(total**2 - temporal**2, 0.0))

print(f"total noise (one frame):  {total:.3f} DN")
print(f"temporal noise:           {temporal:.3f} DN")
print(f"fixed-pattern noise:      {fixed:.3f} DN")

# --- Zero pixels: same location in both frames? ---
zero_a = a == 0
zero_b = b == 0
print(f"\nzero pixels  frame 1: {np.count_nonzero(zero_a)}  "
      f"frame 2: {np.count_nonzero(zero_b)}  "
      f"both: {np.count_nonzero(zero_a & zero_b)}")
for row, col in np.argwhere(zero_a | zero_b):
    print(f"  ({row:4}, {col:4})  frame1={a[row, col]:3.0f}  "
          f"frame2={b[row, col]:3.0f}")

# --- Hot pixels: same location in both frames? ---
threshold_a = a.mean() + 10 * temporal
threshold_b = b.mean() + 10 * temporal
hot_a = a > threshold_a
hot_b = b > threshold_b
print(f"\nhot threshold: mean + 10 x temporal noise (about {threshold_a:.1f} DN)")
print(f"hot pixels  frame 1: {np.count_nonzero(hot_a)}  "
      f"frame 2: {np.count_nonzero(hot_b)}  "
      f"both: {np.count_nonzero(hot_a & hot_b)}")
for row, col in np.argwhere(hot_a | hot_b)[:30]:
    print(f"  ({row:4}, {col:4})  frame1={a[row, col]:3.0f}  "
          f"frame2={b[row, col]:3.0f}")
