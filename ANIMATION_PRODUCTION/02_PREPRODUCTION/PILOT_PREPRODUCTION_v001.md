# Pilot Pre-Production Package v001

**Department:** Session 02, Animation Studio
**Pilots:** P15A *Footprints* (15 s), P30A *Mirror* (30 s), P45A *Display* (45 s)
**Gate:** 2 (storyboard and animatic). Submitted for EP review and Audit Studio review.
**Story source:** `01_STORY/PILOT_CONCEPT_SLATE_v0.2.md`, approved by the EP on 2026-10-30 (Gate 1)

## Package contents

| Item | P15A Footprints | P30A Mirror | P45A Display |
|---|---|---|---|
| Shot data (cameras, staging, beats, cues) | `shots/P15A_Footprints.json` | `shots/P30A_Mirror.json` | `shots/P45A_Display.json` |
| Shot list | `shotlists/P15A_Footprints_shotlist_v001.md` | `shotlists/P30A_Mirror_shotlist_v001.md` | `shotlists/P45A_Display_shotlist_v001.md` |
| Storyboard panels and contact sheet | `../03_STORYBOARDS/P15A_Footprints/` | `../03_STORYBOARDS/P30A_Mirror/` | `../03_STORYBOARDS/P45A_Display/` |
| Animatic (9:16, temp sync sound) | `../04_ANIMATICS/P15A_Footprints_animatic_v001.mp4` | `../04_ANIMATICS/P30A_Mirror_animatic_v001.mp4` | `../04_ANIMATICS/P45A_Display_animatic_v001.mp4` |
| Shots / runtime | 5 shots, 360 f, 15.0 s | 10 shots, 720 f, 30.0 s | 10 shots, 1080 f, 45.0 s |

**How the boards were made:** this environment can't draw, so every board is a real render of a Blender blockout:
- the bakery set and the square
- stand-in characters built to the Character Bible v0.5 heights and proportions (Mila 1.15 m, 4 heads; Borek 1.55 m, 3.5 heads)
- the actual camera and lens for each shot

That makes the framing measurable rather than drawn by eye. The stand-ins are proportion proxies, not character designs.

**Rebuilding everything** from the shot data (about 3 minutes in total):
```bash
EGL_PLATFORM=surfaceless ~/.blender-venv/bin/python 05_BLENDER/scripts/kestrava_blockout.py 02_PREPRODUCTION/shots/<PILOT>.json <render_dir>
python3 05_BLENDER/scripts/make_boards.py 02_PREPRODUCTION/shots/<PILOT>.json <render_dir> ANIMATION_PRODUCTION
```

---

## 1. Story refinements made during boarding (for EP awareness)

Boarding exposed four places where the approved beats contradicted the Character Bible. Each fix stays inside the approved concept. Veto any of them and I'll restore the slate version.

| Pilot | Slate v0.2 | Boarded version | Why |
|---|---|---|---|
| Footprints | The bunny sits alone on the counter; no reason given | She dropped it scrambling up the shelves. Her frozen stare is fixed on Borek and *her bunny*. | Her greatest strength is that she never abandons what she loves. The dropped bunny is why she's frozen, which adds stakes to a 15-second gag. |
| Footprints | Top-down hook shot | Floor-level hook shot | At Bible proportions, Borek's belly hides his own clogs from above, so the clog stamp couldn't be seen. |
| Mirror | Ends on Borek holding the bunny | Adds a 12-frame button: Mila snatches it back | She can't leave the bunny with anyone for long. The snatch is in character and gives the joke a hard out. |
| Display | She leaves the bunny guarding the loaf, hides, and sees the window from outside; Borek props the bunny facing the window | She scoops the bunny up on her way out (S05B). The last image is Mila holding the bunny up to the glass so it can "see" too, while Borek, back turned, has his mustache lift. | The slate version had her walk out without her bunny. The new ending uses her signature consulting gesture instead. |

**Staging addition:** a step stool behind the counter. At 1.15 m tall, Mila can't see over the 0.95 m counter; the blockout proved it. This becomes a permanent bakery prop.

