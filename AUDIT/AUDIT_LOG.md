# Audit Log — Independent Creative & Technical Audit Studio (Session 03)

Newest entries at the bottom. Every finding cites an exact branch, commit, file and location. Evidence images are in `AUDIT/evidence/<audit id>/`.

---

## AUD-001 — Character Bible v0.5 (design-level review)

| Field | Value |
|---|---|
| Project ID | CHR-PREPROD |
| Department | 3D Character Design & Development Lab (Session 01) |
| Version reviewed | `CHARACTER_ASSETS/08_DOCUMENTATION/CHARACTER_BIBLE_v0.5.html` on branch `claude/dreamy-wozniak-qzx8c8`, commit `455caf8` |
| References | `CHARACTER_ASSETS/02_REFERENCE/source_images/ref_girl_braid.jpg` (Mila), `ref_baker.jpg` (Borek), both 900 × 600 px |
| Date | 2026-10-30 |
| Question asked | Are Mila and Borek ready to enter Blender blockout, or should a design problem be fixed first? |
| **Approval status** | **REVISE** (small scope). Correct the proportion specs (F1), then Mila and Borek may enter blockout. No redesign is required. F2 and F3 are tested during blockout and are not preconditions. |

### Answer to the Character Lab's question

Neither character has a design problem that justifies a redesign. Both references pass the silhouette, grayscale and phone-size tests on their main shapes. One error should be fixed before the first `.blend` exists: the head-count specs in section 8A don't match the approved references, and Borek's is clearly outside what the reference shows. Building to the current numbers would make the blockout deviate from references that EP decision 3 says must be reproduced closely.

### What was tested, and how

| Test | Status | Method |
|---|---|---|
| Black silhouette | Executed | Background-difference mask on both references (`evidence/AUD-001/image_tests.py`) → `01_silhouette_grayscale.png` |
| Grayscale / value | Executed | Luminance conversion → `01_silhouette_grayscale.png` |
| Thumbnail / phone size | Executed | Figure scaled into a 360 × 640 frame at 50 % and 85 % of frame height → `02_phone_360x640.png`, `03_face_pixels_at_phone_size.png` |
| Proportion measurement | Executed | Pixel grid on both references → `04_head_count_grid.png`. Single perspective image each, so accuracy is about ±0.3 heads |
| Staging diagram | Executed | Bible SVG rendered offline in Chromium → `05_bible_staging_diagram_render.png`; frame rect 162 × 288 = 9:16, confirmed |
| Document consistency | Executed | Full text read of v0.5, cross-checked against `EP_DECISIONS.md` |
| Front / side / back / three-quarter consistency | **Untested** | Only one view of each character exists |
| Accessory removal | **Untested** | Cannot be done on a flat image; repeat on the blockout |
| Expressionless / neutral lighting | **Untested** | Both references carry an expression and a studio lighting setup |
| Expression readability at 360 × 640 | **Untested** | No expression sheets exist |
| Mesh, topology, normals, UVs, materials, rig, deformation | **Untested** | No Blender assets exist |

What's visible versus interpreted: measurements and pixel sizes below are taken from the reference images. Statements about future readability are predictions to be confirmed on blockout renders.

### Strongest work

- **Borek's silhouette.** It's the strongest shape in the package: a wide, top-heavy mass on short legs, with the loaf as a separate circle. It reads instantly at 50 % frame height (`01`, `02`).
- **Value separation (Art Direction, "Colour and Value Separation").** The claim that Mila reads as a dark top over a warm mid-value body, and Borek as a light mass with a dark accent, is confirmed by the grayscale test. The bible also catches its own colour conflicts (coral tunic against terracotta, cream jacket against flour-white walls).
- **Production specs (section 8).** Units, orientation, naming, topology rules, rig components and deformation tests are specific and testable. Composing face expressions from components instead of eight baked poses is the right call.

### Weakest work

- The central mystery's visual clue (F2). It carries the series' story engine but isn't in the approved reference and is too small to see at phone size as currently described.

### Findings — critical (max three this round)

#### F1 — MAJOR — Head-count specs don't match the approved references

