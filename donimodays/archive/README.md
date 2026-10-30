# Archived: the Morrow, Vesper, and Nix cast

Work on this cast is **paused** (30 October 2026). Everything needed to pick it up
again is in this repository on branch `claude/practical-keller-e3lykf`. Nothing here
needs to be deleted; the cast can be rebuilt from scratch at any time.

## What exists

| Item | Where |
| --- | --- |
| Cast build (all three characters, materials, rigs) | `blender/cast_build.py` |
| Rig build and tests (77 checks, all passing) | `blender/stage5_rigging.py`, report in `blender/renders/stage5/rig_test_report.md` |
| Rigged cast, ready to open | `blender/cast_rigged_v05.blend` |
| How to use the rigs | `blender/RIG_GUIDE.md` |
| 7-second personality test scene | `blender/stage6_personality_test.py` |
| Channel bible and first three episodes | `channel-bible.md`, `episodes-001-003.md` |
| Design audits | `character-design-audit.md`, `audit/character-audit-session2.md` |
| Before and after pictures | `blender/renders/comparison/` |
| Bolder-variant sketches | `blender/renders/sketches/bolder_variants.jpg` |
| Earlier stages (blockout, refinement, materials) | `blender/stage2_blockout.py` to `blender/stage4_materials.py` and their `.blend` files |

## Where the designs stand

- **Morrow:** porcelain seed with a teardrop hole and a floating ember, a smaller
  and lower face, a twisted crest with a split tip. Rigged and tested.
- **Vesper:** tall robed guardian with a broken gold halo, a crescent sweep of
  cloth, and no shoulder capes. Rigged and tested. An optional gold broken-ring
  slot through the robe is built in but switched off: in `cast_build.py`, change
  `P.get("slot", False)` to `True` to try it.
- **Nix:** small floating crescent with a coral edge, an attention bead, two small
  fins under its back, a bite in its lower edge, and lilac eyes. Rigged and tested.

## Open decisions (where work stopped)

1. **The redesign was not bold enough.** The creator judged the audit fixes as too
   small a change from the original cast. The sketch sheet shows two bolder options
   per character. The suggested picks were Morrow A (big face), Vesper A (taller,
   big halo), and Nix B (twice the size, bigger eyes). None were chosen.
2. **Vesper's version:** robe, or robe with the gold slot. Not chosen.
3. **Vesper as a ring (audit option C)** was built and rejected because it read as
   an object, not a character. It is kept as `vesper_option_c_ring_body.patch`.
   Apply it with `git apply` on top of commit `b96b11f` to see it again.
4. **The final stage 6 video was never re-rendered** with the latest fixes. The
   videos in `blender/renders/stage6/` are from before the audit. To render it:
   `STAGE6_SAMPLES=24 STAGE6_RANGE=1-168` with `stage6_personality_test.py` and an
   output folder. It takes about 2 to 2.5 hours on a 4-core cloud CPU, and it
   resumes if stopped.
5. **Still open from the audit:** the halo passes slightly through the collar at
   rest, Morrow's crest base sinks into the shell at full sideways lean, and Nix is
   small in wide shots.

## How to rebuild

The scripts are for Blender 5.2 LTS, run headless, for example as the `bpy` Python
module. `stage5_rigging.py OUTPUT_DIR` rebuilds the cast, runs the tests, renders the
pose stills, and saves `cast_rigged_v05.blend`. The scripts in `archive/scripts/`
made the comparison and sketch pictures. They expect a Blender Python with `bpy`
and were run from a scratch folder, so adjust their paths before reusing them.

## Advisory tool list (not adopted)

The audit session reviewed free tools that could help if work resumes. In its
suggested order: fake-bpy-module and Bone Widget, then study Blender Studio's Rain
rig, then try Wiggle Bones on a copy, then Rhubarb Lipsync NG when sound arrives,
then Flamenco and linked assets as volume grows. None are installed.
