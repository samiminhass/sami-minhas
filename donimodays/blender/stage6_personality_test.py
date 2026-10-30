"""
STAGE 6 - PERSONALITY TEST. A seven-second silent scene with the stage 5 rigs.
Morrow notices a floating dream fragment and cautiously approaches. Nix darts in and
touches it first. The fragment reacts. Vesper instinctively shelters Morrow. Nix tries
to look innocent. Ends on a clear reaction pose. Everything is animated through the
rig controls, then the ember lag and mantle follow-through are baked.
Written for Blender 5.2 LTS. 24 fps, 168 frames, vertical 9:16. Shared cast code lives in cast_build.py.
"""
SCENE_NAME = "STAGE6_Personality_Test"
import os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(compile(open(os.path.join(HERE, "cast_build.py")).read(), os.path.join(HERE, "cast_build.py"), "exec"))

# ================================================================ STAGE 6: scene setup
FPS, F0, F1 = 24, 1, 168   # 7 s: the last 1.5 s is the held reaction pose
scene.render.fps = FPS; scene.frame_start = F0; scene.frame_end = F1
MR, VR, NR = RIGS["morrow"][1], RIGS["vesper"][1], RIGS["nix"][1]
mode_dream()
for ob in C_DRM.objects:                     # keep the environment simple: sky, ground, moon only
    if ob.name.startswith("DRM_shard"):
        ob.hide_render = True
set_visible([C_MOR, C_VES, C_NIX])
C_S6 = make_coll("SCENE_Stage6")

MOR_POS, MOR_ROT = Vector((0.0, 0.0, 0.0)), -20
VES_POS, VES_ROT = Vector((0.36, 0.30, 0.0)), -35
FRAG = Vector((-0.30, -0.24, 0.42))
mor.location = MOR_POS; mor.rotation_euler = (0, 0, math.radians(MOR_ROT))
ves.location = VES_POS; ves.rotation_euler = (0, 0, math.radians(VES_ROT))
upd()

# a soft rim light that only Nix receives (light linking), so it separates from Vesper's dark mantle
_nl = bpy.data.lights.new("S6_nix_rim", 'AREA'); _nl.energy = 18; _nl.size = 0.4; _nl.color = hx("#FFC9B8")
nix_rim = bpy.data.objects.new("S6_nix_rim", _nl); C_DLG.objects.link(nix_rim)
nix_rim.location = (-0.55, 0.45, 1.0)
nix_rim.rotation_euler = (Vector((-0.35, -0.25, 0.5)) - nix_rim.location).to_track_quat('-Z', 'Y').to_euler()
nix_rim.light_linking.receiver_collection = C_NIX

