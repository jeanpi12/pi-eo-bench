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
