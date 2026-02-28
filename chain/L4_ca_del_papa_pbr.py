"""
HomeForge AI — Ca' del Papa — Render Fotorealistico PBR — FINALE
5 iterazioni di raffinamento:
- Muri in sasso: castle_wall_slates con TRUE DISPLACEMENT + mortar darkening
- Tetto piode: castle_wall_slates ruotato/desaturato
- Travi gronda: weathered_brown_planks PBR
- Vetrata angolare SW 3.0x2.6m riflettente
- HDRI alpino + overcast lighting
- Alberi multi-lobe, sassi sparsi, no cespugli
- Soffit sotto gronda, pannelli interni
- 512 samples, doppio render + fotoinserimento
"""
import bpy, bmesh, math, os, time, random
from pathlib import Path
from mathutils import Vector

# === CONFIG ===
PROJECT_DIR = Path(__file__).parent.parent
PHOTOS_DIR = PROJECT_DIR / "photos"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEX_DIR = PROJECT_DIR / "chain" / "materials" / "textures"
HDRI_PATH = str(TEX_DIR / "alps_field_2k.hdr")

FOTO_SORGENTE = Path("C:/Users/Stramba/casa/foto_input/WhatsApp Image 2026-02-13 at 10.07.14.jpeg")
RENDER_MODEL = str(OUTPUT_DIR / "ca_del_papa_model.png")
RENDER_FINALE = str(OUTPUT_DIR / "ca_del_papa_render.png")
RENDER_STANDALONE = str(OUTPUT_DIR / "ca_del_papa_standalone.png")

# Texture paths
tex_stone = {
    "diff": str(TEX_DIR / "castle_wall_slates_diff_2k.jpg"),
    "nor":  str(TEX_DIR / "castle_wall_slates_nor_gl_2k.jpg"),
    "rough": str(TEX_DIR / "castle_wall_slates_rough_2k.jpg"),
    "disp": str(TEX_DIR / "castle_wall_slates_disp_2k.png"),
    "ao":   str(TEX_DIR / "castle_wall_slates_ao_2k.jpg"),
}
tex_wood = {
    "diff": str(TEX_DIR / "weathered_brown_planks_diff_2k.jpg"),
    "nor":  str(TEX_DIR / "weathered_brown_planks_nor_gl_2k.jpg"),
    "rough": str(TEX_DIR / "weathered_brown_planks_rough_2k.jpg"),
    "disp": str(TEX_DIR / "weathered_brown_planks_disp_2k.png"),
    "ao":   str(TEX_DIR / "weathered_brown_planks_ao_2k.jpg"),
}

# Parametri edificio (aggiornato: 11x10m come richiesto)
W = 11.0    # larghezza X (est-ovest)
D = 10.0    # profondita Y (nord-sud)
HG = 3.0    # altezza gronda
HC = 4.8    # altezza colmo
T = 0.45    # spessore muri
CO = 1.5    # offset colmo verso nord
SP = 0.40   # sporto gronda
RT = 0.18   # spessore tetto

# Vetrata angolare SW — più grande per impatto visivo
VET_W = 3.00  # larghezza vetrata (era 2.40)
VET_H = 2.60  # altezza vetrata (era 2.40)


# === UTILITY ===
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print("  Scene reset.")


def make_box(name, w, d, h):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    obj.scale = (w, d, h)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    obj.select_set(False)
    return obj


