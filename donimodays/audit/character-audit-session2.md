# Character Audit, Session 2: Morrow, Vesper, and Nix

An independent check of the cast after stage 6. It does not repeat the earlier
self-audit (`../character-design-audit.md`). It tests that audit's claims against the
files, the rigs, and the final video, played as continuous motion rather than as stills.

No design, rig, or render file was changed. Everything new is in this folder.

## How this audit was done

| Check | Method |
| --- | --- |
| Video as motion | Extracted all 144 frames of `stage6_personality_test_final.mp4` into two contact sheets. Measured frame-to-frame luminance change to find every cut and any pop. |
| Collisions | Opened `stage6_personality_test.blend` in Blender 5.2.3 (bpy) and tested mesh overlap on every frame for 10 part pairs, with penetration depth. |
| Contact and motion | Tracked Morrow's feet, plus 13 parts and every camera, per frame. Computed speed and acceleration to find pops and slides. |
| Framing | Projected each character and the dream fragment into the active camera on every frame, at the 1080 by 1920 resolution used for the video. |
| Rig | Loaded `cast_rigged_v05.blend` and drove each slider to its limits. Checked direction (does "smile" raise the mouth corners?), coverage, and collisions at extremes. Confirmed by eye with a cheap 360 by 300 Cycles render. |
| Readability | Downscaled video frames to Shorts feed-tile size (180 by 320) and smaller (90 by 160), in colour and greyscale. Scaled the silhouette lineup down to 24 pixels tall. |

Every number below can be reproduced with the scripts in `scripts/`. The raw
measurements are in `measure_stage6_collisions.json`, `measure_stage6_framing.json`, and
`frame_difference.txt`. One caveat: Vesper's gaze direction was estimated from the
eye centres relative to the mask centre. That is a rough forward vector, so gaze
numbers are good for comparing frames, not as exact angles.

**Labels.** **Confirmed** means measured or directly visible in a rendered frame.
**Opinion** means a judgement about how the design reads. Opinions are argued from
evidence, but a reasonable artist could disagree.

---

## Ranked findings

### 1. Morrow's worry control is inverted, so fear reads as anger. Confirmed

**What I checked.** I drove `brow_worry` on the rig from -1 to 1 and measured the
height of the inner brow end against the outer end. Then I rendered the face at -1, 0,
and +1.

**Evidence.**

| `brow_worry` | Inner end minus outer end, left brow | Reads as |
| --- | --- | --- |
| -1 (guide says "determination") | +7.2 mm (inner end raised) | Worried, pleading |
| 0 | -2.0 mm | Neutral |
| +1 (guide says "worry") | -8.0 mm (inner end lowered) | Angry |

See `images/morrow_brow_worry_check.png`. The slider description in
`stage5_rigging.py:1240` and `RIG_GUIDE.md` both say "+" raises the inner corner for
worry. It does the opposite. The direction depends on the brow bone's axis, and the
driver `{sgn}*0.4*w` (line 1253) does not account for it.

**Why it matters.** Every use of this control so far shows the wrong emotion:

- In the stage 6 close-up (frames 57 to 70), Morrow's startle reads as a grumpy scowl.
  Keyed as `brow_worry = 1` from frame 61 to 96 (`images/strip_closeup_f57-f71.png`).
- In stage 5, the "morrow worried hug" pose reads as angry, and "morrow determined"
  reads as sad and tired (`../blender/renders/stage5/sheet_rig_poses.png`).

Morrow's whole personality is a fearful character trying to look brave. Its main fear
control produces anger.

**Suggested fix.** Flip the sign of the brow rotation driver for both sides, then
re-render the stage 5 poses and stage 6. Add a direction test (see finding 9) so this
cannot come back.

### 2. The scene's turning point happens off screen. Confirmed

**What I checked.** I compared the fragment's emission keys with where the fragment
falls in each camera.