# the dream fragment, with its own glowing material and a light that only flares when it reacts
frag = dream_shard("S6_dream_fragment", C_S6, Vector((0, 0, 0)), seed=11)
frag.data.transform(Matrix.Diagonal((1.3, 1.3, 1.3, 1)))
fm = MATS["dream"].copy(); fm.name = "MAT_s6_fragment"; frag.data.materials[0] = fm
fb = next(n for n in fm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
fb.inputs["Emission Color"].default_value = (*hx("#FFD7A0"), 1)
L_ = bpy.data.lights.new("S6_fragment_light", 'POINT'); L_.color = hx("#FFD7A0"); L_.shadow_soft_size = 0.03
flight = bpy.data.objects.new("S6_fragment_light", L_); C_S6.objects.link(flight); flight.parent = frag

def kf(idb, path, f, v, index=-1):
    if isinstance(v, (tuple, list, Vector)):
        setattr(idb, path, v)
    else:
        if index >= 0:
            getattr(idb, path)[index] = v
        else:
            setattr(idb, path, v)
    idb.keyframe_insert(path, frame=f, index=index)

def kprop(rig, name, f, v):
    rig[name] = float(v); rig.keyframe_insert(f'["{name}"]', frame=f)

def kbone(rig, bone, f, rot=None, loc=None):
    pb = rig.pose.bones[bone]
    if rot is not None:
        pb.rotation_euler = rot; pb.keyframe_insert("rotation_euler", frame=f)
    if loc is not None:
        pb.location = loc; pb.keyframe_insert("location", frame=f)

def kworld(rig, bone, f, world):
    """Key a bone so its head sits at a WORLD position at frame f (parents evaluated first)."""
    scene.frame_set(f)
    pb = rig.pose.bones[bone]
    m = pb.matrix.copy(); m.translation = rig.matrix_world.inverted() @ Vector(world)
    pb.matrix = m
    pb.keyframe_insert("location", frame=f)

def kworld_aim(rig, bone, f, world, world_dir):
    """Key a bone's position AND turn its length (fingers) to point along world_dir, palm down."""
    scene.frame_set(f)
    pb = rig.pose.bones[bone]
    inv = rig.matrix_world.inverted()
    y = (inv.to_3x3() @ Vector(world_dir)).normalized()
    down = (inv.to_3x3() @ Vector((0, 0, -1))).normalized()
    x = y.cross(down).normalized(); z = x.cross(y).normalized()
    m = Matrix((x, y, z)).transposed().to_4x4(); m.translation = inv @ Vector(world)
    pb.matrix = m
    pb.keyframe_insert("location", frame=f); pb.keyframe_insert("rotation_euler", frame=f)

def kemit(f, strength, light_w, scale):
    fb.inputs["Emission Strength"].default_value = strength; fb.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
    L_.energy = light_w; L_.keyframe_insert("energy", frame=f)
    frag.scale = (scale,) * 3; frag.keyframe_insert("scale", frame=f)

# ================================================================ STAGE 6: fragment (always drifting)
for f in range(F0, F1 + 1, 8):
    t = f / FPS
    frag.location = FRAG + Vector((0.006 * math.sin(t * 2.1), 0, 0.012 * math.sin(t * 2.7)))
    frag.rotation_euler = (0.2 * t, 0.5 * t, 0.15 * math.sin(t))
    frag.keyframe_insert("location", frame=f); frag.keyframe_insert("rotation_euler", frame=f)
kemit(F0, 0.4, 0, 1.0); kemit(56, 0.4, 0, 1.0)
kemit(60, 14.0, 22, 1.45)                    # it reacts to Nix's touch
kemit(66, 6.0, 9, 1.2); kemit(84, 1.6, 2.5, 1.08); kemit(F1, 1.2, 1.5, 1.05)

# ================================================================ STAGE 6: Morrow
for p_, v in (("crest_mood", 0.0), ("crest_lean", 0.0), ("lid_upper_L", 0.3), ("lid_upper_R", 0.3), ("lid_lower_L", 0.1),
              ("lid_lower_R", 0.1), ("brow_raise_L", 0), ("brow_raise_R", 0), ("brow_worry_L", 0), ("brow_worry_R", 0),
              ("mouth_smile", 0.1), ("mouth_width", 0), ("grip_L", 0.45), ("grip_R", 0.45), ("blink", 0)):
    kprop(MR, p_, F0, v)
# notices (f12-18): crest rises, eyes widen, brows lift
kprop(MR, "crest_mood", 12, 0.0); kprop(MR, "crest_mood", 17, 1.0)
for k in ("L", "R"):
    kprop(MR, f"lid_upper_{k}", 12, 0.3); kprop(MR, f"lid_upper_{k}", 16, 0.05)
    kprop(MR, f"brow_raise_{k}", 12, 0); kprop(MR, f"brow_raise_{k}", 16, 0.7)
kprop(MR, "blink", 6, 0); kprop(MR, "blink", 8, 1); kprop(MR, "blink", 10, 0)
# root: anticipation then two quick uneven steps toward the fragment, a balance correction, then the startle hop back
mdir = (FRAG - MOR_POS); mdir.z = 0; mdir.normalize()
# body: a little sway and glance in the first second, anticipation, steps, the lean, the startle, and a slow recovery.
# rotation y turns the body on its vertical axis (the old root turn), so the planted feet do not slide
body = [(F0, (0, 0, 0)), (7, (0.035, 0.04, 0)), (13, (0.0, -0.02, 0)), (18, (0, 0, 0)), (23, (-0.12, 0, 0)), (27, (0.06, 0, 0)),
        (31, (0.03, 0.02, 0)), (33, (0.04, -0.09, 0)), (36, (0.05, -0.05, 0)), (44, (0.16, -0.1, 0)), (57, (0.17, -0.1, 0)),
        (61, (-0.22, -0.05, 0)), (66, (-0.1, -0.1, 0)), (90, (-0.08, -0.1, 0)), (104, (0.02, -0.15, 0)), (132, (0.0, -0.14, 0)), (F1, (0.0, -0.14, 0))]
for f, r in body:
    kbone(MR, "body", f, rot=r)
scene.frame_set(F0)
B0 = (MR.matrix_world @ MR.pose.bones["body"].matrix).to_translation()
FT0 = {k: (MR.matrix_world @ MR.pose.bones[f"foot_{k}"].matrix).to_translation() for k in ("L", "R")}
# the body stays about midway between the planted feet, so the stretchy legs stay near their rest length
for f, d, hop in ((F0, 0.0, 0.0), (24, 0.0, 0.0), (31, 0.03, 0.004), (35, 0.035, 0.0), (40, 0.075, 0.003), (58, 0.078, 0.0),
                  (60, 0.074, 0.008), (62, 0.045, 0.022), (64, 0.035, 0.0), (F1, 0.035, 0.0)):
    kworld(MR, "body", f, B0 + mdir * d + Vector((0, 0, hop)))
steps_L = ((F0, 0.0, 0.0), (25, 0.0, 0.0), (28, 0.03, 0.02), (31, 0.06, 0.0), (58, 0.06, 0.0), (60, 0.055, 0.012), (62, 0.035, 0.02), (64, 0.02, 0.0), (F1, 0.02, 0.0))
steps_R = ((F0, 0.0, 0.0), (35, 0.0, 0.0), (37, 0.045, 0.018), (40, 0.095, 0.0), (58, 0.095, 0.0), (60, 0.09, 0.012), (62, 0.07, 0.02), (64, 0.05, 0.0), (F1, 0.05, 0.0))
for k, steps_ in (("L", steps_L), ("R", steps_R)):
    for f, d, lift in steps_:
        kworld(MR, f"foot_{k}", f, FT0[k] + mdir * d + Vector((0, 0, lift)))
# expressions through the story
for f, v in ((44, 0.1), (56, 0.25), (58, 0.25), (61, -0.85), (90, -0.85), (100, -0.2), (F1, -0.15)):
    kprop(MR, "mouth_smile", f, v)
for f, v in ((57, 1.0), (60, 0.2), (64, -0.75), (67, -1.0), (88, -1.0), (102, -0.3), (F1, -0.3)):   # fast start, eased landing
    kprop(MR, "crest_mood", f, v)
for f, v in ((60, 0.0), (69, 0.0), (74, -0.55), (77, -0.6), (90, -0.6), (104, -0.2), (F1, -0.2)):   # lean comes after the hand arrives
    kprop(MR, "crest_lean", f, v)
for k in ("L", "R"):
    for f, v in ((57, 0.05), (60, 0.0), (90, 0.0), (104, 0.15), (F1, 0.15)):
        kprop(MR, f"lid_upper_{k}", f, v)
    for f, v in ((57, 0.7), (61, 0.0), (F1, 0.0)):
        kprop(MR, f"brow_raise_{k}", f, v)
    for f, v in ((57, 0.0), (61, 1.0), (96, 1.0), (106, 0.5), (F1, 0.5)):
        kprop(MR, f"brow_worry_{k}", f, v)
    for f, v in ((40, 0.45), (46, 0.15), (58, 0.15), (63, 0.9), (F1, 0.85)):
        kprop(MR, f"grip_{k}", f, v)
kprop(MR, "blink", 112, 0); kprop(MR, "blink", 114, 1); kprop(MR, "blink", 116, 0)
kprop(MR, "blink", 150, 0); kprop(MR, "blink", 152, 1); kprop(MR, "blink", 154, 0)

# ================================================================ STAGE 6: Vesper (bow keys first, IK later)
for p_, v in (("frag_shelter", 0), ("frag_spread", 0), ("frag_fluster", 0), ("lid_upper_L", 0.4), ("lid_upper_R", 0.3),
              ("lid_lower_L", 0.15), ("lid_lower_R", 0.15), ("brow_raise_L", 0), ("brow_raise_R", 0), ("grip_L", 0.6), ("grip_R", 0.6), ("blink", 0)):
    kprop(VR, p_, F0, v)
for b_, keys in (("spine_2", ((F0, (0, 0, 0)), (62, (0, 0, 0)), (78, (0.3, 0, 0.05)), (F1, (0.27, 0, 0.05)))),
                 ("spine_3", ((F0, (0, 0, 0)), (64, (0, 0, 0)), (80, (0.27, 0, 0.04)), (F1, (0.25, 0, 0.04)))),
                 ("neck", ((F0, (0, 0, 0)), (64, (0, 0, 0)), (78, (0.25, 0, 0)), (F1, (0.22, 0, 0)))),
                 ("head", ((F0, (0, 0, 0)), (50, (0, 0, 0)), (58, (0.05, 0, -0.15)), (64, (0.15, 0, 0.35)), (88, (0.15, 0, 0.3)),
                           (98, (-0.1, 0.12, -0.5)), (110, (-0.1, 0.12, -0.5)), (118, (0.05, -0.1, -0.15)), (F1, (0.05, -0.1, -0.15))))):
    for f, r in keys:
        kbone(VR, b_, f, rot=r)
for f, v in ((64, 0), (84, 1.0), (F1, 1.0)):
    kprop(VR, "frag_shelter", f, v)
for f, v in ((94, 0.0), (100, 0.35), (108, 0.0)):            # a brief, tiny loss of composure as it pretends
    kprop(VR, "frag_fluster", f, v)
for f, (l, r) in ((60, (0.4, 0.3)), (63, (0.1, 0.1)), (90, (0.1, 0.1)), (98, (0.5, 0.45)), (114, (0.62, 0.3)), (F1, (0.62, 0.3))):
    kprop(VR, "lid_upper_L", f, l); kprop(VR, "lid_upper_R", f, r)
for f, (l, r) in ((60, (0, 0)), (63, (0.8, 0.8)), (92, (0.6, 0.6)), (98, (0.1, 0.0)), (114, (0.9, -0.4)), (F1, (0.9, -0.4))):
    kprop(VR, "brow_raise_L", f, l); kprop(VR, "brow_raise_R", f, r)
for f, v in ((64, 0.6), (80, 0.78), (F1, 0.78)):
    for k in ("L", "R"):
        kprop(VR, f"grip_{k}", f, v)

# ================================================================ STAGE 6: Nix
NIX_START = Vector((0.6, -0.42, 1.05)); NIX_MID = Vector((0.16, -0.5, 0.78))
NIX_TOUCH = FRAG + Vector((-0.098, -0.02, 0.05))
NIX_TOUCH += (NIX_MID - NIX_TOUCH).normalized() * 0.016   # back off along the approach: the option B body is larger
NIX_TOUCH += Vector((-0.78, -0.25, 0.57)).normalized() * 0.02   # and away from the fragment, so the horn tip only grazes it
NIX_INNO = FRAG + Vector((-0.16, -0.06, 0.12))
for p_, v in (("attention", 0), ("fin_A_flare", 0), ("fin_B_flare", 0), ("fin_A_sweep", 0), ("fin_B_sweep", 0),
              ("lid_close", 0), ("lid_mischief", 0), ("lid_innocent", 0)):
    kprop(NR, p_, F0, v)
path = [(F0, NIX_START), (38, NIX_START), (43, NIX_MID), (48, NIX_TOUCH + Vector((0.01, 0, 0.012))), (49, NIX_TOUCH),
        (56, NIX_TOUCH), (61, NIX_TOUCH + Vector((-0.04, -0.01, 0.025))), (96, NIX_TOUCH + Vector((-0.04, -0.01, 0.025))),
        (112, NIX_INNO), (F1, NIX_INNO + Vector((0, 0, 0.006)))]
for f, p_ in path:
    nix.location = p_; nix.keyframe_insert("location", frame=f)
for f, r in ((F0, (0, 0.6, -0.6)), (38, (0, 0.6, -0.6)), (44, (0, 0.9, -0.2)), (49, (0, 0.15, 0.25)), (56, (0, 0.15, 0.25)),
             (61, (0, -0.2, 0.3)), (96, (0, -0.2, 0.3)), (110, (0, -0.1, 0.5)), (120, (0, 0.07, 0.45)), (124, (0, 0.05, 0.47)), (130, (0, 0.0, 1.5)), (146, (0, 0.0, 1.52)), (154, (0, 0.03, 0.95)), (F1, (0, 0.03, 0.92))):
    nix.rotation_euler = r; nix.keyframe_insert("rotation_euler", frame=f)
for f, (fa, fb_, sw) in ((38, (0, 0, 0)), (42, (0.3, 0.3, 1.0)), (48, (0.6, 0.6, 0.5)), (51, (0.2, 0.2, 0)), (54, (1.0, 0.1, -0.3)),
                         (57, (1.0, 0.1, -0.3)), (60, (-1.0, -1.0, 0.2)), (70, (-0.3, -0.3, 0)), (100, (-0.3, -0.3, 0)),
                         (108, (-0.7, -0.6, 0.3)), (F1, (-0.7, -0.6, 0.3))):
    kprop(NR, "fin_A_flare", f, fa); kprop(NR, "fin_B_flare", f, fb_); kprop(NR, "fin_A_sweep", f, sw); kprop(NR, "fin_B_sweep", f, sw)
for f, v in ((38, 0), (46, -80), (56, -95), (62, -60), (100, -60), (110, 60), (F1, 62)):
    kprop(NR, "attention", f, v)
for f, (c, m_, i_) in ((48, (0, 0, 0)), (51, (0, 0.8, 0)), (57, (0, 0.8, 0)), (60, (0, 0, 0)), (100, (0, 0, 0)), (108, (0.25, 0, 1.0)), (F1, (0.25, 0, 1.0))):
    kprop(NR, "lid_close", f, c); kprop(NR, "lid_mischief", f, m_); kprop(NR, "lid_innocent", f, i_)

# ================================================================ STAGE 6: Vesper's dry glance at Nix in the hold
# measured, not guessed: try head turns at the last frame and keep the one whose FACE points nearest Nix.
# The face direction is mask centre to the eyes (the head bone's own axes mostly roll the face, which reads
# as a tilt, not a look)
def _ctr(o):
    oe = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = oe.to_mesh()
    c_ = sum((oe.matrix_world @ v.co for v in me.vertices), Vector()) / len(me.vertices); oe.to_mesh_clear(); return c_
def ves_face_to(target):
    e = (_ctr(bpy.data.objects["VES_eye_L"]) + _ctr(bpy.data.objects["VES_eye_R"])) / 2
    return math.degrees((e - _ctr(bpy.data.objects["VES_mask"])).angle(target - e))
scene.frame_set(F1); _g0 = ves_face_to(nix.matrix_world.translation)
_best = None
_vals = [i_ / 10 for i_ in range(-5, 6)]
for _x in _vals:
    for _y in _vals:
        for _z in _vals:
            VR.pose.bones["head"].rotation_euler = (_x, _y, _z); bpy.context.view_layer.update()
            _a = ves_face_to(nix.matrix_world.translation)
            if _best is None or _a < _best[0]:
                _best = (_a, (_x, _y, _z))
kbone(VR, "head", 131, rot=(0.05, -0.1, -0.15))          # still looking at Morrow as Nix starts to hide
kbone(VR, "head", 135, rot=_best[1]); kbone(VR, "head", F1, rot=_best[1])   # blink, then a quick turn
for f, v in ((129, 0), (131, 1), (133, 0)):
    kprop(VR, "blink", f, v)
for f, v in ((131, 0.6), (135, 0.95), (F1, 0.95)):      # the halo counter-rotates harder as the head dips toward Nix
    kprop(VR, "halo_level", f, v)
for f, (l, r) in ((133, (0.0, 0.0)), (137, (0.5, -0.3)), (F1, (0.5, -0.3))):   # one dry, unimpressed brow
    kprop(VR, "brow_tilt_L", f, l); kprop(VR, "brow_tilt_R", f, r)
scene.frame_set(150); _gm = ves_face_to(_ctr(bpy.data.objects["MOR_face"]))
print(f"VESPER GLANCE face-to-Nix {_g0:.1f} deg before, {_best[0]:.1f} deg after (face-to-Morrow {_gm:.1f}), head {_best[1]}", flush=True)

# ================================================================ STAGE 6: IK and look targets (need parents evaluated)
mor_side = min(("L", "R"), key=lambda k: ((MR.matrix_world @ MR.pose.bones[f"hand_IK_{k}"].head) - FRAG).length)
oth = "R" if mor_side == "L" else "L"
scene.frame_set(F0)
rest_hand = {k: (MR.matrix_world @ MR.pose.bones[f"hand_IK_{k}"].matrix).to_translation() for k in ("L", "R")}
reach = FRAG + (rest_hand[mor_side] - FRAG).normalized() * 0.085
chest = lambda f: (MR.matrix_world @ MR.pose.bones["body"].matrix) @ Vector((0, 0.17, 0.18))
for f in (F0, 40):
    kworld(MR, f"hand_IK_{mor_side}", f, rest_hand[mor_side])
kworld(MR, f"hand_IK_{mor_side}", 47, reach); kworld(MR, f"hand_IK_{mor_side}", 57, reach + Vector((0, 0, 0.005)))
for k in ("L", "R"):
    scene.frame_set(64)
    tgt = (MR.matrix_world @ MR.pose.bones["body"].matrix) @ Vector(((0.06 if k == "L" else -0.06), 0.16, 0.2))
    kworld(MR, f"hand_IK_{k}", 64, tgt); kworld(MR, f"hand_IK_{k}", F1, tgt)
kworld(MR, f"hand_IK_{oth}", 57, (MR.matrix_world @ MR.pose.bones[f"hand_IK_{oth}"].matrix).to_translation())
look = [(F0, FRAG + Vector((0.25, -0.2, 0.1))), (12, FRAG + Vector((0.25, -0.2, 0.1))), (16, FRAG), (56, FRAG), (60, FRAG + Vector((0, 0, 0.05))),
        (88, FRAG), (100, Vector((0.1, 0.0, 0.85))), (108, NIX_INNO), (F1, NIX_INNO)]
for f, p_ in look:
    kworld(MR, "eye_target", f, p_)
ves_side = min(("L", "R"), key=lambda k: ((VR.matrix_world @ VR.pose.bones[f"hand_IK_{k}"].head) - MOR_POS).length)
scene.frame_set(F0)
v_rest = (VR.matrix_world @ VR.pose.bones[f"hand_IK_{ves_side}"].matrix).to_translation()
kworld(VR, f"hand_IK_{ves_side}", F0, v_rest); kworld(VR, f"hand_IK_{ves_side}", 64, v_rest)
over = MOR_POS + mdir * 0.035 + Vector((0.03, 0.02, 0.70))
aim = (MOR_POS - VES_POS); aim.z = 0; aim = (aim.normalized() + Vector((0, 0, -0.25))).normalized()   # fingers reach over Morrow
kworld(VR, f"hand_IK_{ves_side}", 64, v_rest)
scene.frame_set(64); VR.pose.bones[f"hand_IK_{ves_side}"].keyframe_insert("rotation_euler", frame=64)
kworld_aim(VR, f"hand_IK_{ves_side}", 78, over + Vector((0.0, 0.03, 0.05)), aim)
kworld_aim(VR, f"hand_IK_{ves_side}", 84, over, aim)
kworld_aim(VR, f"hand_IK_{ves_side}", F1, over + Vector((0, 0, 0.005)), aim)

v_oth = "R" if ves_side == "L" else "L"
scene.frame_set(F0)
v_rest2 = (VR.matrix_world @ VR.pose.bones[f"hand_IK_{v_oth}"].matrix).to_translation()
def ves_chest(f, side_off=0.0, fwd=0.2, up=0.27):
    scene.frame_set(f)
    m = VR.matrix_world @ VR.pose.bones["spine_3"].matrix
    return m @ Vector((side_off, up, fwd + 0.045))   # clear of the mantle surface
for f in (F0, 64):
    kworld(VR, f"hand_IK_{v_oth}", f, v_rest2)
def ves_fwd(f):
    scene.frame_set(f)
    return ((VR.matrix_world @ VR.pose.bones["spine_3"].matrix).to_3x3() @ Vector((0, 0, 1))).normalized()
for f in (76, 82, 88):          # the bow brings the mantle forward, so the waiting hand eases forward with it
    kworld(VR, f"hand_IK_{v_oth}", f, v_rest2 + ves_fwd(f) * 0.05)
kworld(VR, f"hand_IK_{v_oth}", 91, v_rest2.lerp(ves_chest(98), 0.3) + ves_fwd(91) * 0.06)   # arcs out in front of the mantle
kworld(VR, f"hand_IK_{v_oth}", 94, v_rest2.lerp(ves_chest(98), 0.65) + ves_fwd(94) * 0.06)
kworld(VR, f"hand_IK_{v_oth}", 98, ves_chest(98))                      # hand rises to its collar as it looks away
kworld(VR, f"hand_IK_{v_oth}", 108, ves_chest(108, fwd=0.22))
to_nix = (NIX_INNO - ves_chest(116)); to_nix.normalize()
kworld(VR, f"hand_IK_{v_oth}", 118, ves_chest(118, fwd=0.26) + to_nix * 0.1)   # a small, dry open-palm gesture toward Nix
kworld(VR, f"hand_IK_{v_oth}", 132, ves_chest(132, fwd=0.24) + to_nix * 0.07)
kworld(VR, f"hand_IK_{v_oth}", F1, ves_chest(F1, fwd=0.23) + to_nix * 0.06)
for f, v in ((96, 0.6), (100, 0.85), (114, 0.85), (118, 0.25), (F1, 0.3)):
    kprop(VR, f"grip_{v_oth}", f, v)

# ================================================================ STAGE 6: bake the follow-through
frames = list(range(F0, F1 + 1))
bake_follow_through(VR, frames, [("mantle_1", "spine_1"), ("mantle_2", "spine_2"), ("mantle_3", "spine_3")], delay=4, scale=1.0)
bake_lag(MR, frames, "ember", "body", k=0.5, smooth=0.55)
scene.frame_set(F0)

# ================================================================ STAGE 6: cameras and cuts
def make_cam(name, target, view, height, lens=40, push=0.0, f_in=F0, f_out=F1):
    cd = bpy.data.cameras.new(name); c = bpy.data.objects.new(name, cd); C_CAM.objects.link(c)
    cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24
    view = Vector(view).normalized()
    dist = (height / 2) / math.tan(math.atan(12 / lens))
    for f, pu in ((f_in, 0.0), (f_out, push)):
        c.location = Vector(target) + view * (dist - pu)
        c.rotation_euler = (-view).to_track_quat('-Z', 'Y').to_euler()
        c.keyframe_insert("location", frame=f); c.keyframe_insert("rotation_euler", frame=f)
    return c

def where(ob_name, f):
    scene.frame_set(f)
    ob = bpy.data.objects[ob_name]
    pts = [ob.matrix_world @ Vector(c_) for c_ in ob.bound_box]
    return sum(pts, Vector()) / 8

WIDE_T, WIDE_V = Vector((-0.1, -0.1, 0.86)), (0.05, -1.0, 0.1)
morrow_face_62 = where("MOR_face", 62)
nix_118 = where("NIX_body", 122)
_faces = [where("MOR_face", f) for f in range(67, 85)]
cu_t = sum(_faces, Vector()) / len(_faces) + Vector((0, 0, 0.03))
SHOTS = [  # (first frame, camera)
    (1, make_cam("CAM_1_wide_notice", WIDE_T, WIDE_V, 2.25, push=0.08, f_in=1, f_out=40)),
    (41, make_cam("CAM_2_insert_touch_flare", Vector((-0.27, -0.24, 0.46)), (0.3, -1.0, 0.1), 0.82, lens=50, push=0.03, f_in=41, f_out=66)),
    (67, make_cam("CAM_3_closeup_startle", cu_t, (-0.25, -1.0, 0.06), 0.5, lens=60, push=0.0, f_in=67, f_out=84)),   # 0.75 s, so the startle reads
    (85, make_cam("CAM_4_medium_shelter", Vector((-0.14, -0.08, 0.84)), (0.1, -1.0, 0.1), 1.6, lens=45, push=0.06, f_in=85, f_out=112)),
    (113, make_cam("CAM_5_closeup_innocent", nix_118 + Vector((-0.005, 0, 0.0)), (-0.4, -1.0, 0.06), 0.34, lens=60, push=0.01, f_in=113, f_out=132)),
    (133, make_cam("CAM_6_wide_final_hold", WIDE_T + Vector((0, 0, -0.02)), WIDE_V, 2.15, push=0.03, f_in=133, f_out=F1)),
]
for f, c_ in SHOTS:                     # timeline markers bound to cameras, so the cuts also work in Blender
    mk = scene.timeline_markers.new(c_.name, frame=f); mk.camera = c_
def camera_for(f):
    return [c_ for f0, c_ in SHOTS if f0 <= f][-1]
scene.camera = SHOTS[0][1]
scene.frame_set(F0)

# ================================================================ STAGE 6: pupil check on every frame
def mean_eval(ob):
    dg = bpy.context.evaluated_depsgraph_get(); oe = ob.evaluated_get(dg); me = oe.to_mesh()
    c_ = sum((oe.matrix_world @ v.co for v in me.vertices), Vector()) / len(me.vertices); oe.to_mesh_clear(); return c_
worst_pupil = (0, 0)
for f in range(F0, F1 + 1):
    scene.frame_set(f)
    for k in ("L", "R"):
        ny = (MR.matrix_world.to_3x3() @ MR.data.bones[f"eye_{k}"].matrix_local.col[1].xyz)
        bm_ = MR.matrix_world @ MR.pose.bones["body"].matrix
        ny = (bm_.to_3x3() @ (MR.pose.bones["body"].bone.matrix_local.to_3x3().inverted() @ (MR.matrix_world.to_3x3().inverted() @ ny))).normalized()
        a_ = math.degrees((mean_eval(bpy.data.objects[f"MOR_pupil_{k}"]) - mean_eval(bpy.data.objects[f"MOR_eye_{k}"])).angle(ny))
        if a_ > worst_pupil[0]:
            worst_pupil = (a_, f)
print(f"PUPIL CHECK worst {worst_pupil[0]:.1f} degrees at frame {worst_pupil[1]}", flush=True)
_leg = [9, 0, 0, 0]
for f in range(F0, F1 + 1):
    scene.frame_set(f)
    for k in ("L", "R"):
        pb = MR.pose.bones[f"leg_{k}"]
        r_ = (pb.tail - pb.head).length / MR.data.bones[f"leg_{k}"].length
        if r_ < _leg[0]: _leg[0], _leg[2] = r_, f
        if r_ > _leg[1]: _leg[1], _leg[3] = r_, f
from mathutils.bvhtree import BVHTree as _BVH
def _bvh(o):
    oe = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = oe.to_mesh()
    t = _BVH.FromPolygons([oe.matrix_world @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons]); oe.to_mesh_clear(); return t
_O = bpy.data.objects
_pairs = [("Nix vs fragment", [o for o in _O if o.name.startswith(("NIX_body", "NIX_edge"))], [frag], range(40, 70)),
          ("Vesper hands vs mantle", [o for o in _O if o.name.startswith("VES_hand_") and o.type == 'MESH'],
           [_O["VES_mantle_crescent"], _O["VES_panel_back_calm"], _O["VES_hood"]], range(60, 120)),
          ("Vesper hand vs Morrow crest", [o for o in _O if o.name.startswith("VES_hand_") and o.type == 'MESH'],
           [_O["MOR_crest"], _O["MOR_crest_fork"]], range(60, 120))]
for _nm, _a, _b, _fr in _pairs:
    _hit = []
    for f in _fr:
        scene.frame_set(f)
        _tb = [_bvh(o) for o in _b]
        if any(_bvh(o).overlap(t) for o in _a for t in _tb):
            _hit.append(f)
    print(f"CONTACT CHECK {_nm}: {len(_hit)} frames {_hit[:12]}", flush=True)
print(f"LEG CHECK length {_leg[0]:.2f}x (frame {_leg[2]}) to {_leg[1]:.2f}x (frame {_leg[3]}) of rest", flush=True)
scene.frame_set(F0)

# ================================================================ STAGE 6: render
MODE6 = os.environ.get("STAGE6_MODE", "full")
if OUT:
    os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
    if os.environ.get("STAGE6_SKIP_PUPIL") is None:
        pass
    r = scene.render
    r.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = int(os.environ.get("STAGE6_SAMPLES", "48")); scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = 0.03
    r.use_persistent_data = True
    scene.cycles.max_bounces = 4; scene.cycles.diffuse_bounces = 2; scene.cycles.glossy_bounces = 2; scene.cycles.transmission_bounces = 4
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, int(os.environ.get("STAGE6_PCT", "100"))
    r.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'; scene.view_settings.exposure = 0.0
    r.resolution_percentage = 100; scene.camera = SHOTS[0][1]; scene.frame_set(F0)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "stage6_personality_test.blend"))   # saved with the real settings
    r.resolution_percentage = int(os.environ.get("STAGE6_PCT", "100"))
    if MODE6 == "stills":
        frames_to_render = [int(x) for x in os.environ.get("STAGE6_FRAMES", "1,49,62,84,118,144").split(",")]
    else:
        a_, b_ = [int(x) for x in os.environ.get("STAGE6_RANGE", f"{F0}-{F1}").split("-")]
        frames_to_render = list(range(a_, b_ + 1))
    import time
    for f in frames_to_render:
        t0 = time.time()
        scene.frame_set(f)
        scene.camera = camera_for(f)
        r.filepath = os.path.join(OUT, "frames", f"f{f:04d}.png")
        if MODE6 != "stills" and os.path.exists(r.filepath):
            continue   # resume an interrupted batch
        bpy.ops.render.render(write_still=True)
        print(f"FRAME {f} {time.time()-t0:.1f}s", flush=True)
    print("ALL DONE", flush=True)