def boolean_cut(target_obj, cutter_name, w, d, h, x, y, z):
    cutter = make_box(cutter_name, w, d, h)
    cutter.location = (x, y, z)
    cutter.hide_render = True
    cutter.hide_viewport = True
    mod = target_obj.modifiers.new(name=cutter_name, type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    return cutter


def apply_modifiers(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError:
            obj.modifiers.remove(mod)
    obj.select_set(False)


# === MATERIALI PBR ===

def mat_pietra_pbr():
    """Muro misto alpi - castle_wall_slates con TRUE DISPLACEMENT, mortar darkening, AO."""
    mat = bpy.data.materials.new("PietraPBR")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (1200, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-2000, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1800, 0)
    mp.inputs["Scale"].default_value = (0.75, 0.75, 0.75)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    # Diffuse + AO
    td = tx("Diff", tex_stone["diff"], "sRGB", (-1400, 600))
    ta = tx("AO", tex_stone["ao"], "Non-Color", (-1400, 400))

    # AO crush with Gamma (dark mortar joints)
    ao_gamma = nt.nodes.new("ShaderNodeGamma"); ao_gamma.location = (-1200, 400)
    ao_gamma.inputs["Gamma"].default_value = 0.35
    nt.links.new(ta.outputs["Color"], ao_gamma.inputs["Color"])

    # Multiply diffuse x AO
    mx_ao = nt.nodes.new("ShaderNodeMix")
    mx_ao.data_type = 'RGBA'; mx_ao.blend_type = 'MULTIPLY'
    mx_ao.location = (-1000, 500); mx_ao.inputs["Factor"].default_value = 1.0
    nt.links.new(td.outputs["Color"], mx_ao.inputs[6])
    nt.links.new(ao_gamma.outputs["Color"], mx_ao.inputs[7])

    # Brightness/Contrast
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-800, 500)
    bc.inputs["Contrast"].default_value = 0.25
    nt.links.new(mx_ao.outputs[2], bc.inputs["Color"])

    # HSV
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-600, 500)
    hsv.inputs["Hue"].default_value = 0.505
    hsv.inputs["Saturation"].default_value = 0.92
    hsv.inputs["Value"].default_value = 1.40
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])

    # Warm/cool variation via noise
    noise_v = nt.nodes.new("ShaderNodeTexNoise"); noise_v.location = (-1000, 200)
    noise_v.inputs["Scale"].default_value = 1.0
    noise_v.inputs["Detail"].default_value = 4.0
    noise_v.inputs["Roughness"].default_value = 0.6
    nt.links.new(tc.outputs["Generated"], noise_v.inputs["Vector"])

    warm_hsv = nt.nodes.new("ShaderNodeHueSaturation"); warm_hsv.location = (-400, 300)
    warm_hsv.inputs["Hue"].default_value = 0.55
    warm_hsv.inputs["Saturation"].default_value = 1.35
    warm_hsv.inputs["Value"].default_value = 1.05
    nt.links.new(hsv.outputs["Color"], warm_hsv.inputs["Color"])

    ramp_v = nt.nodes.new("ShaderNodeValToRGB"); ramp_v.location = (-600, 200)
    ramp_v.color_ramp.elements[0].position = 0.30
    ramp_v.color_ramp.elements[1].position = 0.70
    nt.links.new(noise_v.outputs["Fac"], ramp_v.inputs["Fac"])

    color_var = nt.nodes.new("ShaderNodeMix")
    color_var.data_type = 'RGBA'; color_var.location = (-200, 500)
    nt.links.new(ramp_v.outputs["Color"], color_var.inputs["Factor"])
    nt.links.new(hsv.outputs["Color"], color_var.inputs[6])
    nt.links.new(warm_hsv.outputs["Color"], color_var.inputs[7])

    # Mortar darkening via displacement map
    tdi_col = tx("DispColor", tex_stone["disp"], "Non-Color", (-1400, -800))
    invert = nt.nodes.new("ShaderNodeInvert"); invert.location = (-1200, -800)
    nt.links.new(tdi_col.outputs["Color"], invert.inputs["Color"])

    ramp_m = nt.nodes.new("ShaderNodeValToRGB"); ramp_m.location = (-1000, -800)
    ramp_m.color_ramp.elements[0].position = 0.0
    ramp_m.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp_m.color_ramp.elements[1].position = 0.25
    ramp_m.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(invert.outputs["Color"], ramp_m.inputs["Fac"])

    mortar_col = nt.nodes.new("ShaderNodeRGB"); mortar_col.location = (-800, -800)
    mortar_col.outputs[0].default_value = (0.025, 0.025, 0.02, 1.0)

    mortar_mix = nt.nodes.new("ShaderNodeMix")
    mortar_mix.data_type = 'RGBA'; mortar_mix.location = (0, 500)
    nt.links.new(ramp_m.outputs["Color"], mortar_mix.inputs["Factor"])
    nt.links.new(color_var.outputs[2], mortar_mix.inputs[6])
    nt.links.new(mortar_col.outputs[0], mortar_mix.inputs[7])

    nt.links.new(mortar_mix.outputs[2], bsdf.inputs["Base Color"])

    # Roughness
    tr = tx("Rough", tex_stone["rough"], "Non-Color", (-1400, 0))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # Normal + Bump
    tn = tx("Nor", tex_stone["nor"], "Non-Color", (-1400, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-1000, -200)
    nm.inputs["Strength"].default_value = 2.8
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex_stone["disp"], "Non-Color", (-1400, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-800, -400)
    bmp.inputs["Strength"].default_value = 0.7
    bmp.inputs["Distance"].default_value = 0.025
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])

    # Micro noise
    noise_m = nt.nodes.new("ShaderNodeTexNoise"); noise_m.location = (-1400, -650)
    noise_m.inputs["Scale"].default_value = 55.0
    noise_m.inputs["Detail"].default_value = 7.0
    nt.links.new(tc.outputs["Generated"], noise_m.inputs["Vector"])
    bmp2 = nt.nodes.new("ShaderNodeBump"); bmp2.location = (-600, -450)
    bmp2.inputs["Strength"].default_value = 0.04
    bmp2.inputs["Distance"].default_value = 0.004
    nt.links.new(noise_m.outputs["Fac"], bmp2.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], bmp2.inputs["Normal"])
    nt.links.new(bmp2.outputs["Normal"], bsdf.inputs["Normal"])

    # True displacement
    disp_node = nt.nodes.new("ShaderNodeDisplacement"); disp_node.location = (1200, -300)
    disp_node.inputs["Scale"].default_value = 0.045
    disp_node.inputs["Midlevel"].default_value = 0.5
    nt.links.new(tdi.outputs["Color"], disp_node.inputs["Height"])
    nt.links.new(disp_node.outputs["Displacement"], out.inputs["Displacement"])

    mat.displacement_method = 'BOTH'
    return mat


