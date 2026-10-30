# Character Audit, Session 2: Morrow, Vesper, and Nix

An independent art-direction critique of the current cast, written to the creator's
critique brief. It also includes the measured technical findings from the first pass
of this session (Appendix A).

The earlier notes in `../character-design-audit.md` were written by the process that
built the characters. They are treated here as claims to verify, not as evidence.
Nothing in the project was modified. Everything new is in this folder.

## Evidence base

**Judged from existing renders.**

- `../blender/renders/stage4_palette2/`: the current colours. Studio lineup, character
  turnaround sheet, expression sheet, palette card, value check, relationship scene,
  and vertical staging.
- `../blender/renders/stage3/`: grayscale turnarounds and expressions. These show
  stage 3 geometry, before stage 5 flattened Morrow's crest and replaced Nix's fins.
- `../blender/renders/stage5/`: the control-only poses.
- `../blender/renders/stage6/stage6_personality_test_final.mp4`: the only animation.

**Tests I ran myself in this session** (Blender 5.2.3 as a Python module, plus ffmpeg
and Pillow):

1. **A new solid-black silhouette turnaround** of the current rigged cast
   (`cast_rigged_v05.blend`): front, three-quarter, side, and back, at 320 px and at
   64 px tall. File: `images/silhouette_turnaround_current.png`. Method: one flat
   black material on every part, a white background, and an orthographic camera.
2. **Phone-size and grayscale readability** of six frames from the video, at 180 by 320
   and 90 by 160 px (`images/phone_size_test.png`). I also scaled the stage 3
   silhouette lineup down to 24 px (`images/silhouette_scale_test.png`).
3. **All 144 video frames on contact sheets**, plus frame-to-frame difference
   measurements to find cuts and pops (`images/stage6_contact_*.png`).
4. **Per-frame measurements of the stage 6 scene:** collisions with penetration depth,
   foot sliding, what each camera actually shows, and the speed and acceleration of
   key parts (Appendix A).
5. **Rig slider checks** for direction, coverage, and collisions at extreme settings,
   plus three small renders of Morrow's face at three brow settings
   (`images/morrow_brow_worry_check.png`).
6. **An inventory of material settings** on every part (`scripts/list_materials.py`).

I did not run a new neutral-lighting colour render or any new expression or pose
render. Where I say "visible", I am describing one of the images named above.

---

## 1. Honest overall verdict

This is a cast with **one strong idea per character**. Only one of the three has
translated that idea into its whole body.

- **Morrow** is the most complete design. The crescent cavity through a porcelain
  seed, with a loose ember inside, is a structural idea, not an accessory. It reads
  from the front and the back at 64 px. Its weakness is that everything around the
  cavity comes from a standard mascot kit: a face disc, mitten hands, and oval shoes.
  It also loses its identity in three-quarter and side views.
- **Nix** has the clearest silhouette in the cast. It also has the best built-in
  performance idea: it turns edge-on and nearly vanishes when looked at. But the fins
  and glossy black finish pull it toward "orca" or "dolphin", and its face is too small
  to act at the sizes it appears in.
- **Vesper** has the most interesting single invention: a broken halo whose fragments
  act as an emotional instrument. But it is attached to a generic tall robed figure.
  Remove the halo and very little remains. The halo also misreads twice in the current
  renders: as tusks when Vesper bows, and as brass horn tubing when seen side-on.

The cast shares a meaningful theme of things that are incomplete or mended: cracks
repaired with gold, a broken halo, and a bitten crescent. That is worth building on.
It also repeats one visual motif too often: a crescent with a round dot. That motif
appears as Morrow's cavity and ember, as Nix and its bead, and as the notched moon in
the background.

Provisional overall design scores (Part 2):

| Character | Score |
| --- | --- |
| Morrow | about 7 |
| Nix | about 6.5 |
| Vesper | about 5.5 |

These scores describe design quality on the evidence available. They are not a
prediction of audience response.

---

## What is actually there

### Morrow

1. **Silhouette.** Visible: an upright seed or egg shape, narrower at the top, with a
   flat ribbon-like crest standing up from the crown. A crescent-shaped hole goes right
   through the torso, with a round ember floating in it. There are two hanging tube
   arms and two large oval feet.
2. **Shape groups.**
   - Large: the seed body.
   - Medium: the dark celadon face disc, the cavity, the feet, and the arms.
   - Small: the crest, the ember, the brows, the gold seams, and the fingers.
3. **Focal point.** Visible: in colour, the face disc is seen first, because it is dark
   on a light body. In silhouette, the cavity is seen first.
4. **Face.** Visible: two large white eyes with pupils, upper and lower lids, two
   separate brow bars, and a thin apricot mouth line, all on a raised glossy disc. The
   rig has controls for blink, upper and lower lids, brow raise, brow tilt, smile,
   mouth width, gaze, and crest.
5. **Colour and material.** Visible: matte off-white porcelain with gold-filled cracks
   (`MAT_mor_shell`, roughness 0.5). A dark celadon face with a strong clear coat
   (`MAT_mor_face`, coat 0.35, coat roughness 0.03), which causes sharp window-like
   highlights. Apricot crest and mouth. A glowing amber ember (emission 9). Green
   "joint" legs.
6. **Most unusual visible feature.** The through-hole cavity, which turns the
   character's middle into negative space.
7. **Personality.**
   - Visible: in the stage 4 side view, a slight forward lean, arms hanging in front of
     the body, and a raised crest.
   - Interpretation: curious, tentative, and a little fragile.

### Vesper

1. **Silhouette.** Visible: a tall narrow column, flaring slightly at the hem, with
   layered shoulder capes and sleeve shells. A small dark egg-shaped mask sits inside a
   broken gold ring, with three gold fragments continuing the ring's arc above the
   head. Thin arms with pale hands are clasped at waist height.
2. **Shape groups.**
   - Large: the robe and mantle column.
   - Medium: the halo ring, the shoulder capes, and the sleeve shells.
   - Small: the mask, the fragments, the hands, and the eyes.
3. **Focal point.** Visible: the gold halo. In the studio lineup the pale hands come
   second, and the mask comes third.