1. **Location:** Bible v0.5, §3C "Height" (Mila ~4 heads), §4C "Height" (Borek ~3.5 heads), §8A "Girl height" / "Baker height" / "Height ratio", and the proportion diagram.
2. **Evidence:** `04_head_count_grid.png`, measured on the source 900 × 600 px images.
   - **Borek:** crown at y ≈ 20 px, chin at y ≈ 150–165 px, sole at y ≈ 575 px. That's 555 px tall with a 130–145 px head, so **≈ 3.8–4.2 heads**. The spec says 3.5.
   - **Mila:** hair mass top at y ≈ 40 px, skull top at about y ≈ 70 px, chin at y ≈ 205 px, sole at y ≈ 572 px. That's **≈ 3.2 heads counting hair volume, or ≈ 3.7 skull-only**. The spec says 4.
3. **Problem:** The specs describe Borek as relatively bigger-headed than the reference and Mila as smaller-headed. In the reference it's the other way round: Mila is the proportionally bigger-headed character. At the spec heights, Borek's head is 0.44 m against Mila's 0.29 m (1.53×). Reference proportions give roughly 0.37–0.41 m against 0.31–0.36 m (≈ 1.1–1.3×).
4. **Impact:** The blockout would drift from references the EP approved for close fidelity (EP decision 3), and the 9:16 two-shot test would be run on the wrong size relationship. Fixing it after rigging is expensive.
5. **Fix:** Re-derive head counts and the head-size ratio from the references and state the method (with or without hair volume). If the Lab wants to deviate on purpose, e.g. to make Mila read younger, say so as a proposal for the EP.
6. **Acceptance:** §3C, §4C and §8A updated in a new bible version. On the first blockout, a front orthographic render with a head-unit overlay is within ±0.25 heads of the reference measurement for each character, or within ±0.25 of a deviation the EP has approved.

#### F2 — MAJOR — The bunny's crossed-stitch clue won't read at phone size

1. **Location:** Bible v0.5, §1 "Story Engine: One Central Mystery"; §2 "House Style Rules: The stitch is the motif"; §3C "Signature Object".
2. **Evidence:**
   - The approved reference bunny (`ref_girl_braid.jpg`, around x 500–600, y 240–400) shows a plain stitched face and no crossed-stitch seams. The clue is a new design element.
   - At 50 % frame height in a 360 × 640 frame, the bunny is about 50 × 90 px (`02_phone_360x640.png`). A seam stitch at the scale of the reference's stitched face would be 1–2 px.
   - In the black silhouette (`01`), the bunny merges with Mila's torso. Only the ears break the outline.
   - The bible states "the stitch is visible in every shot she's in" and that each sighting "makes a two-second hook".
