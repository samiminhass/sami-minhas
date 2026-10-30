# Audit Studio Status (Session 03)

Branch: `claude/audit-studio`. Full findings: `AUDIT/AUDIT_LOG.md`.

| Audit | Submission | Version | Status | Open findings |
|---|---|---|---|---|
| AUD-001 | Character Bible (CHR-PREPROD) | v0.5 @ `455caf8` | **REVISE** (small scope) | F1 proportion specs must be fixed before blockout. F2 (bunny stitch clue) and F3 (Borek expression vocabulary) are tested at blockout. M1–M8 are minor. |

## Capability notes

- Executed here: image silhouette, grayscale, phone-size (360 × 640) and measurement tests (Python, Pillow, NumPy); HTML/SVG rendering (Chromium); video and audio inspection (FFmpeg/FFprobe).
- Blender: not installed in this session. The studio build (5.2.3 LTS, `STUDIO_DIRECTIVES/setup_blender.sh`) will be installed when the first `.blend` is submitted. Until then every mesh, rig and deformation check is untested.
- Platform analytics: no access. Audience review needs exported data from the EP.

## Waiting for

- Character Lab: a revised bible addressing F1, then the Mila and Borek primary blockouts.
- Animation Studio: no submission yet.