4. **Face.** Visible: a smooth dark mask with no mouth. Two small white eyes with
   heavy upper lids, plus brow bars. The rig has controls for blink, upper and lower
   lids, and brow raise, but no brow tilt. It also has head tilt and three fragment
   controls: shelter, spread, and fluster.
5. **Colour and material.**
   - Visible: an ink-slate mantle (`MAT_ves_mantle`, roughness 0.74) with heather
     interiors.
   - A graphite mask (roughness 0.72) that sits very close to the mantle's value.
   - Antique gold on the halo and fragments (`MAT_ves_brass`, roughness 0.36), with a
     lumpy surface.
   - Dove-mauve hands, brighter than the mask. No emission anywhere.
6. **Most unusual visible feature.** The broken halo, whose loose fragments rearrange
   with emotion (stage 4 "flustered" sheet).
7. **Personality.**
   - Visible: an upright stance, hands clasped low, and the mask's heavy-lidded eyes
     with lowered brows.
   - Interpretation: formal, reserved, and faintly disapproving. The intended
     "patient" and "melancholy" do not read clearly. The rest face reads as stern.

### Nix

1. **Silhouette.** Visible: a fat crescent with a lens-shaped cross-section, so it is
   a thin sliver when seen edge-on. It has two rounded paddle fins on the outer curve,
   a separate round bead floating inside the crescent's opening, and a small angular
   notch (the "bite") near one horn tip.
2. **Shape groups.**
   - Large: the crescent body.
   - Medium: the two fins and the bead.
   - Small: the eyes, the notch, and the coral inner edge.
3. **Focal point.** Visible: the bright bead, then the coral inner edge.
4. **Face.** Visible: two small white wedge eyes on the outer curve, shaped by lid
   cuts. No mouth. Each eye is 15 by 19 mm on a 150 mm body (measured). Rig controls:
   lid close, mischief slant, innocent slant, bead angle, and fin flare and sweep.
5. **Colour and material.**
   - Visible: a near-black aubergine body with an oil-slick sheen (`MAT_nix_body`:
     roughness 0.3, coat 0.3, thin film 380 nm), giving wet-looking highlights.
   - A glowing ember-rose inner edge (emission 12) and a glowing warm bead
     (emission 11).
6. **Most unusual visible feature.** The edge-on sliver view combined with the
   free-floating bead.
7. **Personality.**
   - Visible: the slanted lid cuts and the bead pointing away.
   - Interpretation: sly or smug. Shyness is visible only in the edge-on view (stage 4
     "embarrassed").

---

## 2. Scorecards

The brief's anchors apply: 5 to 6 is functional with familiar choices, 7 to 8 is
strong and deliberate. "Not tested" items are listed in section 6. Morrow and Nix have
rigs and one animation test, so their movement scores draw on both the stills and the
video.

### Morrow

| Criterion | Score | Concrete visual reason | Limitation or improvement | Confidence |
| --- | --- | --- | --- | --- |
| A. Silhouette | 7.5 | Front and back, the crescent hole with the ember dot reads at 64 px (`silhouette_turnaround_current.png`) | In three-quarter and side views the hole closes and Morrow becomes a generic egg or pear with a stem. The arms hang parallel to the body and merge with it | High |
| B. Distinctiveness | 6.5 | A body that is hollow at the centre, with feelings as a loose object visible through the hole, is an authored relationship between anatomy and emotion | Remove the cavity and what remains is a mascot kit: face disc, white mitten hands, oval shoes | Medium |
| C. Personality readability | 6 | The forward lean and raised crest read as curious and tentative | "Nervous and cute" is generic. Nothing visible says it collects frightening dreams or fears being forgotten | Medium |
| D. Charm | 7 | The gold-mended cracks show a breakable thing that has already been broken. That gives vulnerability without baby proportions | The glossy face disc makes the face read as plastic, which undercuts the "tactile porcelain" promise | Medium |
| E. Elegance and hierarchy | 6.5 | Clear light-dark order: light body, dark face, warm ember | The face disc and the cavity are similar in size and both sit at the centre, so they compete. The mitten hands and boot legs add mascot bulk | Medium |
| F. Shape and proportion | 6.5 | The seed shape, round feet, and round eyes form a consistent soft family. The crescent cavity adds one hard-edged contrast | The crest is a flat paddle that repeats no other shape. The arm tubes have one thickness from shoulder to wrist | Medium |
| G. Colour and material | 7 | The porcelain, celadon, amber, and gold family is coherent. The ember's glow stays inside the cavity and never covers the face | The face's coat (0.35, near-mirror roughness 0.03) makes the glossiest surface the one that should read as soft | High |
| H. Expression | 7.5 | Brows, two sets of lids, pupils, mouth, crest, and ember give six channels. Four distinct expressions are shown on the stage 4 sheet | The rig's worry control is inverted, so fear renders as anger (measured, Appendix A1) | High |
| I. Movement identity | 6.5 | The crest as an antenna and the ember lagging behind the body are built-in follow-through | Proposal: a "lean, then catch" walk, where crest and ember lead, the body tips, and the big feet scramble to catch it. Complications: the long tube arms bury into the shell during a hug (measured), and the video's steps are a foot slide | Medium |
| J. Story generation | 6.5 | A hole that can hold things, and cracks that imply a past | The dream-collecting and fear of being forgotten are stated in the brief, not visible in the design | Medium |

**Calculation:** 7.5 + 6.5 + 6 + 7 + 6.5 + 6.5 + 7 + 7.5 + 6.5 + 6.5 = 67.5. Divided
by 10 criteria, that is **6.75**, reported as **about 7**. No criteria were excluded.

### Vesper

