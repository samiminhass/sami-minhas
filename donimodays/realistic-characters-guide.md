# How to Generate Characters That Look Real

Researched October 2026. Most sources are blogs written by tool makers, so treat
their claims as marketing until you test them yourself.

## What "real" means for donimodays

There are two kinds of "real":

- **Photoreal** means it looks like a camera filmed it: real skin, real fabric, real
  light. This suits realistic humans and news-style scenes.
- **Premium 3D** means it looks like a big-studio animated film: believable materials,
  lighting, and depth, but stylized shapes. This is the right target for Donimo,
  Pip, and Old Tock.

Both come from the same three things: **specific materials, specific lighting, and a
locked character reference.**

## The workflow

### Step 1. Make one perfect master image per character

Use an image model such as Google's Nano Banana, Midjourney, or ChatGPT Images.
Upload the render from the `images` folder as a reference, then paste the character
prompt block, the style line, and the realism words below.

Example master prompt for Donimo:

> [paste Donimo prompt block], standing on a dusk hill, full body, front
> three-quarter view, matte porcelain with subtle surface imperfections and tiny
> micro scratches, soft subsurface scattering in the cream face, knit beanie with
> visible wool fibers, warm sunset rim light from behind, soft cool fill light from
> camera left, natural catchlights in the glowing eyes, 50mm lens, f/2.8, shallow
> depth of field, [paste style line]

Generate many versions and pick one. That picture becomes the official Donimo.
Every later image and clip is checked against it.

### Step 2. Build a character sheet

From the master image, generate the same character from 2 to 4 angles: front,
three-quarter, side, and back. Add a few expressions. Guides agree that a single
reference works for a short, simple clip. Multi-shot stories hold together better
with 2 to 4 angles.

### Step 3. Animate with a tool that accepts references

| Tool | How it keeps the character the same |
| --- | --- |
| Kling 3.0 | "Elements" takes 1 to 4 reference images, each tagged as a character, object, or scene |
| Runway Gen-4 and Gen-4.5 | "References" uses one image as an identity anchor, with no training needed |
| Seedance | Multi-reference input and multi-shot storyboards |
| Atlabs, Paintbrush, Neolemon | Built for recurring casts. You save each character once and reuse it |

Test the same three-shot scene in two or three tools before choosing one. No
independent benchmarks exist yet.

### Step 4. Pass the character from shot to shot

Export a clean frame of the character from the end of clip one. Use it as the
reference for clip two, and so on. Guides call this **reference propagation**.
It stops the character slowly drifting away from the design.

### Step 5. Keep shots short and simple

- One action per clip, 3 to 6 seconds.
- Slow camera moves. Fast spins cause the character to change shape.
- Check the first, middle, and last frame of every clip. Drift usually shows up
  near the end.
- Regenerate any clip where the character looks wrong. Never keep "close enough".

### Step 6. Optional: train your own character model

Once the channel grows, you can train a small custom model, often called a LoRA, on
15 to 30 clean images of a character. After that, the tool knows Donimo without a
reference image. Several platforms offer this without code.

## Realism words that actually work

AI models default to smooth, plastic, evenly lit images. Specific wording fixes that.

**Lighting.** Name the direction and quality, not the mood.

- Write "warm rim light from behind, soft fill from camera left".
- Do not write only "well lit" or "beautiful lighting".
- Avoid hard light straight from above unless you want a moody look.
- Ask for "natural catchlights in the eyes". Eyes without reflections look dead.

**Camera.** Use real photography terms.

- "50mm lens, f/2.8, shallow depth of field" for character shots.
- "85mm lens" for close-ups.
- "wide 24mm lens, low angle" for epic exploration shots.

**Materials.** Say what things are made of and how they have aged.

- "matte porcelain with micro scratches" instead of "white".
- "knit wool with visible fibers" instead of "a hat".
- "brushed brass with fingerprints and patina" instead of "gold".
- "subsurface scattering" makes light glow softly through a surface.

**For realistic humans,** if a news or story episode needs one.

- "natural skin texture, visible pores, no airbrushing".
- Name age range, hair, eye color, and clothing exactly. Never write just "a man".

## The 3D route, for later

If you want full control instead of AI video:

- **Meshy** generates a 3D model of a character from images and can rig it
  automatically, so it is ready to animate.
- **DeepMotion** turns a video of you acting into 3D animation. Its free tier gives
  60 seconds per month for personal use.
- **Blender** is free and puts it all together into final renders.

## Sources

- [Atlabs: Best Character Consistency AI Video Tools in 2026](https://www.atlabs.ai/blog/best-character-consistency-ai-video-tools-in-2026-(ultimate-guide))
- [Higgsfield: 7 Tools for Consistent AI Characters](https://higgsfield.ai/blog/tools-for-consistent-ai-characters)
- [Neolemon: How to Create Consistent Characters in AI Videos](https://www.neolemon.com/blog/how-to-create-consistent-characters-in-ai-videos-complete-guide/)
- [Paintbrush: Best AI Video Generators for Consistent Characters](https://www.paintbrush.gg/blog/best-ai-video-generator-consistent-characters)
- [Magic Hour: How to Keep Characters Consistent in AI Video](https://magichour.ai/blog/how-to-keep-characters-consistent-in-ai-video)
- [Martini: How to Build a Consistent AI Character](https://martini.art/en/blog/how-to-build-consistent-ai-character)
- [Lovino: AI Character Consistency Across Videos](https://lovino.ai/blog/ai-character-consistency-across-videos-2026)
- [Prompt Architects: Getting Realistic Skin in AI Images](https://prompt-architects.com/blog/361-getting-realistic-skin-in-ai-images)
- [The Neural Post: Physics Prompting Guide for Nano Banana](https://theneuralpost.com/2025/12/10/mastering-nano-banana-the-physics-prompting-guide-for-perfect-lighting/)
- [GPTImg: Prompting Nano Banana for Photorealistic Faces](https://gptimg.co/blog/nano-banana-photorealistic-faces-hands)