def mat_piode_pbr():
    """Piode tetto - castle_wall_slates ruotato, desaturato."""
    mat = bpy.data.materials.new("PiodePBR")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1200, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (800, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1600, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1400, 0)
    mp.inputs["Scale"].default_value = (3.0, 3.0, 3.0)
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(90))
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    td = tx("Diff", tex_stone["diff"], "sRGB", (-1000, 400))
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-600, 400)
    hsv.inputs["Saturation"].default_value = 0.55
    hsv.inputs["Value"].default_value = 0.70
    nt.links.new(td.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    tr = tx("Rough", tex_stone["rough"], "Non-Color", (-1000, 100))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    tn = tx("Nor", tex_stone["nor"], "Non-Color", (-1000, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-600, -200)
    nm.inputs["Strength"].default_value = 2.0
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex_stone["disp"], "Non-Color", (-1000, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-400, -400)
    bmp.inputs["Strength"].default_value = 1.0
    bmp.inputs["Distance"].default_value = 0.06
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def mat_legno_pbr():
    """Legno travi/telai - weathered_brown_planks PBR."""
    mat = bpy.data.materials.new("LegnoPBR")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1200, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (800, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1600, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1400, 0)
    mp.inputs["Scale"].default_value = (3, 0.25, 3)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    td = tx("Diff", tex_wood["diff"], "sRGB", (-1000, 400))
    ta = tx("AO", tex_wood["ao"], "Non-Color", (-1000, 200))
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
    mx.location = (-600, 300); mx.inputs["Factor"].default_value = 0.6
    nt.links.new(td.outputs["Color"], mx.inputs[6])
    nt.links.new(ta.outputs["Color"], mx.inputs[7])

    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-400, 300)
    hsv.inputs["Saturation"].default_value = 0.90
    hsv.inputs["Value"].default_value = 0.80
    nt.links.new(mx.outputs[2], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    tr = tx("Rough", tex_wood["rough"], "Non-Color", (-1000, 0))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    tn = tx("Nor", tex_wood["nor"], "Non-Color", (-1000, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-600, -200)
    nm.inputs["Strength"].default_value = 1.8
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex_wood["disp"], "Non-Color", (-1000, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-400, -400)
    bmp.inputs["Strength"].default_value = 0.5
    bmp.inputs["Distance"].default_value = 0.012
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def mat_vetro():
    """Vetro architettonico — riflettente, leggermente verdastro, bassa trasmissione."""
    mat = bpy.data.materials.new("Vetro")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.15, 0.20, 0.18, 1.0)
    bsdf.inputs["Transmission Weight"].default_value = 0.6
    bsdf.inputs["IOR"].default_value = 1.52
    bsdf.inputs["Roughness"].default_value = 0.01
    bsdf.inputs["Specular IOR Level"].default_value = 0.8
    bsdf.inputs["Metallic"].default_value = 0.15
    return mat


def mat_simple(name, color, rough=0.9, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


# === GEOMETRIA ===

def build_geometry(mats):
    """Costruisci l'intera casa."""
    print("[GEO] Building walls...")

    # === MURI ===
    wall_specs = [
        ("MuroSud",   W,    T, HG, (W/2, T/2, HG/2)),
        ("MuroNord",  W,    T, HG, (W/2, D-T/2, HG/2)),
        ("MuroOvest", T,    D, HG, (T/2, D/2, HG/2)),
        ("MuroEst",   T,    D, HG, (W-T/2, D/2, HG/2)),
    ]
    walls = {}
    for name, w, d, h, loc in wall_specs:
        obj = make_box(name, w, d, h)
        obj.location = loc
        # Subdiv for true displacement
        mod = obj.modifiers.new("Subdiv", 'SUBSURF')
        mod.subdivision_type = 'SIMPLE'
        mod.levels = 0
        mod.render_levels = 4
        walls[name] = obj

    # Boolean cuts
    cuts = [
        ("MuroSud",   "cut_VetSud",  VET_W, T*4, VET_H, VET_W/2, T/2, VET_H/2 + 0.40),
        ("MuroOvest", "cut_VetOvest", T*4, VET_W, VET_H, T/2, VET_W/2, VET_H/2 + 0.40),
        ("MuroSud",   "cut_FinSud",  1.20, T*4, 1.40, 7.00, T/2, 1.60),
        ("MuroSud",   "cut_Porta",   1.00, T*4, 2.20, 4.50, T/2, 1.10),
        ("MuroOvest", "cut_FinOvest", T*4, 1.00, 1.20, T/2, 6.00, 1.50),
        ("MuroEst",   "cut_FinEst1", T*4, 1.20, 1.40, W-T/2, 3.50, 1.60),
        ("MuroEst",   "cut_FinEst2", T*4, 1.00, 1.20, W-T/2, 7.50, 1.50),
        ("MuroNord",  "cut_FinN1",   0.80, T*4, 1.00, 3.50, D-T/2, 1.70),
        ("MuroNord",  "cut_FinN2",   0.80, T*4, 1.00, 8.00, D-T/2, 1.70),
    ]
    cutters = []
    for target, cname, cw, cd, ch, cx, cy, cz in cuts:
        cutter = boolean_cut(walls[target], cname, cw, cd, ch, cx, cy, cz)
        cutters.append(cutter)

    # Apply modifiers
    for name, wall in walls.items():
        apply_modifiers(wall)
        wall.data.materials.append(mats["Pietra"])

    for c in cutters:
        bpy.data.objects.remove(c, do_unlink=True)

    # === VETRI E PORTA ===
    print("[GEO] Building glazing...")
    glass_specs = [
        ("VetroSWsud",   VET_W, 0.03, VET_H, (VET_W/2, 0.02, VET_H/2 + 0.40)),
        ("VetroSWovest", 0.03, VET_W, VET_H, (0.02, VET_W/2, VET_H/2 + 0.40)),
        ("VetroFinSud",  1.20, 0.03, 1.40, (7.00, 0.02, 1.60)),
        ("VetroFinOvest", 0.03, 1.00, 1.20, (0.02, 6.00, 1.50)),
        ("VetroEst1",    0.03, 1.20, 1.40, (W-0.02, 3.50, 1.60)),
        ("VetroEst2",    0.03, 1.00, 1.20, (W-0.02, 7.50, 1.50)),
        ("VetroNord1",   0.80, 0.03, 1.00, (3.50, D-0.02, 1.70)),
        ("VetroNord2",   0.80, 0.03, 1.00, (8.00, D-0.02, 1.70)),
    ]
    for name, gw, gd, gh, loc in glass_specs:
        obj = make_box(name, gw, gd, gh)
        obj.location = loc
        obj.data.materials.append(mats["Vetro"])

    # Porta — usa legno PBR
    porta = make_box("Porta", 1.00, 0.08, 2.20)
    porta.location = (4.50, 0.04, 1.10)
    porta.data.materials.append(mats["Legno"])

    # === TELAI FINESTRE (legno scuro) ===
    print("[GEO] Building frames...")
    s = 0.06
    frame_specs = [
        (1.32, s, s, (7.00, 0.03, 2.33)),   # Fin sud top
        (1.32, s, s, (7.00, 0.03, 0.87)),   # Fin sud bot
        (s, s, 1.52, (6.37, 0.03, 1.60)),   # Fin sud sx
        (s, s, 1.52, (7.63, 0.03, 1.60)),   # Fin sud dx
        (1.12, s, s, (4.50, 0.03, 2.23)),   # Porta top
        (s, s, 2.32, (3.97, 0.03, 1.10)),   # Porta sx
        (s, s, 2.32, (5.03, 0.03, 1.10)),   # Porta dx
    ]
    for i, (fw, fd, fh, loc) in enumerate(frame_specs):
        obj = make_box(f"Frame_{i}", fw, fd, fh)
        obj.location = loc
        obj.data.materials.append(mats["Legno"])

    # === TETTO ASIMMETRICO ===
    print("[GEO] Building roof...")
    colmo_y = D/2 + CO

    verts_ext = [
        (-SP, -SP, HG), (W+SP, -SP, HG),
        (W+SP, colmo_y, HC), (-SP, colmo_y, HC),
        (-SP, D+SP, HG), (W+SP, D+SP, HG),
    ]
    verts_int = [
        (-SP, -SP, HG-RT), (W+SP, -SP, HG-RT),
        (W+SP, colmo_y, HC-RT), (-SP, colmo_y, HC-RT),
        (-SP, D+SP, HG-RT), (W+SP, D+SP, HG-RT),
    ]
    verts = verts_ext + verts_int
    faces = [
        (0, 1, 2, 3), (3, 2, 5, 4),
        (9, 8, 7, 6), (10, 9, 8, 11),
        (0, 1, 7, 6), (4, 5, 11, 10),
        (0, 3, 9, 6), (1, 2, 8, 7),
        (3, 4, 10, 9), (2, 5, 11, 8),
    ]
    mesh = bpy.data.meshes.new("Tetto")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    tetto = bpy.data.objects.new("Tetto", mesh)
    bpy.context.scene.collection.objects.link(tetto)
    tetto.data.materials.append(mats["Piode"])

    # === TIMPANI (frontoni) ===
    print("[GEO] Building gables...")
    for side_name, x_base, x_off in [("TimpW", 0, T), ("TimpE", W, -T)]:
        verts_t = [
            (x_base, 0, HG), (x_base, D, HG), (x_base, colmo_y, HC),
            (x_base+x_off, 0, HG), (x_base+x_off, D, HG), (x_base+x_off, colmo_y, HC),
        ]
        if x_off > 0:
            faces_t = [(0,1,2), (5,4,3), (0,3,5,2), (1,2,5,4), (0,1,4,3)]
        else:
            faces_t = [(2,1,0), (3,4,5), (2,5,3,0), (4,1,2,5), (3,4,1,0)]
        m = bpy.data.meshes.new(side_name)
        m.from_pydata(verts_t, [], faces_t)
        m.update()
        obj = bpy.data.objects.new(side_name, m)
        bpy.context.scene.collection.objects.link(obj)
        # Subdiv per displacement
        mod = obj.modifiers.new("Sub", 'SUBSURF')
        mod.subdivision_type = 'SIMPLE'; mod.levels = 0; mod.render_levels = 4
        obj.data.materials.append(mats["Pietra"])

    # === TRAVI GRONDA ===
    print("[GEO] Building eave beams...")
    beam_w, beam_d, beam_h = 0.15, 0.80, 0.20
    n_beams = int(W / 0.60) + 1
    for i in range(n_beams):
        x = 0.30 + i * 0.60
        for label, y_pos in [("S", -0.20), ("N", D + 0.20)]:
            b = make_box(f"Trave{label}_{i}", beam_w, beam_d, beam_h)
            b.location = (x, y_pos, HG - beam_h/2)
            b.data.materials.append(mats["Legno"])

    # === COMIGNOLO ===
    base = make_box("Comignolo", 0.60, 0.60, 1.00)
    base.location = (W/2, colmo_y, HC + 0.50)
    base.data.materials.append(mats["Pietra"])
    cap = make_box("ComignoloCap", 0.80, 0.80, 0.10)
    cap.location = (W/2, colmo_y, HC + 1.05)
    cap.data.materials.append(mats["Pietra"])

    # === DAVANZALI ===
    for name, dw, dd, dh, loc in [
        ("DavSud", 1.35, 0.12, 0.05, (7.00, -0.03, 0.87)),
        ("DavOvest", 0.12, 1.10, 0.05, (-0.03, 6.00, 0.87)),
    ]:
        obj = make_box(name, dw, dd, dh)
        obj.location = loc
        obj.data.materials.append(mats["Pietra"])

    # === SOFFIT sotto sporto tetto ===
    print("[GEO] Building soffit...")
    soffit_mat = mat_simple("Soffit", (0.65, 0.55, 0.45, 1), 0.80)
    # Soffit sud
    sof_s = make_box("SoffitS", W + 2*SP, SP + 0.05, 0.04)
    sof_s.location = (W/2, -SP/2, HG - 0.02)
    sof_s.data.materials.append(soffit_mat)
    # Soffit nord
    sof_n = make_box("SoffitN", W + 2*SP, SP + 0.05, 0.04)
    sof_n.location = (W/2, D + SP/2, HG - 0.02)
    sof_n.data.materials.append(soffit_mat)

    # === PANNELLI INTERNI — solo piccole finestre, NON la vetrata SW ===
    print("[GEO] Building interior backplanes...")
    int_mat = mat_simple("Interior", (0.35, 0.33, 0.30, 1), 0.85)
    # Pannello dietro finestra sud (piccola, arretrato 0.4m)
    bp3 = make_box("IntFinS", 1.10, 0.05, 1.30)
    bp3.location = (7.00, T + 0.40, 1.60)
    bp3.data.materials.append(int_mat)

    print("[GEO] Geometry complete.")


def build_environment(mats):
    """Prato, vegetazione, contesto alpino."""
    print("[ENV] Building environment...")
    random.seed(42)

    # Ground (green grass with overlay)
    bpy.ops.mesh.primitive_plane_add(size=80, location=(W/2, D/2, 0))
    ground = bpy.context.active_object; ground.name = "Ground"
    ground.data.materials.append(mats["Prato"])

    # NO bushes — troppo CG, solo sassi sparsi
    for ri in range(18):
        rx = random.uniform(-5, W + 5)
        ry = random.uniform(-5, D + 5)
        # Evita centro casa
        if 0.5 < rx < W - 0.5 and 0.5 < ry < D - 0.5:
            continue
        rr = random.uniform(0.06, 0.18)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rr, location=(rx, ry, rr*0.3))
        rock = bpy.context.active_object; rock.name = f"Rock_{ri}"
        rock.scale = (random.uniform(0.8, 1.5), random.uniform(0.8, 1.5), random.uniform(0.3, 0.6))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        rock.data.materials.append(mats["Pietra"])

    # Multi-lobe trees — thinner trunks, positioned further from house
    tree_data = [
        (-7, 4, 8.0, 2.8, 0.12, mats["FogliaDark"]),
        (W + 8, 3, 9.5, 3.5, 0.15, mats["FogliaMid"]),
        (-5, D + 6, 7.0, 2.5, 0.10, mats["FogliaDark"]),
        (W + 6, D + 4, 6.5, 2.3, 0.09, mats["FogliaLight"]),
        (-10, -5, 8.5, 3.0, 0.13, mats["FogliaMid"]),
    ]
    for ti, (tx_, ty, th, tcr, tr, cmat) in enumerate(tree_data):
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=tr,
            radius2=tr*0.4, depth=th, location=(tx_, ty, th/2))
        bpy.context.active_object.name = f"Trunk_{ti}"
        bpy.context.active_object.data.materials.append(mats["Corteccia"])

        n_lobes = random.randint(5, 8)
        for li in range(n_lobes):
            lr = tcr * random.uniform(0.40, 0.80)
            lx = tx_ + random.uniform(-tcr*0.5, tcr*0.5)
            ly = ty + random.uniform(-tcr*0.5, tcr*0.5)
            lz = th * 0.6 + random.uniform(0, tcr*0.8)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=lr, location=(lx, ly, lz))
            c = bpy.context.active_object; c.name = f"Lobe_{ti}_{li}"
            c.scale[2] = random.uniform(0.55, 0.80)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.shade_smooth()
            dm = c.modifiers.new("D", 'DISPLACE')
            nt = bpy.data.textures.new(f"TN_{ti}_{li}", 'CLOUDS')
            nt.noise_scale = 0.30; nt.noise_depth = 6
            dm.texture = nt; dm.strength = 0.30 * lr
            c.data.materials.append(cmat)

    print("[ENV] Environment complete.")