| Criterion | Score | Concrete visual reason | Limitation or improvement | Confidence |
| --- | --- | --- | --- | --- |
| A. Silhouette | 6 | From the front and back, the ring around the head with the fragment arc above it is unmistakable at 64 px | The side view turns the halo edge-on into a vertical stick. Below the shoulders the outline is a generic robe. The front and back silhouettes are identical | High |
| B. Distinctiveness | 5 | A broken halo whose pieces work as an emotional instrument (fluster, shelter) is specific and authored | Remove the halo and what remains is a familiar hooded robe with a faceless mask. The body does not take part in the halo idea | High |
| C. Personality readability | 5.5 | Clasped hands and a vertical stance read as formal and composed | The face reads as stern, not patient or melancholy. "Mysterious guardian" is the default read of any tall dark robed figure | Medium |
| D. Charm | 5.5 | A guardian whose own halo is broken is a quiet, sympathetic contradiction | The small, flat, dark mask is hard to connect with. The only warmth comes from the hands | Medium |
| E. Elegance and hierarchy | 6 | One dominant ring and a restrained antique gold | Shoulder capes, sleeve shells, the diagonal panel, and the trim are four medium layers of similar size. The halo's lumpy texture and flared, bell-like ends make it read as horn tubing up close | Medium |
| F. Shape and proportion | 5.5 | Tall and narrow against Morrow's compact seed is a useful contrast | The crescent appears only in the halo. The robe is a near-straight column. The forearms are uniform rods. The hands do not read as long at rest | Medium |
| G. Colour and material | 6 | The ink, heather, and gold evening palette is coherent and needs no glow | The mask (graphite, roughness 0.72) and mantle are too close in value, so the face sinks in the dream lighting (video frames 85 to 144) | High |
| H. Expression | 5 | Lids, a brow raise, head tilt, and fragment spacing. Fragment fluster is a genuinely unusual channel | There is no mouth and no brow tilt control, so concern, sorrow, and dry amusement collapse into "stern" or "sleepy" | Medium |
| I. Movement identity | 6.5 | The orbiting fragments invite slow, formal motion with delayed, drifting follow-through | Proposal: "still body, restless halo". Vesper holds perfectly still while the fragments drift, then corrects them with one finger. Complication: in the bow the halo reads as tusks, and the fragments pass through the hood and halo (measured) | Medium |
| J. Story generation | 6 | A broken halo implies loss and a duty it could not fulfil, which suits several scenes | "Preserves moments but cannot bring back the people in them" has no visible counterpart | Medium |

**Calculation:** 6 + 5 + 5.5 + 5.5 + 6 + 5.5 + 6 + 5 + 6.5 + 6 = 57. Divided by 10
criteria, that is **5.7**, reported as **about 5.5**. No criteria were excluded.

### Nix

| Criterion | Score | Concrete visual reason | Limitation or improvement | Confidence |
| --- | --- | --- | --- | --- |
| A. Silhouette | 8 | Readable from all four views at 64 px. The edge-on sliver with a floating bead is a second, equally distinct silhouette | The two fins are placed where a dorsal fin and flipper would be, which pushes the outline toward a leaping dolphin or orca | High |
| B. Distinctiveness | 6 | A lens-shaped body that disappears edge-on, plus an attention bead orbiting outside the body, links anatomy directly to personality | "Crescent moon with a face" is a long-established image. The fins and gloss add a familiar sea-creature read | Medium |
| C. Personality readability | 6 | The slanted lid cuts and the bead pointing away read as sly | At rest it reads as "smug", not "show-off who is shy". The shy half needs the edge-on turn to be performed | Medium |
| D. Charm | 6 | Hiding by turning edge-on is a vulnerable, funny behaviour that comes from its construction | Cold wet gloss, no mouth, and tiny eyes make it hard to warm to | Medium |
| E. Elegance and hierarchy | 7 | One big shape, two medium shapes, and one bright dot. The most restrained design in the cast | The "bite" reads as a chamfered corner. The specular highlights compete with the coral edge for brightness | High |
| F. Shape and proportion | 6.5 | The crescent, round bead, and rounded fins stay in one soft-curve family | The fins are rigid paddles on the outer curve. They neither echo the crescent nor clearly serve the motion | Medium |
| G. Colour and material | 6 | Aubergine with an ember-rose edge and a warm bead is a clear accent system | The darkest object dissolves into the dark world in greyscale (`phone_size_test.png`, frame 144). The sheen reads as wet skin | High |
| H. Expression | 4.5 | Eye lid cuts, bead direction, fin pose, and body turn | The eyes are 15 by 19 mm, about 1 mm tall on a phone in a wide shot. Mischief and innocence are mirror slants of the same 4 mm cut. There is no mouth | High |
| I. Movement identity | 7.5 | A floating crescent invites the dart-and-dead-stop shown in the video, rolling, and the edge-on vanish | Proposal: the "eclipse turn". Nix turns edge-on when looked at, but the bead stays put and gives it away. Complication: the bead's orbit is incomplete, which limits where it can point | Medium |
| J. Story generation | 6.5 | The bead (what it wants) against the edge-on turn (hiding from being seen) generates repeatable situations | Only one trick is visible. A second behaviour would stop it becoming a single running joke | Medium |

**Calculation:** 8 + 6 + 6 + 6 + 7 + 6.5 + 6 + 4.5 + 7.5 + 6.5 = 64. Divided by 10
criteria, that is **6.4**, reported as **about 6.5**. No criteria were excluded.

---

## 3. Originality pressure test

These comparisons name shared traits so the differences are clear. None of them
implies copying.

### Morrow

1. **Familiar ingredients.**
   - The egg-with-face tradition (Humpty Dumpty and countless egg mascots).
   - White four-digit cartoon gloves and oversized oval shoes, the classic rubber-hose
     kit.
   - A sprout or antenna on top of the head.
   - A glowing heart-light in the chest.
   - Kintsugi gold repair as a visual metaphor.
2. **Distinctive combination.** The heart-light is not set into the chest. It floats
   loose in a hole that goes all the way through. That makes the character's feelings
   visible from behind, and it makes the character literally hollow at the centre. The
   gold-mended cracks connect that hollowness to past damage.
3. **Accessory removal.** The cavity is structural, not an accessory, so I tested the
   crest instead. Without the crest, Morrow is still identifiable from the front and
   back by the cavity. Without the cavity, Morrow is a generic egg mascot.
4. **Substitution.** The face disc could be swapped for almost any cartoon face without
   changing the personality. That marks the face as the most superficial part of the
   design. Changing the cavity would change the character.
5. **Plain lighting.** Supported: the stage 4 studio lineup and turnaround. It holds
   up, though in plain light it reads more like a vinyl toy than porcelain.
6. **Expressionless.** Partly. The silhouette's lean and arm hang suggest timidity,
   but the rest pose is close to neutral. Most of the personality lives in the face
   and crest.

