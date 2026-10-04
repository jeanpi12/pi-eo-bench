# Lab Notebook

## Setup
- Raspberry Pi 4 Model B (8 GB), Arducam OV5647, Raspberry Pi OS (trixie)
- libcamera v0.7.2+rpt20260817
- Mode 2592x1944, 10-bit raw, GBRG Bayer pattern
- Dark frames: lens covered (describe how), shutter 10000 us, gain 1.0

## 2026-09-29 — First dark frame (dark.dng)
- Mean 14.7-14.9 DN in all four color planes, std 1.3 DN
- Nominal black level in tuning file: 16 DN; measured ~14.8 DN
- 6 zero pixels, max 36-42 DN, 0 saturated

## 2026-10-03 — Second dark frame (dark2.dng), compared to first
- Mean and std unchanged: baseline is repeatable over 4 days
- Noise split (compare_darks.py):
  - total 1.306 DN, temporal 0.656 DN, fixed-pattern 1.130 DN
  - fixed-pattern noise dominates, so dark subtraction removes most of it
- Zero pixels: 9 locations zero in at least one frame; 2 zero in both:
  (131, 1492) and (1935, 893), candidate dead pixels
- Other 7 zero pixels read 5-30 DN in the other frame (flickering)
- Observation: 5 of 9 zero locations in columns >= 2400, 2 in rows
  1935-1936 (edges). Possibly chance; watch with more data.

## Method issue: hot-pixel threshold
- Threshold of mean + 10 x temporal noise (21.4 DN) flagged 1011 and
  1186 pixels, only 129 in both frames
- Most flagged pixels jump ~7 DN between frames rather than staying high
- Cause: threshold assumed Gaussian noise; actual distribution is
  heavy-tailed (most pixels quiet, a minority jump)
- Hypothesis: random telegraph noise (RTN). Needs more frames to confirm.

## Design implication
- Single dark frame adds its own temporal noise: ~0.93 DN after correction
- Averaging N frames into a master dark: ~0.68 DN with N = 16
- Plan: master dark from at least 16 frames

## 2026-10-03 — Burst capture
- 20 dark frames, dark_01 to dark_20, same settings as above
- Stored in camera-data/darks/ (not in git)

## 2026-10-03 — 20-frame classification (classify_pixels.py)
- Master dark built from dark_01 to dark_20, saved as
  camera-data/master_dark.npy (not in git)
- Results identical on rerun (reproducible)

### Noise
- Temporal noise per pixel: median 0.553 DN, mean 0.606 DN
  (mean > median: a minority of noisy pixels pulls the mean up)
- Master dark: median 15.30 DN, robust spread 0.890 DN, plain std 1.140 DN
- Per-frame means (~14.85) below master median (15.30): distribution
  skewed low by pixels that occasionally dip far down

### Defects
- Dead (0 in all 20 frames): 0. Revises earlier candidates
  (131, 1492) and (1935, 893): not zero in every frame.
- Hot (master > median + 10 x robust spread = 24.2 DN): 14 pixels,
  master 24.6 to 42.5 DN. 13 of 14 also flicker, likely shot noise
  from their extra dark current, not RTN.
- Adjacent hot pair: (392, 1791) and (393, 1791). Matters for defect
  correction (a bad pixel's neighbor can't be used to fix it).
- Flickering (spread > 10 x temporal = 5.5 DN): 94,875 pixels (~1.9%)

### Flickering pixels
- First test sampled only row 0 (sampling bias). Fixed with a seeded
  random sample (seed 0).
- Random sample: main cluster plus scattered excursions in both
  directions; only some pixels look like two-level RTN.
  RTN hypothesis weakened; cause undetermined with 20 frames.
- Edges not special: row 0: 40, last row: 51, median 49 per row.
  Earlier edge-clustering observation not supported.
- Columns 160 (77), 1964 (75), 336 (70) about 2x expected
  (~37 per column; expected max by chance ~58).
  Hypothesis: noisy column readout circuitry.
- Row 391 (81) slightly high, next to hot pair at rows 392-393.

### Design implication
- ~2% of pixels randomly jump 5+ DN; dark subtraction can't remove this.
- A threshold set from typical noise would give false detections every
  frame. Supports a smoothing (convolution) stage before thresholding.