# === SETUP ===

def setup_hdri():
    """HDRI alpino."""
    world = bpy.data.worlds.new("World"); bpy.context.scene.world = world
    world.use_nodes = True
    wnt = world.node_tree; wnt.nodes.clear()
    bg = wnt.nodes.new("ShaderNodeBackground"); bg.location = (200, 0)
    env = wnt.nodes.new("ShaderNodeTexEnvironment"); env.location = (-400, 0)
    env.image = bpy.data.images.load(HDRI_PATH)
    mpw = wnt.nodes.new("ShaderNodeMapping"); mpw.location = (-600, 0)
    tcw = wnt.nodes.new("ShaderNodeTexCoord"); tcw.location = (-800, 0)
    outw = wnt.nodes.new("ShaderNodeOutputWorld"); outw.location = (400, 0)
    bg.inputs["Strength"].default_value = 1.2
    mpw.inputs["Rotation"].default_value = (0, 0, math.radians(40))
    wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
    wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
    wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
    wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])


def setup_lighting():
    """Overcast alpine lighting matching the photo."""
    # Sun (overcast, diffuse)
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.active_object; sun.name = "Sun"
    sun.data.energy = 2.5
    sun.data.angle = math.radians(3.0)  # Soft, overcast
    sun.rotation_euler = (math.radians(45), math.radians(10), math.radians(-25))
    sun.data.color = (0.95, 0.93, 0.90)  # Slightly warm overcast

    # Fill
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    fill = bpy.context.active_object; fill.name = "Fill"
    fill.data.energy = 0.8
    fill.data.angle = math.radians(20)
    fill.rotation_euler = (math.radians(55), 0, math.radians(40))
    fill.data.color = (0.88, 0.90, 0.95)