**Verdict: a distinctive combination of familiar ideas.** The cavity relationship is
authored. The limbs, hands, feet, and face disc are conventional.

### Vesper

1. **Familiar ingredients.**
   - The tall hooded robe (the reaper, monk, and wizard traditions).
   - The halo of religious iconography.
   - A faceless mask with small eyes.
   - The clasped-hands posture of a butler or priest.
   - Gold ornament as a sign of age and authority.

   The stage 2 audit flagged No-Face (*Spirited Away*). The shared traits are a tall
   dark figure, a floating mask-like face, and a quiet watcher role. The differences
   now are a dark mask instead of a pale one, the halo system, visible hands with a
   formal gesture, and layered panels. In my view the specific resemblance has been
   resolved. The broader "dark robed masked spirit" tradition still applies.
2. **Distinctive combination.** The broken halo is used as an instrument. The
   fragments spread, bunch, fluster, and form a shelter. That is a specific idea.
3. **Accessory removal.** The halo is structurally central to the concept, so removing
   it is not a fair test of the concept. It is a fair test of the body, though, and the
   body underneath does not carry the idea. Nothing about the robe or hands says
   "broken" or "preserving".
4. **Substitution.** Replace the halo with floating lanterns or a ring of candles and
   the personality survives almost intact. That suggests the link between the halo and
   the body is loose. The idea sits on the character rather than inside it.
5. **Plain lighting.** Supported: the stage 4 studio lineup and turnaround. In studio
   light the mantle reads deep blue rather than black, and Vesper looks more formal and
   less mysterious.
6. **Expressionless.** Yes for formality: the upright stance and clasped hands do it.
   The bow (stage 5 and the video) reads as protective. Melancholy does not read
   without the face, and the face does not carry it either.

**Verdict: familiar but well executed,** with one individual element, the halo
system, that the rest of the body does not yet share.

### Nix

1. **Familiar ingredients.**
   - The crescent "man in the moon" with a face.
   - A floating sidekick sprite.
   - An orbiting satellite dot.
   - Slanted smug cartoon eyes.
   - From the fins and gloss: dolphin and orca traits, namely glossy black skin, white
     eye patches, and fins on the back and front curve.
2. **Distinctive combination.** Nix's shyness is built into the geometry. The lens
   cross-section makes it vanish edge-on, and its attention is an object outside the
   body that it cannot hide. Being looked at and hiding from being looked at are both
   physical.
3. **Accessory removal.** Without the bead, Nix keeps its silhouette but loses its
   attention channel, and becomes a moon-shaped fish. The bead is structurally
   important.
4. **Substitution.** The fins could be replaced with almost anything, or removed,
   without changing the personality. They are the superficial part, and they are what
   causes the sea-creature read.
5. **Plain lighting.** Supported: the stage 4 sheets. The coral edge and bead read
   clearly. The gloss is the main distraction.
6. **Expressionless.** Yes. The edge-on turn and the bead's direction carry the
   personality with a neutral face. This is the strongest result in the cast.

**Verdict: a distinctive combination of familiar ideas.** It is close to a strongly
individual design language once the fins stop pointing toward cetaceans.

---

## 4. Charm and elegance assessment

### Morrow

| Prompt | Answer |
| --- | --- |
| Detail that creates affection | The gold-filled cracks. It has been broken and someone, or it, mended it |
| Detail that creates curiosity | The ember loose inside the hole. What is it, and why can it move? |
| Overdesigned | The face. A separate raised disc carries brows, two lid sets, pupils, and a mouth, with a mirror-like coat. It competes with the cavity |
| Where restraint helps | Matte the face and blend its edge into the shell. Shrink the mitten hands about 15 percent |
| Emotional contradiction it supports | Fragile but forward-leaning: a breakable thing that keeps reaching. Visible in the lean, the cracks, and the reach poses |
| Signature silent moment | When frightened, the ember drifts to the back of the cavity and hides, visible through the hole, while the face tries to look brave |

**Imaginary scene: "The Teacup".**

1. Morrow finds a cracked teacup and turns it until the crack lines up with its own
   seam, comparing.
2. It tries to fit the cup into its cavity, beside the ember, to keep it.
3. The cup is too big. It pokes out the back, and Morrow, pinned, cannot see it.
4. Morrow walks on as if this was the plan, the cup sticking out behind it.

### Vesper

| Prompt | Answer |
| --- | --- |
| Detail that creates affection | The formally clasped hands, a tidy habit held even when nobody is watching |
| Detail that creates curiosity | Where the halo's missing pieces went, and why three still orbit |
| Overdesigned | The upper body layering: shoulder capes, sleeve shells, a diagonal panel, and trim. Also the lumpy, horn-ended halo surface |
| Where restraint helps | Merge the capes and sleeves into one crescent mantle sweep. Make the halo smooth with clean breaks, so "old" comes from the breaks, not from the texture |
| Emotional contradiction it supports | Composure against fluster: a still body while the fragments lose formation. Supported by the stage 4 "flustered" sheet and the fluster control |
| Signature silent moment | A fragment drifts out of place. Vesper, without moving its body, lifts one finger and nudges it back |

**Imaginary scene: "Composure".**

1. Vesper stands at attention while a breeze passes. The robe holds, but one fragment
   drifts.
2. Vesper checks no one is looking, and pushes the fragment back with one finger.
3. A second fragment drifts, then the third.
4. Vesper gives up and holds all three in its cupped hand, like a pocket watch,
   standing just as straight as before.

### Nix

| Prompt | Answer |
| --- | --- |
| Detail that creates affection | The bead, an attention it cannot hide |
| Detail that creates curiosity | The bite. Who bit it? |
| Overdesigned | The thin-film "oil-slick" sheen with a glossy coat (roughness 0.3, coat 0.3, film 380 nm). It turns the body into a highlight show that competes with the coral edge |
| Where restraint helps | A satin, near-matte aubergine, so the coral edge and the bead are the only bright things |
| Emotional contradiction it supports | Wants the spotlight and flees sincere attention. Visible in the stage 4 "embarrassed" edge-on view |
| Signature silent moment | Someone looks at it sincerely. Nix snaps edge-on and vanishes, but the bead keeps hovering and pointing at them |

