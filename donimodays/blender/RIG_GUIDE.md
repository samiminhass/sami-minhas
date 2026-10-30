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
- **Arms use IK.** Move the `hand_IK_L` and `hand_IK_R` bones and the arm follows.
  These targets ride with the body, so leaning does not fold the elbows.

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
| `ember` | Offset this a little behind fast moves for the "ember lags behind" effect |
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
| `spine_1`, `spine_2`, `spine_3` | Bends the mantle. Rotate forward together for the bow |
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
| `lid_close` | 0 to 1 | Lids come down over both eyes |
| `lid_mischief` | 0 to 1 | Lids slant inward: scheming |
| `lid_innocent` | 0 to 1 | Lids slant outward: innocent |

| Bone | Use |
| --- | --- |
| `root` | Position and rotation. Rotate about 65 degrees to turn edge-on and "disappear" |
| `body` | Secondary wobble on top of the root |

## Test results

**45 of 45 tests pass.** Every control was checked to move the part it controls.
Every deforming part was measured against its rest shape in each story pose and in
one deliberate "range" pose per character. The worst edge stretch is 1.41 and the
worst compression is 0.70. The limits are 1.8 and 0.5.

## Known limits

- **Only static poses were tested.** No motion over time has been tested yet.
  Stage 6 is the first real test of animation.
- **The ember does not lag on its own.** Its lag is animated by hand on the `ember` bone.
- **Vesper's mantle has no automatic delayed follow.** Panels bend with the spine.
  A delayed follow would need offset keys or a physics pass.
- **The arm IK has no pole targets.** Elbows follow the rest bend direction. Extreme
  targets behind the body can flip the elbow.
- **The controls are sliders, not on-screen widgets.** Custom bone shapes would make
  them easier to grab in the viewport.
- **Two design changes were made for rigging.** Morrow's crest ribbon is now flat
  and facing front, so it curls cleanly instead of twisting. Nix's fins are now
  rigid paddles that swing from the base, because bending such short, thick fins
  tore them in testing.