def setup_camera():
    """Camera che replica il punto di vista di foto1 (prato sud, vista 3/4 con angolo SW in primo piano)."""
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Posizione: dal prato sud-ovest per mostrare angolo vetrata SW
    cam_obj.location = (-4.0, -10.0, 1.70)
    target = Vector((W * 0.35, D * 0.35, 2.2))
    direction = target - Vector(cam_obj.location)
    rot = direction.to_track_quat('-Z', 'Y').to_euler()
    cam_obj.rotation_euler = rot

    cam_data.lens = 32
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 15.0
    cam_data.dof.aperture_fstop = 5.6
    cam_data.clip_end = 500


def setup_render(transparent=False):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 512
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_depth = '16'
    scene.render.film_transparent = transparent
    if transparent:
        scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - Medium Contrast'
    except:
        scene.view_settings.look = 'AgX - Base Contrast'


# === PRATO (green grass) ===
def mat_prato():
    """Green grass material (forced green, learned from training)."""
    from pathlib import Path as P
    grass_diff = str(PROJECT_DIR / "chain" / "training" / "archviz_workflow" / "textures" / "grass_path_2_diff_2k.jpg")
    grass_nor = str(PROJECT_DIR / "chain" / "training" / "archviz_workflow" / "textures" / "grass_path_2_nor_gl_2k.jpg")

    mat = bpy.data.materials.new("Prato")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (1200, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-2000, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1800, 0)
    mp.inputs["Scale"].default_value = (7, 7, 7)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    # Load grass texture if available, otherwise use pure color
    try:
        td = nt.nodes.new("ShaderNodeTexImage"); td.location = (-1400, 500)
        td.image = bpy.data.images.load(grass_diff)
        td.projection = 'BOX'; td.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], td.inputs["Vector"])

        # Green overlay
        green = nt.nodes.new("ShaderNodeRGB"); green.location = (-1400, 300)
        green.outputs[0].default_value = (0.10, 0.25, 0.06, 1.0)
        mix_g = nt.nodes.new("ShaderNodeMix")
        mix_g.data_type = 'RGBA'; mix_g.blend_type = 'OVERLAY'
        mix_g.location = (-1000, 500); mix_g.inputs["Factor"].default_value = 0.65
        nt.links.new(td.outputs["Color"], mix_g.inputs[6])
        nt.links.new(green.outputs[0], mix_g.inputs[7])

        hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-800, 500)
        hsv.inputs["Saturation"].default_value = 0.90
        hsv.inputs["Value"].default_value = 0.85
        nt.links.new(mix_g.outputs[2], hsv.inputs["Color"])
        nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

        tn = nt.nodes.new("ShaderNodeTexImage"); tn.location = (-1400, -200)
        tn.image = bpy.data.images.load(grass_nor)
        tn.image.colorspace_settings.name = 'Non-Color'
        tn.projection = 'BOX'; tn.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], tn.inputs["Vector"])
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-1000, -200)
        nm.inputs["Strength"].default_value = 0.8
        nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    except Exception:
        bsdf.inputs["Base Color"].default_value = (0.12, 0.22, 0.06, 1.0)

    bsdf.inputs["Roughness"].default_value = 0.85
    return mat