**Imaginary scene: "Spotlight".**

1. Nix drifts into the centre of a moonbeam, its bead swinging toward Morrow to make
   sure it is seen.
2. Morrow looks up with open admiration.
3. Nix snaps edge-on to a sliver. The bead stays, still pointing at Morrow.
4. Nix turns back a few degrees, peeks with one eye, and snaps edge-on again.

---

## 5. Cast assessment

| Question | Assessment |
| --- | --- |
| Are the silhouettes sufficiently different? | Yes. A compact seed, a tall column with a ring, and a crescent stay distinct at 24 px (`silhouette_scale_test.png`). |
| Are heights and proportions complementary? | They complement each other in shape. In scale they are extreme: Vesper is about 1.71 m, Morrow about 0.60 m, and Nix's body about 0.15 m. In a 9:16 frame, Nix covers about 15 percent of the width in wide shots and becomes visually insignificant. |
| Does each have a distinct focal feature? | In function, yes: cavity, halo, and bead. In shape, no. See the next row. |
| Are too many using the same trick? | Yes, twice. In shape, a crescent with a round dot appears as Morrow's cavity and ember, as Nix and its bead, and as the notched moon in the backdrop. Morrow's front silhouette contains a small Nix. In emotion, all three show feeling through a loose floating object: ember, fragments, and bead. |
| Shared world language beyond colour? | Yes: incompleteness. Mended cracks, a broken halo, and a bitten crescent. This is the cast's best shared idea. |
| Who attracts attention first? | Morrow, the lightest value, sitting at the centre of mass with the only warm glow inside it. In close shots, Vesper's gold halo. |
| Does anyone become insignificant? | Nix, in every wide shot. Vesper's face, at any distance in the dream lighting. |
| What relationship does a group pose suggest? | The vertical staging (`stage4_palette2/staging_vertical_dream.png`) reads clearly: Vesper's hand rests on Morrow's head as guardian and child, while Nix perches above the halo to be seen. The studio lineup shows no relationship. It is three characters standing side by side. |
| Is each role distinct without dialogue? | Protagonist and guardian, yes. The trickster role reads only through the motion in the video, not in the stills. |

1. **Strongest pairing: Morrow and Vesper.** The contrasts are large: light and dark,
   compact and tall, warm glow and none. The protective hand gives a clear relationship.
2. **Weakest contrast: Vesper and Nix in value.** Both are near-black with warm
   accents, and in the dark world Nix disappears against Vesper's mantle.
3. **Motif to retain: incompleteness.** Crack, break, bite. Each character is missing
   something, in a different way.
4. **Motif to reduce: the crescent with a dot.** Keep it for Nix. Change Morrow's
   cavity profile (Morrow, Option B, in section 7) and remove the notch from the backdrop moon.
5. **Proposed group composition:** Vesper bowed into one large crescent arc over
   Morrow, so the cast's crescent motif lives at group scale. Morrow low and centre,
   facing out. Nix sitting in the gap of Vesper's broken halo, filling the missing
   piece. That suggests a relationship: Nix as the halo's unwanted, unofficial last
   fragment. This is a proposal, not something the current design communicates.

---

## 6. Missing evidence and tests

| # | Test | Status | Evidence, or what to create |
| --- | --- | --- | --- |
| 1 | Solid-black silhouette | **Supported** | Stage 3 silhouette sheets, plus my new turnaround of the current rigs (`images/silhouette_turnaround_current.png`) |
| 2 | Grayscale readability | **Supported** | `stage4_palette2/check_value_from_color.png` and my 90 by 160 greyscale frames (`images/phone_size_test.png`). Vesper's face and Nix in the dream world fail |
| 3 | Small thumbnail readability | **Supported** | Silhouettes at 24 and 64 px, and frames at feed-tile size, all tested by me |
| 4 | Neutral studio lighting | **Supported** | The stage 4 studio lineup and turnaround in current colours |
| 5 | Front, side, back, three-quarter | **Partially supported** | Silhouettes of the current geometry in all four views (my render). Lit turnarounds exist only for the stage 3 grey geometry and the stage 4 front and three-quarter views. **Create:** a lit four-view colour turnaround of `cast_rigged_v05.blend` in studio light. Question it answers: do Morrow's flattened crest and Nix's new fins hold up from the side and back in colour? |
| 6 | Five contrasting expressions | **Partially supported** | Morrow 4, Vesper 3, Nix 3 (stage 4 sheet), plus the stage 5 poses. Morrow's "worried" and "determined" rig poses show the wrong emotions (Appendix A1). **Create:** after fixing the brow control, five rig-driven face close-ups per character: joy, fear, anger, sadness, and embarrassment. Question: can each face carry five distinct emotions, and especially, can Vesper show sorrow without a mouth or brow tilt? |
| 7 | Extreme body poses | **Partially supported** | The stage 5 "range" poses (one per character). **Create:** a squash, a full stretch, a deep crouch, and a fast twist for each. Question: where do the arms, crest, halo, and fins collide or break the silhouette? |
| 8 | Short silent performance | **Partially supported** | One 6-second test. Reviewed frame by frame and measured (Appendix A). It shows the beats only partly read: the flare is off screen, and the hug is hidden inside the body. **Create:** three 4-second single-character acting tests, the scenes in section 4. Question: does each character's signature moment read with no cuts and no glow change? |
| 9 | Recognition without environment | **Supported** | The studio renders and silhouettes |
| 10 | Material readability without bloom | **Supported** | I checked both `cast_rigged_v05.blend` and `stage6_personality_test.blend`: neither has a compositor (so no glare or bloom pass), and Cycles adds none by itself. The ember, bead, and edge are plain emission. Morrow's ember does not cover the face |

---

## 7. Three redesign options per character

### Morrow

**Option A: Refinement.** Low effort.

- **Exact change.** Lower `MAT_mor_face` coat from 0.35 to about 0.05 and coat
  roughness from 0.03 to about 0.3. Feather the face disc's edge into the shell with a
  small bevel. Taper the arms from shoulder to wrist, about 25 percent thinner at the
  wrist. Shrink the hands about 15 percent.
- **Why it helps.** The face stops reading as a stuck-on plastic plate. The cavity
  regains first place. The limbs stop reading as a mascot kit.