---

## 2. Character performance plan

Tempo rules from Bible v0.5:
- **Mila:** acts in 6–10 frames, short holds, 3–4-frame blinks. Total stillness means something is wrong.
- **Borek:** 8–12-frame anticipations, 1–2-second holds, 6–8-frame blinks. His mustache trails his head by 3–6 frames.

| Pilot | Key acting beats |
|---|---|
| Footprints | **Borek:** a heavy crouch (10-frame anticipation); a slow, suspicious track of the prints; a 1.5 s nose-to-nose hold with the bunny, which "wins"; his mustache rises on its own. **Mila:** frozen and silent, roll in her mouth, one 3-frame blink. |
| Mirror | The comedy is tempo contrast. Every Borek move takes him 1–2 s; Mila copies it in a fraction of a second. **Borek:** slow brow lift; puffing chest; a bread shove without looking; a baffled 8-frame blink; his mustache lifts and he presses it down. **Mila:** dead-serious braid mustache, an instant brow snap, a chest-puff wobble, a copy of his shove, a 2-frame snatch. |
| Display | **Mila:** a 10-frame hesitation before letting go of the bunny; total stillness behind the sacks; braid clutched in both fists; her face opening over 20 frames at the window. **Borek:** routine apron tie; a 2 s unreadable hold on the loaf; two knocks; careful, precise hands placing the bad loaf as if it were his best. |