3. **Problem:** The series' main hook depends on a detail that can't be resolved on the target screen at the framings the bible plans for. The other sightings (Borek's apron patch, a cottage cushion) are smaller still in frame.
4. **Impact:** Viewers can't notice the clue, so the mystery doesn't start, or the Animation Studio is forced into an insert close-up every time it appears.
5. **Fix:**
   - Design the crossed stitch as a bold mark: a thread colour that contrasts with the bunny fabric, and stitch length large enough to read.
   - Specify where on the bunny it sits, so it faces the camera in Mila's standard hold.
   - Specify the minimum framing at which the clue can be read, so the Animation Studio knows when an insert is needed.
   - Add the bunny's crossed stitch to the bible's design sheets before the bunny is modelled. This doesn't block the Mila or Borek body blockout.
6. **Acceptance:** On a blockout or look-dev render downscaled to 360 × 640, at least four of five testers identify the stitch as the same pattern as Mila's braid cord, in both:
   - a medium shot (bunny ≥ 15 % of frame height);
   - one other placement (apron patch).

#### F3 — MAJOR — Borek's expression set leans on eyes that are tiny at phone size, and his mustache shapes overlap between moods

1. **Location:** Bible v0.5, §4D "Emotional Tell", §4E "Required Expressions" (Happy, Angry, Worried, Surprised, Confused).
2. **Evidence:**
   - **Eye size:** at 50 % frame height in a 360 × 640 frame, each of Borek's eyes is about 12 × 5 px. Mila's are about 17 × 17 px, roughly 4–5× the area (`03_face_pixels_at_phone_size.png`).
   - **Expressions that depend on the eyes:** Happy ("eyes soften") and Worried ("eyes dart").
   - **Overlapping mustache shapes:** §4D says the mustache "bristles upward when he's proud or pleased". §4E Angry is "Full bristle. Mustache points straight out". Two opposite emotions share the word and nearly the same shape.
   - **Expressions told apart only by degree:** Surprised ("eyebrows shoot above the eye line") and Confused ("both eyebrows up") differ mainly in how far the brows rise.
3. **Problem:** The Lab already flags the eye-size risk and its handling (catchlight, brow lift) is reasonable. The mustache is meant to carry his acting, but its shapes aren't defined distinctly enough to do that.
4. **Impact:** In a 15 s short, one reaction has to land in about a second (bible §2). A pleased Borek that reads as angry inverts the joke.
5. **Fix:**
   - Add a mustache shape table: one distinct silhouette per expression, covering curl tightness, tip angle and symmetry. For example, pleased = curls tighten and lift; angry = straight horizontal spikes; sad = droop past the mouth line.
   - Rewrite §4D so "bristle" belongs to anger only.
   - Make Surprised and Confused differ by mustache shape as well as brow height.
6. **Acceptance:** On the facial blockout, all eight Borek expressions downscaled to 360 × 640 at medium-shot size, shown in random order, are named correctly by at least four of five testers within about one second. Happy and Angry are never confused with each other.

### Findings — minor

| # | Location | Evidence | Fix | Acceptance |
|---|---|---|---|---|
| M1 | §3A Mila "Role" | Says "entry point into **Millbrook**"; EP decision 6 approved Kestrava | Replace with Kestrava | No "Millbrook" outside the naming rationale |
| M2 | Bible footer | "Awaiting Executive Producer approval on names, world concept…", which EP decisions 4, 5 and 7 already granted | List only what is still open | Footer matches `EP_DECISIONS.md` |
| M3 | §7 Pim ↔ Borek | "delivers bread to **Baba Vela**"; the name was approved as "Vela" and "Baba" was flagged as a witch reading | Use "Vela" | No "Baba" outside the naming rationale |
| M4 | §8D Naming | Examples still use `CHR01_GIRL` / `CHR02_BAKER`; the rule says to replace them once names are approved, and they now are. Files are never overwritten, so a rename later means churn | Lock `CHR01_MILA`, `CHR02_BOREK` before the first `.blend` | First blockout files use the locked IDs |
| M5 | §3C Mouth / §3E Neutral vs reference | The reference face rests in a clear closed smile. The bible's Neutral is "guarded… brow slightly lowered" | Sculpt the rest face as true neutral and build the reference smile as a shape key, so both reads are available | Neutral and reference-smile renders side by side on the facial blockout |
| M6 | §4C Facial Hair vs black silhouette | In the front view, the curls sit inside the head/cheek outline (`01`), so the "width and mustache" signature (§2 Vertical & Mobile Readability) isn't visible in silhouette from the front | Check the three-quarter and profile silhouettes at blockout. If the curls don't break the outline in at least one standard angle, propose a small extension to the EP (reference fidelity applies) | Silhouette renders at front, three-quarter and profile |
| M7 | `CHARACTER_ASSETS/08_DOCUMENTATION/STATUS.md` | Marks Mila and Borek "Ready for Blender blockout" before this audit returned | Update to the audit outcome | Status cites AUD-001 |
| M8 | §5 Pim (proposed) | Recommended direction B ("never invents anything new") but §5A, §5B, §5C and §7 still describe an inventor whose inventions go wrong. 4.5 heads breaks the art-direction rule "1/3 to 1/4 of total body height" | Align the text once the EP chooses a direction; state the rule exception or change it | Not blocking; Pim is proposed |

### Optional

- **O1 — Two-shot staging.** In the rendered diagram (`05`), Mila near the camera ends up with a head as large as Borek's. Depth staging erases the size contrast that carries their comedy and warmth. Test at least one alternative in the blockout two-shot: Borek near, Mila far; or both on one plane with vertical offset. Also keep Mila's head off the frame edge; in the diagram, her hair touches the left border.
- **O2 — Bunny hold poses.** Since the bunny merges with the torso in silhouette, animation guidance should keep the ears above the arm line, or the bunny held out to the side, in key poses.

### Scores (design documentation only; no assets exist)

| Area | Score | Reason |
|---|---|---|
| World and story engine | 8/10 | Coherent rules, one central mystery and a well-argued silent-first policy. Held back by F2: the clue that drives the mystery isn't readable as specified. |
| Art direction | 8/10 | Specific house rules and value-separation rules, confirmed by the grayscale test. Colour conflicts self-identified. |
| Mila (design) | 8/10 | Strong dark-top silhouette, braid reads, large high-contrast eyes. Bunny lost in silhouette; proportion spec off (F1). |
| Borek (design) | 7/10 | Best silhouette in the package. Expression vocabulary underdefined for his small eyes (F3); head-count spec clearly off (F1). |
| Mobile readability planning | 7/10 | Good, testable rules, contradicted in one place by the story engine's reliance on fine stitch detail. |
| Production specifications | 8/10 | Thorough and consistent. Proportion inputs wrong; naming examples stale (M4). |
| Pim and Vela | Not scored | Proposed characters. Directions well reasoned; identity text not yet aligned (M8). |

### Recommendations for the EP (not blockers on the Character Lab)

- **F1 deviation decision.** If the Lab argues for different proportions than the references show, that's your call under decision 3.
- **M6 mustache extension.** Any extension of Borek's mustache beyond the reference needs your approval.

### Required retests on resubmission

1. F1: the revised bible §3C, §4C and §8A, plus front orthographic blockout renders with a head-unit overlay.
2. F2: the bunny stitch design sheet, then the 360 × 640 tester check.
3. F3: Borek's mustache shape table now; the eight-expression blind test at facial blockout.
4. Untested items carried forward to the blockout: turnaround consistency, accessory removal, neutral lighting, expressionless, and the 9:16 two-shot.

---

## AUD-001 R1 — Re-review of Character Bible v0.6

| Field | Value |
|---|---|
| Version reviewed | `CHARACTER_BIBLE_v0.6.html` on `claude/dreamy-wozniak-qzx8c8`, commit `474fee9` |
| Method | Full text diff against v0.5, arithmetic check of every new number, offline render of the redrawn diagram → `evidence/AUD-001/06_v0.6_staging_diagram_render.png` |
| Date | 2026-10-30 |
| **Approval status** | **PASS for entry to Blender blockout** (Mila and Borek). F1 is closed at document level. F2 and F3 design responses are accepted, and their acceptance tests run on blockout renders. |

### Finding status

| Finding | Status | Verification |
|---|---|---|
| F1 Head counts | **Closed (document)**; render retest pending | §3C, §4C and §8A now use crown-to-chin without hair, matching AUD-001. Checks: 1.15 m ÷ 3.7 = 0.31 m; 1.55 m ÷ 4 = 0.39 m; head ratio 1.25, inside the 1.1–1.3 measured range. With 4 cm of hair, Mila is 1.19 ÷ 0.35 ≈ 3.4 heads, which agrees. In the redrawn diagram, the heads measure ≈ 0.31 m and ≈ 0.39 m at its 200 px/m scale. Retest: front orthographic head-unit overlay, ±0.25 heads. |
| F2 Stitch clue | **Design accepted**; tester retest pending | Bunny 0.30 m is ≈ 26 % of Mila's height (reference ≈ 29 %, consistent). At bunny = 15 % of a 640 px frame (96 px), a 3–4 cm X is ≈ 10–13 px and a 6 mm cord ≈ 2 px. The Lab's "≈ 8 px, 1.5 px" is conservative. Readability remains a prediction until tested. |
| F3 Borek mustache | **Design accepted**; blind test pending | §4F gives eight distinct tip-angle/symmetry combinations. "Bristle" is used only for anger. Surprised (+70° V) and Confused (+45°/−30° seesaw) now differ by mustache shape. **Watch item:** Neutral (+20°) and Angry (0°, +20 % width) differ by only 20° of tip angle. The distinction rests on the straightened curls and the brows; the blind test must check this pair as well as Happy and Angry. |
| M1–M5, M7 | **Closed** | Verified in the text diff and `STATUS.md` @ `474fee9` |
| M6 | Carried to blockout | Listed in §8H |
| M8 | Closed as flagged | Exception stated in §2; Pim's text marked as direction A until the EP decides |
| O1, O2 | Adopted | Three stagings in §8A; hold guidance in §3C/§3D |

### New observations (minor, not blocking)

- **N1:** In the diagram's two-shot, Mila's hair still touches the left frame edge, and the "UI overlay (approx.)" label overlaps the frame border. This is cosmetic; the real test is the blockout two-shot.

### Retests required with the blockout submission

1. F1: head-unit overlay on front orthographic Workbench renders of both characters.
2. F2: stitch tester check on a 360 × 640 render (medium shot and apron patch). This can follow the bunny build.
3. F3: eight-expression blind test at the facial blockout, including the Neutral/Angry pair.
4. Carried forward: turnaround consistency, accessory removal, neutral lighting, expressionless, M6 silhouettes, the three O1 two-shot stagings.