- **What must stay unchanged.** The cavity, the ember, the gold seams, the seed
  silhouette, and the face layout.
- **Tradeoff or risk.** A matte dark face loses some sparkle in close-ups. Compensate
  with a soft rim light, not gloss.

**Option B: Stronger design.** Medium effort.

- **Exact change.** Re-shape the cavity from a symmetric crescent into a teardrop or
  keyhole hole that is clearly not a moon. That removes the "small Nix inside Morrow"
  echo. Lower the face disc about 10 percent and make it smaller, so the face and the
  cavity become one vertical reading line (face, then the hole beneath it) instead of
  two centred targets. Rebuild the crest as a slightly twisted ribbon with a split tip.
- **Why it helps.** It gives Morrow a motif of its own. It fixes the face-and-cavity
  competition that the stage 2 audit already named. It restores "ribbon" over "pull
  tab".
- **What must stay unchanged.** The through-hole idea, the loose ember, the porcelain,
  and the cracks.
- **Tradeoff or risk.** It changes the brand image that the stage 4 renders establish.
  The crest rig would need its twist re-tested.

**Option C: Bold reinterpretation.** High effort.

- **Exact change.** Drop the face disc entirely. Paint the face directly on the
  porcelain as celadon glaze, with no raised plate. Let the cavity rim become the
  mouth area, so Morrow's emotional face and its hollow are one feature.
- **Why it helps.** It removes the most generic part of the design and fuses face and
  hollow. The character's feelings then live in one place.
- **What must stay unchanged.** The seed silhouette, the ember, the cracks, and the
  crest.
- **Tradeoff or risk.** It loses the strong dark-on-light face frame that helps
  readability. It needs a new facial rig approach, such as texture-driven or
  displacement-driven features.

### Vesper

**Option A: Refinement.** Low effort.

- **Exact change.** Calm the halo's mottled surface. Cut the halo's flared, bell-like
  ends back to clean fractures. Lift `MAT_ves_mask` one value step lighter than the
  mantle, or add a cool rim light that only the mask receives. Separate fragments 2 and
  3, which overlap at rest.
- **Why it helps.** It removes the "brass horn" read and makes the face findable in the
  dark world.
- **What must stay unchanged.** The silhouette, palette, halo concept, and clasped
  hands.
- **Tradeoff or risk.** A lighter mask moves back toward the No-Face recipe flagged in
  stage 2. Keep it clearly darker than the hands.

**Option B: Stronger design.** Medium effort.

- **Exact change.**
  - Replace the shoulder capes, sleeve shells, and diagonal panel with one large
    crescent mantle sweep that starts at one shoulder and curls under the opposite arm.
    That puts the halo's broken-ring shape into the body.
  - Taper the forearms and lengthen the hands so they visibly reach past the hem.
  - Counter-rotate the halo during bows so its opening stays upward, like a crown,
    instead of hanging into tusks.
  - Add a brow tilt control and a subtle lower-mask crease that can carry a mouth-less
    frown.
- **Why it helps.** The body finally shares the halo's broken-circle language. Removing
  the halo would no longer leave a generic robe. The bow stops misreading.
- **What must stay unchanged.** The tall proportion, the halo and fragments system, the
  colour family, and the formality.
- **Tradeoff or risk.** It means re-rigging the mantle and re-testing its
  follow-through. It is a sizeable modelling change.

**Option C: Bold reinterpretation.** High effort.

- **Exact change.** Make the halo the body. Vesper's robe becomes a tall broken ring
  standing on edge, the same gap as the halo, with the mask and hands inside the
  ring's opening. The fragments are the missing pieces of Vesper itself.
- **Why it helps.** It fully fuses "guardian" with "broken". Vesper could shelter
  Morrow by literally closing its ring around it. The accessory-removal test would be
  passed structurally.
- **What must stay unchanged.** The mask, the formality, the fragments as emotion, and
  the antique gold.
- **Tradeoff or risk.** It loses the human-like robed figure that makes Vesper read as
  a guardian at a glance. It is a full rebuild and re-rig, and it risks becoming an
  abstract object rather than a character.

### Nix

**Option A: Refinement.** Low effort.

- **Exact change.** Set `MAT_nix_body` and `MAT_nix_fin` thin film to 0, coat to about
  0.05, and roughness to about 0.5 for a satin finish. Recut the bite as a clean,
  round, scalloped arc, about 1.5 times larger.
- **Why it helps.** It stops the "wet sea creature" read. The coral edge and the bead
  become the only bright features. The bite reads as a bite.
- **What must stay unchanged.** The silhouette, fins, eyes, and colours.
- **Tradeoff or risk.** It loses some "performer catching stage light" sparkle. That
  can come back as a brief rim highlight in performance shots.

**Option B: Stronger design.** Medium effort.

- **Exact change.**
  - Move both fins onto the outer back curve as a pair of small swept fins, or replace
    them with two short tufts that follow the crescent's curve. Either option removes
    the dorsal-plus-flipper layout.
  - Enlarge the eyes about 1.5 times.
  - Give mischief and innocence different eye shapes, not mirrored slants: a flat
    half-lidded line for smug, round and wide for innocent.
- **Why it helps.** It removes the orca or dolphin read and makes the face actable at
  wide-shot size.
- **What must stay unchanged.** The crescent, the lens cross-section, the edge-on
  vanish, the bead, and the coral edge.
- **Tradeoff or risk.** Bigger eyes push toward "cute". Keep them narrow to preserve
  the slyness.

**Option C: Bold reinterpretation.** Medium to high effort.

- **Exact change.** Remove the fins entirely. Let Nix propel itself by rolling and
  tumbling along its curve, like a coin. Make the bead its only appendage, held on a
  short, visible tether arc, so it can be pulled, hidden behind the body, or let slip.
- **Why it helps.** It makes the silhouette pure crescent, gives it a distinctive
  locomotion (rolling, flipping, spinning edge-on), and makes the attention bead even
  more central.
- **What must stay unchanged.** The edge-on hiding, the bead as attention, and the
  colour accents.
- **Tradeoff or risk.** Without fins it has no secondary motion for drag or hover, and
  steering reads less clearly. It also strengthens the plain "moon icon" ancestry.