# === COMPOSITING ===
def composite_on_photo(model_path, photo_path, output_path):
    """Alpha-over compositing: model RGBA on photo RGB."""
    print(f"[COMP] Compositing model on photo...")
    foto = bpy.data.images.load(str(photo_path))
    model = bpy.data.images.load(model_path)
    fw, fh = foto.size; mw, mh = model.size
    print(f"  Photo: {fw}x{fh}, Model: {mw}x{mh}")
    if mw != fw or mh != fh:
        model.scale(fw, fh)
    foto_px = list(foto.pixels)
    mod_px = list(model.pixels)
    if len(foto_px) == fw * fh * 3:
        rgba = []
        for i in range(fw * fh):
            idx = i * 3
            rgba.extend([foto_px[idx], foto_px[idx+1], foto_px[idx+2], 1.0])
        foto_px = rgba
    res = [0.0] * (fw * fh * 4)
    for i in range(fw * fh):
        idx = i * 4
        a = mod_px[idx + 3]
        res[idx] = mod_px[idx]*a + foto_px[idx]*(1-a)
        res[idx+1] = mod_px[idx+1]*a + foto_px[idx+1]*(1-a)
        res[idx+2] = mod_px[idx+2]*a + foto_px[idx+2]*(1-a)
        res[idx+3] = 1.0
    result = bpy.data.images.new("Comp", width=fw, height=fh)
    result.pixels = res
    result.filepath_raw = output_path
    result.file_format = 'PNG'
    result.save()
    print(f"[COMP] Saved: {output_path}")


