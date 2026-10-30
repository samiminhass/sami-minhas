# donimodays: Channel Bible

> **Status: paused and archived (30 October 2026).** See `archive/README.md` for where the cast stands and how to resume.

This replaces the earlier Donimo, Pip, and Old Tock cast. The current cast is
Morrow, Vesper, and Nix, built in Blender (see `blender/`). The earlier cast remains
in this file's git history.

## The big idea

**In this world, forgotten dreams become physical objects, and broken moments drift
through the air.** Every video is one small encounter with one of those objects, told
in 15 to 45 seconds, mostly without dialogue.

The channel name stays: every episode is one of Morrow's days, the days of a
small creature that collects dreams.

**Tagline:** *Every forgotten dream lands somewhere.*

## Format rules

| Setting | Value |
| --- | --- |
| Aspect ratio | 9:16 vertical, 1080 x 1920 |
| Length | 15 to 45 seconds |
| Shots per video | 4 to 8, cut on action |
| Hook | Something strange or tender in the first 2 seconds |
| Dialogue | Little or none. Sound, posture, and faces carry the story |
| Ending | A held reaction pose of at least 1.5 seconds |
| Look | Surreal storybook meets tactile cinematic 3D. Neutral studio first, the dream world for story |

## The cast

Full design notes, rig controls, and test results are in `blender/RIG_GUIDE.md`,
`character-design-audit.md`, and `audit/character-audit-session2.md`.

### Morrow, the protagonist

A small porcelain seed with a teardrop-shaped hole through its body, the tip pointing
up at its face. A loose amber ember floats in the round of the drop and shows what
Morrow feels. Gold-mended cracks show
it has been broken before.

- **Personality:** curious, stubborn, easily startled, unexpectedly brave.
- **Contradiction:** collects frightening dreams because it is afraid of being forgotten.
- **Signature moves:** a lean before every move, quick uneven steps, a crest that
  rises when curious and folds back when afraid, an ember that lags behind sudden moves.
- **Palette:** porcelain `#ECE3D3`, celadon face `#22403E`, apricot `#E59B74`,
  amber ember `#FFB04A`, kintsugi gold `#C9A15E`.

### Vesper, the guardian

A tall, formal figure wrapped in one wide midnight crescent that sweeps from its right
shoulder down under its left arm, echoing its broken halo. Its dark stone face floats
inside that broken antique-gold halo. Three fragments of the halo orbit it.

- **Personality:** patient, overly formal, quietly funny, anxious about making mistakes.
- **Contradiction:** it can preserve a moment, but cannot bring back the people who
  lived in it.
- **Signature moves:** slow weight shifts and long pauses. A deep bow with one long
  hand that shelters. Fragments that swing into a shelter or go uneven when it loses
  composure.
- **Palette:** ink slate `#1B2130`, heather `#5B4757`, antique gold `#B08A52`,
  graphite stone `#3B3838`, dove mauve hands `#8E8089`.

### Nix, the troublemaker

A tiny floating crescent with a bite taken out of its lower edge and two small fins
tucked under its back. A coral line runs along its inner edge, and an "attention bead" orbits through its open centre.

- **Personality:** fearless, nosy, theatrical, and secretly afraid of being ignored.
- **Contradiction:** it steals the spotlight, but turns edge-on to disappear when
  someone pays it real attention.
- **Signature moves:** fast curved darts, then a dead-still hover. Its bead points
  at whatever it wants. Smug is a heavy, flat lid line; innocent is two round, wide eyes.
- **Palette:** eclipse `#1D1424`, lilac pearl eyes `#DCD2E8`, ember rose edge `#FF7A5C`.

## Series

The topics stay the same. Each becomes a format for this cast.

| Topic | Series | Formula |
| --- | --- | --- |
| Comedy | **Nix Touched It** | Nix touches a dream object first, and the others deal with what happens |
| Motivation | **Vesper Keeps** | Morrow loses heart. Vesper shows it a preserved moment that changes its mind |
| Mystery | **The Lost Dream** | A strange dream object lands. Three clues about whose dream it was. End on a question |
| Future | **Tomorrow's Dream** | A dream about the future drifts in, and the cast reacts to what it shows |
| Exploration | **Morrow Wanders** | Morrow follows a drifting moment to a new corner of the dream world |
| Daily news | **Dream Report** | One real, true fact, delivered as a dream object Morrow finds |

## Weekly schedule

| Day | Series |
| --- | --- |
| Monday | Vesper Keeps |
| Tuesday | Nix Touched It |
| Wednesday | The Lost Dream |
| Thursday | Tomorrow's Dream |
| Friday | Nix Touched It |
| Saturday | Morrow Wanders |
| Sunday | Dream Report |

## Production checklist for every video

1. Write a beat sheet: what each character wants, what goes wrong, and the final held pose.
2. Build any new dream objects the beat sheet needs (a shell, a stair of fragments, a book).
   None exist yet beyond Vesper's halo fragments and the floating dream fragment from stage 6.
3. Block it with the rigs, using controls only. The characters are built by
   `blender/cast_build.py`; build each scene on that file so rig fixes reach every episode.
4. Check the faces at phone size (about 180 by 320 pixels).
5. Run the follow-through bakes: Vesper's mantle and Morrow's ember.
6. Render the cuts, add sound, and add captions only if the story needs them.
7. In YouTube's upload settings, check the altered or synthetic content setting.

## Rules for news, mystery, and exploration episodes

- Check every fact against at least two reliable sources before publishing.
- Clearly separate facts from the characters' play.
- Never make the dream world look like real news footage of a real event.