**Facial rig needs** (all in the Bible's rig spec):
- Borek: independent brow masses; mustache L/R curl and bristle; slow blink.
- Mila: single-brow raise, freckle bunching on the smile, eye aim.

**Braid pose (new):** *Mirror* needs Mila's braid end held under her nose. Please add this pose to the braid deformation tests.

---

## 3. Environment and prop plan

All three pilots share one hero set, which is built and saved as `05_BLENDER/blockout/ENV_bakery_blockout_v001.blend`.

| Element | Blockout state | Final-build notes |
|---|---|---|
| Bakery interior, 6 × 5 × 3.4 m | Built | Smoke-darkened plaster and dark wood (house style: Borek stays the light shape in his own space). Timber ceiling beams. |
| Wood-fired oven, back-left wall | Built | Oven mouth is the main night practical. Needs fire and ember light, and heat shimmer only if it reads at phone size. |
| Counter, 0.95 m, with roll basket | Built | Crust and crumb materials per the Bible's starting values. |
| Tall shelves, back-right, top shelf at 2.3 m | Built | Must take a 1.15 m child crouching on top (Footprints). |
| Flour sacks | Built | A gap in the top row is a staging requirement: Mila peeks through it. |
| Shop window and display stand | Built | No centre mullion; it blocked the Display payoff. Glass with a faint reflection for S06/S07. |
| Front door and facade, whitewashed | Built | Picture sign (a loaf) above the door, per the approved world. |
| The square: cobbles, fountain, facades | Built | Stone and whitewash backgrounds keep Mila's coral away from terracotta (house style). |
| **Step stool** | Built (new) | Permanent prop. |
| Loaves: perfect and lopsided; bread peel; rolls; wildflower | Proxy | Lopsided loaf is a hero prop: readable as "made by a child" at phone size. |
| Flour footprints | Proxy decals | Final: displaced flour with sneaker tread. |
| **Borek's oldest apron, crossed-stitch patch** | Proxy | Costume variant of CHR02. Needs a Character Lab change request (filed in STATUS). |
| Bunny (PRP_Bunny) | Proxy | From the Character Lab. Needs hand/world attachment, and can stand alone on a counter. |

---

## 4. Camera plan

- **Lens kit:** 24, 28, 35, 40 and 50 mm (Blender, sensor fit on the long edge). 24 mm is reserved for wides that need the room; 50 mm for faces.
- **Vertical first:**
  - Footprints' reveal is a tilt up the full frame height.
  - Display's payoff is a frame within a frame (the shop window).
  - Mirror's two-shots stage in depth, Mila near and Borek mid, never side by side.
- **Mirrored singles in Mirror** (S03/S04) use the same lens and are scaled to head size, so the copying reads instantly.
- **Movement is rare.** One tilt (Footprints S04), one slow push (Mirror S06), one follow pan (Display S05A). Everything else is locked off, like a miniature-set camera.
- **Safe zones:** every board carries approximate platform overlay zones (red) and a face/action box (white). The hooks of all three pilots sit inside the white box.
  - The zones are a planning aid. Each platform's current guidelines get checked before export (directive section 6).

---

## 5. Sound plan

- **Animatic sound is a sync guide, not sound design.** Clops, knocks, sniffs and stings are synthesised placeholders placed at the beat times in the shot data. They're for timing review only and will never ship.
- **Final sound** (Gate 6):
  - Original Foley: clogs on stone and on wood (Borek's signature sound hook), canvas sneakers, flour, bread crust, sacking, the oven fire.
  - Original or licensed music: a small acoustic palette per tone.
  - Vocalisations only, per the dialogue policy.
  - Licensing tracked per asset.
- **Silence is scored on purpose:** Mirror S03, Display S04B.

---

## 6. Technical findings from the blockout

For the Character Lab and the Audit Studio.

1. **Borek's belly hides his feet from above.** Any top-down or high shot of his clogs needs a different angle. Not a design problem, just a staging rule.
2. **Mila can't see over a standard counter.** The bakery needs the step stool, and the same scale check applies to every future set.
3. **Borek's eyes read at medium close-up but vanish in wides** (Mirror S02, Footprints S02), even with clear proxy whites. This confirms the Bible's known risk: in wides, his brows and mustache must carry the beat.
4. **Profile two-shots of Borek are dominated by his mass** (Footprints S03/S04). Those two shots are provisional and will be re-staged once the real model's silhouette exists.
5. **Storyboard renders use the Standard view transform** so colours read clearly on boards. Final renders use AgX as the Bible specifies.

## 7. Rendering capacity

Measured in this environment (4 CPU threads, no GPU):

| Render | Time per frame |
|---|---|
| Workbench storyboard frame, 540 × 960 | about 1 s |
| Cycles, bakery blockout, 1080 × 1920, 128 samples, denoised | **242 s** (set and proxies only, plain materials) |

**This is the studio's main production risk.** At 242 s a frame:

| | Frames | Cycles CPU time |
|---|---|---|
| Footprints | 360 | about 24 h |
| Mirror | 720 | about 48 h |
| Display | 1,080 | about 73 h |
| **All three pilots** | **2,160** | **about 145 h, roughly 6 days of continuous rendering** |

That's before real characters, hair curves, subsurface skin and textures, which will raise the cost. It also assumes one render pass, with no re-renders after audit notes.

**Options to bring it down** (to be tested on the first animated shot before choosing):
1. **Fewer samples with denoising.** Try 32–48 samples and OpenImageDenoise; quality to be judged at phone size.
2. **Background plates rendered once.** 20 of the 25 shots are locked off, so render each background once and render characters over it as separate layers.
3. **Animating on twos** where the stop-motion feel suits (a Bible v0.5 option). This halves the unique frames in those shots.
4. **EEVEE.** It's slow here only because there's no GPU. On any GPU machine it would be minutes per shot, not hours.
5. **External GPU render capacity.** This is an EP decision with cost implications.

**Recommendation:** run options 1–3 on the first shot once characters are released and measure the real time per frame. Bring the EP a schedule from that measurement. Option 5 stays open if the pilots need it.

## 8. Known limitations of v001

- Stand-in characters, not designs. Expressions are indicated by brow, mustache and pose only.
- The animatic holds stills for each shot, except Footprints S04, which is the real camera tilt rendered frame by frame.
- Temp sound is synthesised.
- Safe zones are approximate.

## 9. Requested decisions

1. **EP, Gate 2:** approve the boards and animatics, or give notes. Includes the four story refinements in section 1.
2. **Audit Studio:** formal review of the three animatics, with the opening 2 seconds as the priority per Addendum 01.