# === MAIN ===
def main():
    start = time.time()
    print("=" * 60)
    print("Ca' del Papa — Render Fotorealistico PBR")
    print("=" * 60)

    clear_scene()

    # Materials
    print("\n[MAT] Creating PBR materials...")
    mats = {
        "Pietra": mat_pietra_pbr(),
        "Piode": mat_piode_pbr(),
        "Legno": mat_legno_pbr(),
        "Vetro": mat_vetro(),
        "Porta": mat_simple("Porta", (0.06, 0.04, 0.02, 1), 0.55),
        "Prato": mat_prato(),
        "FogliaDark": mat_simple("FD", (0.015, 0.06, 0.01, 1), 0.92),
        "FogliaMid": mat_simple("FM", (0.03, 0.10, 0.02, 1), 0.92),
        "FogliaLight": mat_simple("FL", (0.05, 0.14, 0.03, 1), 0.92),
        "Corteccia": mat_simple("Bark", (0.08, 0.05, 0.02, 1), 0.95),
    }

    # Geometry
    build_geometry(mats)
    build_environment(mats)

    # Setup
    setup_hdri()
    setup_lighting()
    setup_camera()

    # RENDER 1: Standalone (with HDRI background)
    print("\n[RENDER] Standalone render (512 samples FINALE)...")
    setup_render(transparent=False)
    bpy.context.scene.render.filepath = RENDER_STANDALONE
    bpy.ops.render.render(write_still=True)
    t1 = time.time() - start
    print(f"[RENDER] Standalone done in {t1:.0f}s: {RENDER_STANDALONE}")

    # RENDER 2: Transparent for compositing
    if FOTO_SORGENTE.exists():
        print("\n[RENDER] Transparent render for compositing...")
        setup_render(transparent=True)
        bpy.context.scene.render.filepath = RENDER_MODEL
        bpy.ops.render.render(write_still=True)
        t2 = time.time() - start
        print(f"[RENDER] Transparent done in {t2:.0f}s")

        # Composite
        composite_on_photo(RENDER_MODEL, FOTO_SORGENTE, RENDER_FINALE)
    else:
        print(f"[WARN] Foto sorgente non trovata: {FOTO_SORGENTE}")

    total = time.time() - start
    print(f"\n{'='*60}")
    print(f"Ca' del Papa — RENDER FINALE COMPLETO in {total:.0f}s")
    print(f"Standalone: {RENDER_STANDALONE}")
    if FOTO_SORGENTE.exists():
        print(f"Fotoinserimento: {RENDER_FINALE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