---

## 8. Prioritized Blender action plan

These tasks are based on the objects, materials, and rig controls that exist in
`cast_rigged_v05.blend` and `stage6_personality_test.blend`. Nothing has been applied.
The order is by impact per effort.

### Rigging and controls

1. **Flip Morrow's brow tilt.** In `stage5_rigging.py`, `rig_morrow`, invert the sign on
   the `brow_{k}` rotation driver (`f"{sgn}*0.4*w"`, line 1253). Then `brow_worry = +1`
   raises the inner ends, as the slider label says. Verify with
   `scripts/rig_checks.py`: at +1, the inner end should be higher than the outer end.
2. **Add direction tests to the rig test suite.** Each face slider gets a measured sign
   (corner height for smile, inner-minus-outer height for worry, lid below pupil for
   blink). Test every slider on both sides, closing the 13 untested ones.
3. **Add a `brow_tilt_L/R` control to Vesper,** mirroring Morrow's. Optionally add a
   jaw-line crease shape key on `VES_mask`.
4. **Add foot IK targets to Morrow** so `MOR_foot_L` and `MOR_foot_R` can stay planted
   while `root` moves. That fixes the glide.
5. **Halo counter-rotation for Vesper.** Add a "Copy Rotation, inverted, influence about
   0.6" constraint, or a driver, from `spine_3` and `neck` to the `halo` bone, so the
   ring stays near upright during bows.

### Geometry and proportions

1. **Morrow.**
   - Taper `MOR_arm_L` and `MOR_arm_R` toward the wrist.
   - Scale the `MOR_hand_*` parts by about 0.85.
   - Reshape the cavity cutter so the hole is a teardrop rather than a crescent
     (Option B, needs your approval).
   - Move the hug IK targets forward of the chest surface, so the arms stay visible
     around the shell instead of inside it.
2. **Vesper.**
   - Rebuild the halo's two end caps, `VES_halo_break_1` and `VES_halo_break_2`, at
     the ring's own tube radius (0.024 instead of 0.03) and without jitter (now 0.3), as
     clean fractures. These caps make the flared, bell-like ends. The ring itself is
     already a smooth tube.
   - Separate `VES_fragment_2` and `VES_fragment_3` at rest. They overlap in 131 of 144
     frames.
   - Taper `VES_forearm_L` and `VES_forearm_R`, and give each a visible wrist.
   - (Option B) Merge `VES_panel_frontL_med`, `VES_panel_right_med`, and the sleeve
     shells (`VES_sleeve_L`, `VES_sleeve_R`) into a single sweep with
     `VES_mantle_crescent`.
3. **Nix.**
   - Recut the bite on `NIX_body` as a round scallop.
   - Reposition `NIX_fin_A` and `NIX_fin_B` off the dorsal and flipper positions
     (Option B).
   - Scale `NIX_eye_L` and `NIX_eye_R` (and their lid cutters) by about 1.5.

### Face and expression

1. Re-render Morrow's worried and determined poses after the brow fix, and check they
   read as intended at 180 by 320 px.
2. Build five-expression sheets per character (section 6, test 6) using rig controls
   only.
3. For Nix, change the `lid_mischief` cut to a flat, lowered lid line rather than a
   mirrored slant, so it differs in shape from `lid_innocent`.

### Materials

1. `MAT_mor_face`: coat 0.35 to about 0.05, coat roughness 0.03 to about 0.3.
2. `MAT_nix_body` and `MAT_nix_fin`: thin film 380 to 0, coat 0.3 to about 0.05,
   roughness 0.3 to about 0.5.
3. `MAT_ves_mask`: raise the base value one step above `MAT_ves_mantle`, or keep it and
   add a mask-only rim light (light linking).
4. `MAT_ves_brass`: lower the contrast of its noise-driven colour and roughness
   mottling (the Noise Texture through two Map Range nodes). The halo then reads as
   smooth old gold, not crusted. The material has no bump node, so the crusted look in
   close-ups comes from this mottling.

### Posing and animation (stage 6)

1. Put the fragment's flare on screen. Extend the insert shot to about frame 62, or
   frame the fragment inside the close-up.
2. Fix the shelter contacts:
   - Raise Vesper's `hand_IK` target about 3 cm, or curl the crest under the hand from
     frame 80.
   - Bring Morrow's hug hands out of the shell.
   - Keep the fragments out of the halo and hood.
3. Replace the root-slide steps with alternating foot plants (after the foot IK task
   above).
4. Hold the close-up camera still during the hop. Give Nix a real edge-on turn of about
   60 degrees. Hold the final pose 1.5 to 2 seconds.

### Lighting and presentation

1. **Remove the bite notch from the backdrop moon** (`DRM_moon`) and shrink it, so it
   stops duplicating Nix. Keep it out of the close-up frames.
2. **Fill the dark horizon band** with a curved backdrop or distant terrain.
3. **Give Nix a soft separation light** in the dream world, or lift the dream ground's
   value near the horizon, so Nix stops dissolving in greyscale.
4. **Save stage 6 with its real render settings** (1080 by 1920, Cycles) before
   `save_as_mainfile`. The file currently opens at 1920 by 1080 with Eevee.
5. **Render the missing tests** in section 6: a lit four-view colour turnaround, five
   expressions each, extreme poses, and three single-character acting tests.

---

## Closing

**Three design decisions worth preserving.**

1. Morrow's through-hole cavity with a loose ember: feelings that can be seen from
   behind.
2. Vesper's broken halo as an emotional instrument: spacing, fluster, and shelter.
3. Nix's lens-shaped body that vanishes edge-on, with an attention bead it cannot hide.

**Three weaknesses that matter most.**

1. Vesper's body does not share its idea. Without the halo it is a generic robe, and
   in the bow the halo misreads as tusks while the face disappears.
2. Expression systems that fail at real sizes or in the wrong direction: Morrow's
   inverted worry control, Nix's 1 mm eyes, and Vesper's lack of brow tilt and mouth.
3. The repeated crescent-with-a-dot motif and the floating-object emotion trick, which
   make the cast's focal features rhyme too closely.

