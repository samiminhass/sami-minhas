# Audit scripts

Measurement scripts used for `../character-audit-session2.md`. They only read the
`.blend` files and never save them. Run them with the bpy 5.2.3 module, for example:

```
uv venv bvenv && uv pip install --python bvenv/bin/python bpy==5.2.3 pillow numpy
bvenv/bin/python measure_stage6.py out.json ../../blender/stage6_personality_test.blend
```

| Script | Arguments | What it measures |
| --- | --- | --- |
| `measure_stage6.py` | output JSON, stage 6 blend | Per-frame mesh overlaps and penetration depth, foot contact, and on-screen position in the active camera |
| `motion_stage6.py` | output JSON, stage 6 blend | Per-frame positions of key parts and cameras, for speed and acceleration |
| `vesper_fragment_collisions.py` | stage 6 blend | Vesper's fragments against each other, the halo, hood, and mantle |
| `rig_checks.py` | rigged cast blend | Slider direction, untested sliders, and collisions at extreme settings |
| `driver_check.py` | any blend | Whether drivers need Python auto-run |
| `render_brow_worry.py` | rigged cast blend, output folder | Three small Cycles renders of Morrow's face |
| `frame_difference.py` | folder holding `frames/f###.png` | Mean luminance change between video frames, to find cuts and pops |
| `render_silhouette_turnaround.py` | rigged cast blend, output folder | Solid-black and clay renders of each character from four angles (only the silhouettes were used; the clay pass was overexposed) |
| `list_materials.py` | rigged cast blend | Each character material's roughness, coat, thin film, and emission, with the parts that use it |
