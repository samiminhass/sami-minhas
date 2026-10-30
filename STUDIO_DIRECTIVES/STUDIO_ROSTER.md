# Studio Roster and Communication Protocol

Maintained by Session 01 (Character Lab) as the studio's communication hub.
Repository: `samiminhass/sami-minhas`. Studio-wide documents live on branch `claude/dreamy-wozniak-qzx8c8`.

## Departments

| Session | Department | Session ID | Owns |
|---------|------------|------------|------|
| EP | Executive Producer (human) | — | Final creative authority, all approvals, the YouTube channel and brand, all publishing and account actions |
| 01 | 3D Character Design & Development Lab | `session_01D6wRLhmJ7agjY25rura968` | Characters, expressions, models, materials, rigs, character release packages |
| 02 | Animation & Film Production Studio | `session_01D6wRLgXUPHhH4gQF84wdTN` | Story, animation, cinematography, environments, sound, editing, platform deliverables |
| 03 | Independent Creative & Technical Audit Studio | `session_01D6wRLgw1j8JZ8PCoMhwkTo` | Independent audits of both departments, `AUDIT_LOG.md` |

## How the sessions stay connected

1. **Messages.** Session 01 can send messages to Sessions 02 and 03. Their tool lists show they can receive messages but cannot send them. So Session 01 relays notices between departments, and the EP can post directly in any session.
2. **Shared documents.** Studio-wide directives, the roster and EP decisions are in `STUDIO_DIRECTIVES/` on `claude/dreamy-wozniak-qzx8c8`. Read them with:
   ```bash
   git fetch origin claude/dreamy-wozniak-qzx8c8
   git show origin/claude/dreamy-wozniak-qzx8c8:STUDIO_DIRECTIVES/EP_DECISIONS.md
   ```
3. **Each department writes only to its own branch** and keeps a status file there:
   - Session 01: `CHARACTER_ASSETS/08_DOCUMENTATION/STATUS.md`
   - Session 02: `ANIMATION_PRODUCTION/STATUS.md`
   - Session 03: `AUDIT/AUDIT_LOG.md` and `AUDIT/STATUS.md`
4. **Reading other departments' work.** Every session can list and read every branch:
   ```bash
   git ls-remote --heads origin
   git fetch origin <branch>
   git show origin/<branch>:<path>
   ```
5. **Submissions and findings.** A department submits work by naming the branch, path and version. The Audit Studio reports findings in its `AUDIT_LOG.md` with the same references. Session 01 relays the submission notice and the verdict.
6. **Versions are never overwritten.** Each new version is a new file or a new commit, and every cross-department reference cites an exact version.

## Shared production environment

All sessions run in the same cloud environment and can install the same Blender build:

```bash
bash STUDIO_DIRECTIVES/setup_blender.sh
```

- Blender **5.2.3 LTS** as a Python module (`bpy`), supported until July 2028.
- Render engines verified headless: Cycles (CPU), Workbench, and EEVEE through software graphics (slow).
- 4 CPU threads per session, no GPU. Final-quality rendering will be the studio's main capacity limit.
