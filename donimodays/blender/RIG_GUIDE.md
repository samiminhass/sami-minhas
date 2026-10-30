# Rig Guide: Morrow, Vesper, and Nix

Open `cast_rigged_v05.blend` in Blender 5.2 or later. Each character has an armature
named `RIG_MOR`, `RIG_VES`, or `RIG_NIX`. Select it and open the **Object
Properties > Custom Properties** panel. Every control below is a slider there.
Bone controls are moved in **Pose Mode**.

The rigs are built by `stage5_rigging.py`, which also runs the tests in
`renders/stage5/rig_test_report.md`.

## How the rigs are built

- **Rigid parts follow bones.** The shell, faces, eyes, mask, halo, fragments, and
  Nix's body never deform, so they can never stretch or break.
- **Only parts that must bend deform:** Morrow's arms, fingers, and crest, plus
  Vesper's fingers and mantle. They use smooth weights and volume-preserving
  (dual quaternion) deformation.
- **Arms use IK with elbow poles.** Move the `hand_IK_L` and `hand_IK_R` bones and
  the arm follows. Move `elbow_pole_L` and `elbow_pole_R` to aim the elbows. The
  pole angles are solved so the rest pose stays exactly in place. The hand targets
  ride with the body, so leaning does not fold the elbows.
- **Viewport widgets.** Every control bone has an on-screen shape: circles for body
  controls, squares for hands, diamonds for poles, fins, and fragments, spheres for
  look targets. Bones are grouped into Controls, Face, Fingers, and a hidden
  "Deform and mechanics" collection.

## Morrow (`RIG_MOR`)

| Control | Range | What it does |
| --- | --- | --- |
| `blink` | 0 to 1 | Closes both eyes |
| `lid_upper_L`, `lid_upper_R` | 0 to 1 | Upper lid. 0 open, 1 shut. Default 0.3 |
| `lid_lower_L`, `lid_lower_R` | 0 to 1 | Lower lid rises for delight and squints |
| `brow_raise_L`, `brow_raise_R` | -1 to 1 | Brow up or down |
| `brow_worry_L`, `brow_worry_R` | -1 to 1 | Inner corner up for worry, down for determination |
| `mouth_smile` | -1 to 1 | Smile or frown, using shape keys |
| `mouth_width` | -1 to 1 | Wide or small mouth |
| `crest_mood` | -1 to 1 | 1 raised (curious), 0 relaxed, -1 curled (frightened) |
| `crest_lean` | -1 to 1 | Swings the whole crest sideways |
| `grip_L`, `grip_R` | 0 to 1 | Curls every finger joint |

| Bone | Use |
| --- | --- |
| `root` | Moves the whole character |
| `body` | Leans the seed body. The legs stay planted |
| `hand_IK_L`, `hand_IK_R` | Hand targets: reach, hug, point |
| `eye_target` | Where both pupils look |
| `ember` | Lags behind sudden moves. Run `bake_lag` after animating the body |
| `elbow_pole_L`, `elbow_pole_R` | Aim the elbows |
| `leg_L`, `leg_R`, `foot_L`, `foot_R` | Steps and balance corrections |

## Vesper (`RIG_VES`)

| Control | Range | What it does |
| --- | --- | --- |
| `blink` | 0 to 1 | Closes both eyes |
| `lid_upper_L`, `lid_upper_R` | 0 to 1 | Upper lids. Uneven defaults give its dry look |
| `lid_lower_L`, `lid_lower_R` | 0 to 1 | Lower lids |
| `brow_raise_L`, `brow_raise_R` | -1 to 1 | Brows. One up, one down reads as dry humour |
| `frag_shelter` | 0 to 1 | The three fragments swing into a partial sheltering arc |
| `frag_spread` | -1 to 1 | Fragments bunch together or spread apart |
| `frag_fluster` | 0 to 1 | Loss of composure: fragment spacing becomes uneven |
| `grip_L`, `grip_R` | 0 to 1 | Curls every finger joint |

| Bone | Use |
| --- | --- |
| `root` | Moves the whole character |
| `spine_1`, `spine_2`, `spine_3` | The bow. The mantle follows through `mantle_1` to `mantle_3` |
| `elbow_pole_L`, `elbow_pole_R` | Aim the elbows |
| `neck`, `head` | Head tilt, its main way of showing emotion |
| `hand_IK_L`, `hand_IK_R` | Hand targets. One long hand can shelter Morrow |
| `halo`, `fragment_1` to `fragment_3` | Hand-key the halo and fragments on top of the sliders |
| `eye_target` | A look target, for future eye controls |

## Nix (`RIG_NIX`)

| Control | Range | What it does |
| --- | --- | --- |
| `attention` | -230 to 70 degrees | Moves the bead around its incomplete orbit, toward whatever interests Nix |
| `fin_A_flare`, `fin_B_flare` | -1 to 1 | Fin flares out or folds in |
| `fin_A_sweep`, `fin_B_sweep` | -1 to 1 | Fin sweeps back or forward |
| `lid_close` | 0 to 1 | Lids come down over both eyes. At 1 a thin sliver stays visible |
| `lid_rest` | 0 to 0.6 | How much the lids cover when relaxed. Default 0.25 |
| `lid_mischief` | 0 to 1 | Lids slant inward: scheming |
| `lid_innocent` | 0 to 1 | Lids slant outward: innocent |

Nix's lids are live cuts. Each eye is cut by an invisible box on a `lid_L` or `lid_R`
bone, so the lid edge stays clean at any setting and never sticks out past the body.

| Bone | Use |
| --- | --- |
| `root` | Position and rotation. Rotate about 65 degrees to turn edge-on and "disappear" |
| `body` | Secondary wobble on top of the root |

## Follow-through tools

Two functions in `stage5_rigging.py` add secondary motion after the main animation
is keyed. Stage 6 uses both.

- **`bake_follow_through(rig, frames, pairs, delay)`** makes Vesper's mantle trail
  the spine by a few frames. The mantle bones copy the spine, and the tool keys a
  delay offset on top. Without a bake, the mantle follows the spine exactly.
- **`bake_lag(rig, frames, "ember", "body")`** makes Morrow's ember drift opposite
  to sudden body moves and settle when the body stops.

## Test results

**54 of 54 tests pass.**

- **Every control moves the part it controls.**
- **Deformation stays within limits.** Every deforming part was measured in each
  story pose and one deliberate "range" pose per character. The worst edge stretch
  is 1.41 and the worst compression is 0.70. The limits are 1.8 and 0.5.
- **The elbow poles leave the rest pose in place.** The largest drift is 0.07 millimetres.
- **Every control bone has a viewport widget.**
- **Morrow's pupils stay on the visible front of the eye** at extreme gaze: at most 47 degrees from straight ahead, under the 50 degree limit.
- **The mantle follow bones match the spine exactly** when no delay is baked.

## Known limits

- **The follow-through is baked, not live.** After changing the animation, run the
  bake tools again.
- **The controls were not checked by eye in the viewport.** Everything was built and
  tested headless. The widgets exist and are assigned, but their on-screen sizes may
  need adjusting when you open the file.
- **Eevee cannot run in this cloud container,** which has no graphics drivers. All
  renders use Cycles. Eevee should work normally on your own computer.
- **Two design changes were made for rigging.** Morrow's crest ribbon is now flat
  and facing front, so it curls cleanly instead of twisting. Nix's fins are now
  rigid paddles that swing from the base, because bending such short, thick fins
  tore them in testing.
- **Vesper's panels now have heather interiors.** The inside faces carry the
  heather material, so the plum shows through openings as designed.