**The single highest-impact change to make first.** Flip Morrow's worry control and
re-render its fear beats. It is a one-line change. It fixes the protagonist's central
emotion, fear disguised as bravery, in every pose and shot that already uses it. Right
now that emotion reads as anger.

---

## Appendix A: measured technical findings

These are the findings from the first pass of this session, unchanged in substance. They are ranked by how much they block production.

### How the measurements were made

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



### A1. Morrow's worry control is inverted, so fear reads as anger. Confirmed

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
re-render the stage 5 poses and stage 6. Add a direction test (see Appendix A9) so this
cannot come back.

### A2. The scene's turning point happens off screen. Confirmed

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

### A3. The shelter beat is full of intersections. Confirmed

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

### A4. Vesper's bow reads as a mammoth, and its face disappears. Opinion, with measured support

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

### A5. Nix reads as an orca or dolphin, and its face is too small to act. Opinion and measurement

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
it (Appendix A7).

**Suggested fix.** Lighten the sheen and shift the hue toward aubergine so it reads as
lacquer, not wet skin. Make the bite an unmistakable round scallop. Move the fins off the
whale positions, for example both on the back curve. Enlarge the eyes about 1.5 times,
and make mischief and innocence differ in shape as well as slant: a flat smug line
versus round and wide.

### A6. Morrow's "two quick uneven steps" are a glide. Confirmed

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

### A7. Shot timing and staging undersell every beat. Confirmed, with judgements on impact

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

### A8. The stage 6 file opens with the wrong render settings. Confirmed

`stage6_personality_test.blend` opens at 1920 by 1080 (landscape) with Eevee as the
engine and 4096 Cycles samples. The script saves the file before it sets 1080 by 1920,
Cycles, and the sample count (`stage6_personality_test.py`, "STAGE 6: render" block).
Anyone who opens the file and presses Render gets a landscape image of a vertical scene.

**Suggested fix.** Move the render setup above the `save_as_mainfile` call.

### A9. The rig tests cannot catch real faults. Confirmed

**What I checked.** The test logic at `stage5_rigging.py:1578` onward, and which
sliders it covers.

**Evidence.**

- **A test passes if any vertex moves more than 0.2 mm.** It never checks direction or
  amount. That is how A1 passed: `brow_worry_L = 1` "moved 7.74 mm" in the wrong
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

### A10. The channel documents describe a different show. Confirmed

`channel-bible.md` and `episodes-001-003.md` are entirely about Donimo, Pip, and Old
Tock. No document outside the audit names Morrow, Vesper, or Nix. They also contradict
the new cast on look and format:

- "bright colors" against the moonlit, muted palette.
- "Glow: only eyes, pips, and Pip" against the ember, the bead, and Nix's edge.
- A domino brand motif in every shot.
- The `images/` folder holds the old cast.

The channel name "donimodays" (domino days) now has no link to any character. That is a
branding decision for you, not a fix I can make.

### A11. What still blocks real Shorts production. Confirmed

| Blocker | Evidence |
| --- | --- |
| No sound at all | The video has one stream, video only. The sound identity notes exist only as text. Shorts are watched with sound on, and silent Shorts lose viewers quickly. |
| Render cost | About 1 minute per frame on this CPU container. A 30-second Short at 24 fps is 720 frames, about 12 hours. A 45-second one is about 18 hours. Eevee is untested. |
| The cast is rebuilt, not linked | Lines 1 to 1578 of `stage6_personality_test.py` are a copy of `stage5_rigging.py`, apart from the header. Each scene regenerates the cast instead of linking `cast_rigged_v05.blend`. A rig fix (like A1) must be made in every script and every scene rebuilt. Hand-animated episodes in Blender would not pick up rig fixes. |
| Baked secondary motion | The ember lag and mantle follow-through are baked keys. Any change to the animation needs `bake_lag` and `bake_follow_through` to be run again by script. |
| No feet or contact tools | No foot IK, no ground contact, no hand-on-object constraint. These are the causes of A3 and A6. |
| No story bible for the new cast | See A10. No episodes, no format rules, no caption style, no signature poses captured as a pose library. |

### A12. Polish items from the previous session, verified

| Item | Status |
| --- | --- |
| Insert shot shows the fragment before Nix enters | Confirmed, 6 frames (39 to 44). Minor. |
| Moon large and cropped | Confirmed. In shot 5 it is a big pale arc in the top corner, and a second crescent next to Nix that competes with it. In the wide shots it is cut by the right edge behind Vesper's head. |
| Dark horizon band | Confirmed in every wide and medium shot, at about 40 percent of frame height. Clear in greyscale. |
| Glossy finish on Morrow's face and Nix | Confirmed. Sharp window-like highlights on Morrow's face in the close-up (`images/strip_closeup_f57-f71.png`). It reads as plastic rather than glaze. |
| Subtle coral edge in wide shots | Confirmed. Nix is 15 percent of frame width in the final shot, and the edge is a hairline. |
| No sound | Confirmed (Appendix A11). |

---

---

## Appendix B: claims from the previous audit, checked

| Claim | Verdict |
| --- | --- |
| "Every focal feature survives the thumbnail test" | Morrow's yes. Vesper's halo yes, but its face no. Nix's coral edge and bead only partly. |
| "The movement styles differ: Morrow quick and uneven, Vesper slow, Nix darting" | Vesper and Nix yes. Morrow's "uneven steps" are a glide (Appendix A6). |
| "No dialogue is needed. The beats read from poses, timing, and the one flash" | The flash is off screen (Appendix A2). The hug is hidden inside the body (Appendix A3). |
| "Nix half turns edge-on" | Not present (Appendix A7). |
| "Vesper glances at Nix with one brow up" | The brow keys exist. The head angle does not change toward Nix, and the face is unreadable at that size. |
| "Worst pupil angle 44.5 degrees" | Not re-measured. The rig test's own 47 degree result is consistent with it. |
| "54 of 54 tests pass" | True, but the tests could not detect A1, and 13 sliders are never exercised (Appendix A9). |
| "All three fit a 9:16 frame" | True in the final wide shot. Not true in the opening shot, where Vesper is cropped. |

## Appendix C: images in this folder

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
| `images/silhouette_turnaround_current.png` | Solid-black front, three-quarter, side, and back views of the current rigged cast, plus the same at 64 px |