**Evidence.** The fragment's flare peaks at frame 60 (emission strength 14, light 22 W),
inside shot 3, the close-up on Morrow. In that shot the fragment is entirely outside the
frame on every frame from 57 to 70 (0 percent visible). When the cut to the medium shot
lands at frame 71, the glow has already fallen to 3.3, about 23 percent of its peak.
The fragment is then a small white blob at the left edge.

**Why it matters.** The beat table says "the fragment flares and swells. The only new
light in the scene, and it means something". The viewer never sees it. Morrow startles
at something we did not see, so the cause and effect, which is the story, is lost.
Without dialogue there is nothing else to carry it.

**Suggested fix.** Either show the flare in the insert shot (extend shot 2 to about
frame 62 and cut to Morrow's reaction after the flash), or place the fragment in the
close-up's frame so the light hits Morrow's face as it startles. The second option also
gives the ember and the face a warm light that changes on cue.

### 3. The shelter beat is full of intersections. Confirmed

The earlier audit listed "no systematic collision check" as open. I ran one on every
frame.

| Contact | Frames | Worst depth | Visible? |
| --- | --- | --- | --- |
| Morrow's crest goes through Vesper's sheltering hand | 83 to 96 (14 frames) | 3.7 mm. The surfaces cross each other, and the crest tip disappears into the palm | Yes, in the medium shot (`images/crest_through_hand_f84-f96.png`) |
| Morrow's hands sink into its own chest during the hug | 65 to 144 | 50 mm or more (my measurement stops at 50 mm), against about 5 mm of fingertip contact before the hug. Overlapping triangle pairs rise from 129 to 697 | Yes. Morrow's arms vanish from the medium and final shots. The "arms hug its chest" beat cannot be seen |
| Vesper's collar hand passes through its own mantle panels | 88 to 107 | 6.0 mm | Yes. The wrist emerges from inside the mantle |
| Fragment 3 passes through Vesper's own halo | 67 to 144 (78 frames) | n/a | Yes. The fragments stack along the halo and merge with it |
| Fragment 3 passes through Vesper's hood | 80 to 144 (45 frames) | n/a | Partly |
| Fragments 2 and 3 overlap each other | 131 of 144 frames, including rest | n/a | Reads as one lump at a distance |
| Nix sinks into the dream fragment on its "touch" | 48 to 59 | 5.0 mm | Slightly, in the insert shot |

Some contacts are clean: Vesper's hand never touches Morrow's body or face, and Nix never
touches Morrow or Vesper.

**Why it matters.** The shelter is the emotional centre of the test, and the
intersections land right there. The buried hug also removes Morrow's best piece of body
language.

**Suggested fix.**

- Raise Vesper's hand IK target about 3 cm, or lower `crest_mood` to about -0.6 from
  frame 80 so the crest curls under the hand.
- Move Morrow's hug targets forward of the chest surface, using the chest point plus the
  surface normal, not a fixed offset inside the body.
- Spread `frag_shelter` so the fragments clear the halo.
- Add a collision pass, like `scripts/measure_stage6.py`, to the stage 6 script so it
  fails loudly.

### 4. Vesper's bow reads as a mammoth, and its face disappears. Opinion, with measured support

**What I checked.** I viewed shots 4 and 6 at feed-tile size and in greyscale
(`images/phone_size_test.png`, frames 88 and 144).

**Evidence.** In the bow, the broken halo hangs on both sides of a lowered dark head.
From this camera angle it reads as a pair of tusks, and the hunched mantle reads as an
elephant or woolly mammoth. The dark graphite mask sits on a dark mantle against a dark
sky, so at phone size Vesper's eyes vanish. Vesper's brightest parts become the halo and
the pale hands, not the face.

My gaze estimate puts Vesper's eyes at least 54 degrees away from Morrow for the whole
scene. So it shelters Morrow without ever looking at it.

The earlier open item also still stands: from the front, Vesper reads as a robed figure
with a halo. In the 48 and 24 pixel silhouettes it is a generic saint or monk icon
(`images/silhouette_scale_test.png`). The No-Face collision from stage 2 is gone. The
design now drifts toward "hooded reaper with halo" instead.

**Why it matters.** Vesper is the guardian. In its signature pose it reads as a
different creature with no face. Vesper also has only `brow_raise` and lid controls, with
no brow tilt, so it cannot show concern or sorrow with its face. Its "concern" expression
on the stage 4 sheet already reads as a frown.

**Suggested fix.** Keep the halo's opening facing up when Vesper bows: counter-rotate the
`halo` bone against the spine so it stays roughly level, like a crown. Give the mask a
faint rim light, or lift its value one step, so the eyes read in the dark world. Add a
`brow_tilt` control. Aim the head at Morrow during the shelter. For the front view, the
earlier fix still applies: carry the crescent sweep into the largest front shape.

### 5. Nix reads as an orca or dolphin, and its face is too small to act. Opinion and measurement

**Evidence.** A glossy near-black body, white wedge-shaped eyes on the outer curve, and
two fins placed like a dorsal fin and a flipper. At feed size, frame 118 reads as a
leaping orca (`images/phone_size_test.png`). The "bite" is an angular notch at the lower
horn tip (`../blender/renders/stage3/sheet_nix.png`). It reads as a cut corner, not a
bite, and is gone at thumbnail size.

Nix's eyes are 15 by 19 mm on a 150 mm body. In the final wide shot, Nix spans about 15
percent of the frame width, so each eye is roughly 20 pixels on a 1080-wide frame, about
1 mm on a phone. `lid_mischief` and `lid_innocent` are mirror-image slants of the same
4 mm cut. Even on the stage 4 close-up sheet the two are hard to tell apart. Nix has no
mouth.

**Why it matters.** The brief says Nix is recognizable by silhouette and that its
contradiction is "steals the spotlight but hates sincere attention". At the sizes it
appears in, Nix has one readable trick: turning edge-on. The stage 6 video does not use
it (finding 7).

**Suggested fix.** Lighten the sheen and shift the hue toward aubergine so it reads as
lacquer, not wet skin. Make the bite an unmistakable round scallop. Move the fins off the
whale positions, for example both on the back curve. Enlarge the eyes about 1.5 times,
and make mischief and innocence differ in shape as well as slant: a flat smug line
versus round and wide.

### 6. Morrow's "two quick uneven steps" are a glide. Confirmed

**Evidence.** I tracked both feet per frame. During frames 24 to 40 both feet move
together, in parallel, and neither lifts more than 9 mm. The left foot slides 62 mm and
the right foot 38 mm while touching the ground. The script only keys the root position
and a foot tilt, so the whole body slides (`stage6_personality_test.py`, the `steps`
list).

**Why it matters.** The beat table claims "two quick uneven steps with a balance wobble".
Sliding feet are one of the most visible animation faults, even at phone size.

**Suggested fix.** Key `foot_L` and `foot_R` locations as alternating plants and lifts,
and move the root between plants. Or add foot IK targets to the rig so feet stay put
while the body moves.

### 7. Shot timing and staging undersell every beat. Confirmed, with judgements on impact

| Shot | Frames | Length | Problem found |
| --- | --- | --- | --- |
| 1 Wide | 1 to 38 | 1.58 s | Almost nothing moves for the first second: frame difference stays under 0.9 until frame 24. Vesper's head and halo run off the right edge (to 103 percent of frame width). Nix is entirely off screen. |
| 2 Insert | 39 to 56 | 0.75 s | The fragment sits alone for 6 frames before Nix enters at frame 45. The earlier audit noted this, and it is minor. |
| 3 Close-up | 57 to 70 | 0.58 s | The camera is keyed to Morrow's face, so the face stays fixed on screen (x 0.19 to 0.80 throughout) while the background whips. The camera reaches 1.3 m/s with acceleration spikes about 8 times the shot's median. The hop reads as camera shake, not as Morrow jumping. |
| 4 Medium | 71 to 110 | 1.67 s | Only 9 to 15 percent of Nix is in frame, cropped at the left edge, for all 40 frames. Morrow's legs are cut by the bottom edge. |
| 5 Nix close-up | 111 to 128 | 0.75 s | The "half turn edge-on" does not happen. Nix's on-screen width does not shrink (0.59 to 0.64 of frame). Its Z rotation changes by about 0.2 radians, while the rig guide says edge-on needs about 65 degrees. A bright cropped fragment sits in the corner. |
| 6 Wide final | 129 to 144 | 0.67 s | The payoff pose lasts two-thirds of a second. Vesper's "glance at Nix" measures 32 degrees off Nix, the same angle as during the shelter at frame 85, so no new glance registers. Morrow's "peek out" is not visible. |

**Positive, also confirmed.** No popping. Outside the intended dart and stop on Nix, and
the startle, no tracked part has an acceleration spike. Both of those are deliberate.

**Suggested fix.**

- Open on motion. For example, start on Nix's dart or on Morrow already mid-lean.
- Let the close-up hold still while Morrow hops inside it.
- Frame shot 4 to include Nix fully.
- Key a real edge-on turn of about 60 degrees for Nix.
- Hold the final pose 1.5 to 2 seconds, or design the end to loop back into the start.

### 8. The stage 6 file opens with the wrong render settings. Confirmed

`stage6_personality_test.blend` opens at 1920 by 1080 (landscape) with Eevee as the
engine and 4096 Cycles samples. The script saves the file before it sets 1080 by 1920,
Cycles, and the sample count (`stage6_personality_test.py`, "STAGE 6: render" block).
Anyone who opens the file and presses Render gets a landscape image of a vertical scene.

**Suggested fix.** Move the render setup above the `save_as_mainfile` call.

### 9. The rig tests cannot catch real faults. Confirmed

**What I checked.** The test logic at `stage5_rigging.py:1578` onward, and which
sliders it covers.

**Evidence.**

- **A test passes if any vertex moves more than 0.2 mm.** It never checks direction or
  amount. That is how finding 1 passed: `brow_worry_L = 1` "moved 7.74 mm" in the wrong
  direction. `mouth_smile` at +1 and at -1 both report the same 6.47 mm, so the test
  cannot tell a smile from a frown. (I measured them: they are correct.)
- **13 of 36 sliders are never exercised:**
  - Morrow: `brow_raise_L`, `brow_worry_R`, `lid_lower_R`, `lid_upper_L`, `lid_upper_R`.
  - Vesper: `brow_raise_R`, `grip_L`, `lid_lower_L`, `lid_upper_L`, `lid_upper_R`.
  - Nix: `fin_A_sweep`, `fin_B_flare`, `lid_rest`.

  The report headline "Every control moves the part it controls" is not supported.
- **There are no collision or combination tests.** I found:
  - Fragments collide with each other and with the halo, hood, and mantle when
    `frag_shelter = 1` is combined with `frag_spread` or `frag_fluster`.
  - The halo cuts through the hood and mantle even at rest (108 and 136 crossing
    triangle pairs).
  - Morrow's crest base crosses the shell at every setting. That is expected at a root,
    but it is untested.
- **The Nix stretch test is empty.** All Nix parts are rigid, so it measures nothing.
  This is reported honestly, but it counts towards "54 passed".
- **The meaningful tests are real:** the elbow-pole drift test, the pupil-angle test,
  and the mantle-follow test.

**Also confirmed safe.** All 77 drivers are Blender "simple expressions", so they work
with Python auto-run turned off, which is Blender's default. Slider ranges are set
correctly on every control.

**Suggested fix.** For each face slider, assert a direction with a measured sign. For
example: smile raises the corners relative to the centre, worry raises the inner brow
end, and blink brings the lid below the pupil. Test every slider on both sides. Add
pairwise overlap tests for poses at extreme slider values.

### 10. The channel documents describe a different show. Confirmed

`channel-bible.md` and `episodes-001-003.md` are entirely about Donimo, Pip, and Old
Tock. No document outside the audit names Morrow, Vesper, or Nix. They also contradict
the new cast on look and format:

- "bright colors" against the moonlit, muted palette.
- "Glow: only eyes, pips, and Pip" against the ember, the bead, and Nix's edge.
- A domino brand motif in every shot.
- The `images/` folder holds the old cast.

The channel name "donimodays" (domino days) now has no link to any character. That is a
branding decision for you, not a fix I can make.

### 11. What still blocks real Shorts production. Confirmed

| Blocker | Evidence |
| --- | --- |
| No sound at all | The video has one stream, video only. The sound identity notes exist only as text. Shorts are watched with sound on, and silent Shorts lose viewers quickly. |
| Render cost | About 1 minute per frame on this CPU container. A 30-second Short at 24 fps is 720 frames, about 12 hours. A 45-second one is about 18 hours. Eevee is untested. |
| The cast is rebuilt, not linked | Lines 1 to 1578 of `stage6_personality_test.py` are a copy of `stage5_rigging.py`, apart from the header. Each scene regenerates the cast instead of linking `cast_rigged_v05.blend`. A rig fix (like finding 1) must be made in every script and every scene rebuilt. Hand-animated episodes in Blender would not pick up rig fixes. |
| Baked secondary motion | The ember lag and mantle follow-through are baked keys. Any change to the animation needs `bake_lag` and `bake_follow_through` to be run again by script. |
| No feet or contact tools | No foot IK, no ground contact, no hand-on-object constraint. These are the causes of findings 3 and 6. |
| No story bible for the new cast | See finding 10. No episodes, no format rules, no caption style, no signature poses captured as a pose library. |

### 12. Polish items from the previous session, verified

| Item | Status |
| --- | --- |
| Insert shot shows the fragment before Nix enters | Confirmed, 6 frames (39 to 44). Minor. |
| Moon large and cropped | Confirmed. In shot 5 it is a big pale arc in the top corner, and a second crescent next to Nix that competes with it. In the wide shots it is cut by the right edge behind Vesper's head. |
| Dark horizon band | Confirmed in every wide and medium shot, at about 40 percent of frame height. Clear in greyscale. |
| Glossy finish on Morrow's face and Nix | Confirmed. Sharp window-like highlights on Morrow's face in the close-up (`images/strip_closeup_f57-f71.png`). It reads as plastic rather than glaze. |
| Subtle coral edge in wide shots | Confirmed. Nix is 15 percent of frame width in the final shot, and the edge is a hairline. |
| No sound | Confirmed (finding 11). |

---

## Design review, character by character

### Morrow: the strongest of the three

**What works (confirmed by the readability tests).**

- The seed silhouette and crest read at 24 pixels tall.
- The cavity and ember survive greyscale and feed size.
- Morrow is the lightest value in every shot it appears in, so it leads the eye.
- Its range of brows, lids, and mouth is the widest in the cast, once the worry control
  works.

**Opinions.**

- **The face patch reads as a separate glossy disc stuck on the shell**, not glaze on
  porcelain, especially in close-up. Matte it down. Let the shell's colour bleed into
  its edge so it looks fired-on.
- **The crest reads as a pull-tab, a stem, or a rabbit ear** more than a ribbon. It
  stays flat and front-facing because stage 5 flattened it for rigging. A slight twist
  or a split tip would bring back "ribbon".
- **The emotional contradiction is not visible yet.** Nothing in the design says
  "collects frightening dreams because it fears being forgotten". The cavity is empty
  except for the ember. That is a story decision. One option: the cavity holds the dream
  fragments it has collected, dimly. That uses an existing feature rather than adding an
  accessory.
- **Collision check.** "Egg with a face" is an archetype, not a specific character. The
  cavity and kintsugi seams make Morrow its own. No collision found.

### Vesper: most improved since stage 2, still the weakest on screen

**What works.**

- The broken halo is the most distinctive shape in the cast.
- The No-Face collision is resolved.
- The fragments are a good tool for showing emotion, through spacing and fluster.

**Problems.** Findings 3 and 4 cover them: the mammoth read in the bow, the face that
cannot be seen, no brow tilt, a front view that reads as a robed icon, and fragments
that pass through the halo.

**More opinions.**

- In the static front view, the broken halo reads as a letter "C" or "G". Fine as a
  logo, but worth knowing.
- The forearms are uniform straight rods. In the medium shot one reads like a pole
  through the mantle (`images/crest_through_hand_f84-f96.png`). A taper and a visible
  wrist would fix it.
- The pale mauve hands are brighter than the mask. Next to the halo, they are what you
  see first.
- **The emotional contradiction is not visible yet.** "Preserves moments but cannot
  bring back the people in them" is unrepresented. The fragments could hold a frozen
  glint of something, the way Morrow's cavity could hold dreams.

### Nix: the clearest idea, the weakest execution at small size

**What works.**

- The crescent reads in one glance at every size I tested.
- The edge-on "disappear" turn is an excellent built-in gag (stage 4 expression sheet).
- The bead is a clear attention pointer.

**Problems.** Findings 5 and 7 cover them: the orca read, eyes too small to act, a bite
that reads as a cut corner, and an edge-on gag that the video never uses. Nix is also
the darkest object on the darkest part of the frame. In greyscale at 90 by 160 it nearly
vanishes in the final shot. The coral edge is doing all the work and is a hairline at
that size.

---

## Claims from the previous audit, checked

| Claim | Verdict |
| --- | --- |
| "Every focal feature survives the thumbnail test" | Morrow's yes. Vesper's halo yes, but its face no. Nix's coral edge and bead only partly. |
| "The movement styles differ: Morrow quick and uneven, Vesper slow, Nix darting" | Vesper and Nix yes. Morrow's "uneven steps" are a glide (finding 6). |
| "No dialogue is needed. The beats read from poses, timing, and the one flash" | The flash is off screen (finding 2). The hug is hidden inside the body (finding 3). |
| "Nix half turns edge-on" | Not present (finding 7). |
| "Vesper glances at Nix with one brow up" | The brow keys exist. The head angle does not change toward Nix, and the face is unreadable at that size. |
| "Worst pupil angle 44.5 degrees" | Not re-measured. The rig test's own 47 degree result is consistent with it. |
| "54 of 54 tests pass" | True, but the tests could not detect finding 1, and 13 sliders are never exercised (finding 9). |
| "All three fit a 9:16 frame" | True in the final wide shot. Not true in the opening shot, where Vesper is cropped. |

## Images in this folder

| File | What it shows |
| --- | --- |
| `images/stage6_contact_f001-f072.png`, `images/stage6_contact_f073-f144.png` | Every frame of the final video, labelled with frame and time |
| `images/strip_closeup_f57-f71.png` | The startle close-up at full resolution: angry brows, the hand arriving |
| `images/strip_medium_f73-f110.png` | The shelter: mammoth read, crest at the hand, arms hidden |
| `images/crest_through_hand_f84-f96.png` | Close crop of the crest going into Vesper's palm |
| `images/strip_shots_f1-f144.png` | One frame from each shot |
| `images/phone_size_test.png` | Frames at feed-tile size and 90 by 160, colour and greyscale |
| `images/silhouette_scale_test.png` | The stage 3 silhouette lineup at 200, 96, 48, and 24 pixels tall |
| `images/morrow_brow_worry_check.png` | `brow_worry` at -1, 0, and +1 |

## What I recommend fixing first

1. Flip the `brow_worry` driver, and add direction tests (findings 1 and 9). This is a
   small change with a large effect.
2. Re-stage the flare so it is on screen, and fix the shelter contacts (findings 2
   and 3).
3. Plant Morrow's feet (finding 6), and re-time the shots (finding 7).
4. Fix the render settings in the saved file (finding 8). One line.
5. Design decisions for you: Vesper's bow and halo (finding 4), Nix's orca read
   (finding 5), and the channel identity (finding 10).
