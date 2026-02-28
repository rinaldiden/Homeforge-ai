"""
ARCHVIZ WORKFLOW — ITERAZIONE 5 (FINAL)
Fixes from iter 4:
- Ground: override grass to be truly green (stronger hue shift + sat)
- Slightly closer camera for better composition
- Warmer overall tone
- Post-processing via PIL: vignette, warm grade, subtle sharpening
"""
import bpy
import os
import math
import random
from mathutils import Vector

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(BASE, "textures")
HDRI_DIR = os.path.join(BASE, "hdri")
OUT_DIR = BASE
os.makedirs(OUT_DIR, exist_ok=True)

hdri_path = os.path.join(HDRI_DIR, "kloofendal_48d_partly_cloudy_2k.hdr")

tex_concrete = {
    "diff": os.path.join(TEX_DIR, "concrete_wall_008_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "concrete_wall_008_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "concrete_wall_008_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "concrete_wall_008_disp_2k.jpg"),
}
tex_wood = {
    "diff": os.path.join(TEX_DIR, "wood_planks_grey_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "wood_planks_grey_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "wood_planks_grey_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "wood_planks_grey_disp_2k.jpg"),
}
tex_grass = {
    "diff": os.path.join(TEX_DIR, "grass_path_2_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "grass_path_2_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "grass_path_2_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "grass_path_2_disp_2k.jpg"),
}
tex_paving = {
    "diff": os.path.join(TEX_DIR, "concrete_floor_02_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "concrete_floor_02_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "concrete_floor_02_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "concrete_floor_02_disp_2k.jpg"),
}


# ====== MATERIAL FUNCTIONS ======

def make_pbr(name, tex, scale=(1,1,1), sat=1.0, val=1.0, contrast=0.0,
             nstr=1.5, bstr=0.3, bdist=0.01, rough_offset=0.0, hue=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (1000, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1800, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1600, 0)
    mp.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    td = tx("Diff", tex["diff"], "sRGB", (-1200, 500))
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-800, 500)
    bc.inputs["Contrast"].default_value = contrast
    nt.links.new(td.outputs["Color"], bc.inputs["Color"])
    hsv_n = nt.nodes.new("ShaderNodeHueSaturation"); hsv_n.location = (-600, 500)
    hsv_n.inputs["Hue"].default_value = hue
    hsv_n.inputs["Saturation"].default_value = sat
    hsv_n.inputs["Value"].default_value = val
    nt.links.new(bc.outputs["Color"], hsv_n.inputs["Color"])
    nt.links.new(hsv_n.outputs["Color"], bsdf.inputs["Base Color"])

    tr = tx("Rough", tex["rough"], "Non-Color", (-1200, 100))
    if rough_offset != 0.0:
        rm = nt.nodes.new("ShaderNodeMath"); rm.location = (-800, 100)
        rm.operation = 'ADD'; rm.inputs[1].default_value = rough_offset; rm.use_clamp = True
        nt.links.new(tr.outputs["Color"], rm.inputs[0])
        nt.links.new(rm.outputs["Value"], bsdf.inputs["Roughness"])
    else:
        nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    tn = tx("Nor", tex["nor"], "Non-Color", (-1200, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-800, -200)
    nm.inputs["Strength"].default_value = nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-1200, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-600, -350)
    bmp.inputs["Strength"].default_value = bstr
    bmp.inputs["Distance"].default_value = bdist
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])

    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-1200, -700)
    noise.inputs["Scale"].default_value = 55.0; noise.inputs["Detail"].default_value = 7.0
    nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])
    bmp2 = nt.nodes.new("ShaderNodeBump"); bmp2.location = (-400, -400)
    bmp2.inputs["Strength"].default_value = 0.04; bmp2.inputs["Distance"].default_value = 0.004
    nt.links.new(noise.outputs["Fac"], bmp2.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], bmp2.inputs["Normal"])
    nt.links.new(bmp2.outputs["Normal"], bsdf.inputs["Normal"])
    mat.displacement_method = 'BUMP'
    return mat


def make_green_grass(name, tex):
    """Grass material that forces green tint via Mix node overlay."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (1200, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-2000, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1800, 0)
    mp.inputs["Scale"].default_value = (7, 7, 7)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    td = tx("Diff", tex["diff"], "sRGB", (-1400, 500))

    # Force green by mixing texture with green tint
    green_tint = nt.nodes.new("ShaderNodeRGB"); green_tint.location = (-1400, 300)
    green_tint.outputs[0].default_value = (0.12, 0.28, 0.08, 1.0)

    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = 'RGBA'; mix.blend_type = 'OVERLAY'
    mix.location = (-1000, 500); mix.inputs["Factor"].default_value = 0.65
    nt.links.new(td.outputs["Color"], mix.inputs[6])
    nt.links.new(green_tint.outputs[0], mix.inputs[7])

    # Variation with noise
    noise_v = nt.nodes.new("ShaderNodeTexNoise"); noise_v.location = (-1400, 100)
    noise_v.inputs["Scale"].default_value = 2.0
    noise_v.inputs["Detail"].default_value = 5.0
    nt.links.new(tc.outputs["Generated"], noise_v.inputs["Vector"])

    # Second green shade for variety
    green2 = nt.nodes.new("ShaderNodeRGB"); green2.location = (-1000, 200)
    green2.outputs[0].default_value = (0.08, 0.22, 0.05, 1.0)

    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location = (-1000, 100)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.65
    nt.links.new(noise_v.outputs["Fac"], ramp.inputs["Fac"])

    mix2 = nt.nodes.new("ShaderNodeMix")
    mix2.data_type = 'RGBA'; mix2.location = (-600, 500)
    nt.links.new(ramp.outputs["Color"], mix2.inputs["Factor"])
    nt.links.new(mix.outputs[2], mix2.inputs[6])
    nt.links.new(green2.outputs[0], mix2.inputs[7])

    # HSV final adjustment
    hsv_n = nt.nodes.new("ShaderNodeHueSaturation"); hsv_n.location = (-400, 500)
    hsv_n.inputs["Saturation"].default_value = 1.30
    hsv_n.inputs["Value"].default_value = 1.05
    nt.links.new(mix2.outputs[2], hsv_n.inputs["Color"])
    nt.links.new(hsv_n.outputs["Color"], bsdf.inputs["Base Color"])

    bsdf.inputs["Roughness"].default_value = 0.85

    # Normal
    tn = tx("Nor", tex["nor"], "Non-Color", (-1400, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-1000, -200)
    nm.inputs["Strength"].default_value = 0.8
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def make_weathered_concrete(name, tex):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (1000, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-2000, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1800, 0)
    mp.inputs["Scale"].default_value = (1.5, 1.5, 1.5)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    td = tx("Diff", tex["diff"], "sRGB", (-1400, 500))
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-1000, 500)
    bc.inputs["Contrast"].default_value = 0.22
    nt.links.new(td.outputs["Color"], bc.inputs["Color"])
    hsv_n = nt.nodes.new("ShaderNodeHueSaturation"); hsv_n.location = (-800, 500)
    hsv_n.inputs["Saturation"].default_value = 0.72; hsv_n.inputs["Value"].default_value = 0.83
    nt.links.new(bc.outputs["Color"], hsv_n.inputs["Color"])

    # Weathering gradient
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-1400, -800)
    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location = (-1200, -800)
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.5, 0.5, 0.5, 1)
    ramp.color_ramp.elements[1].position = 0.10; ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    el = ramp.color_ramp.elements.new(0.93); el.color = (0.78, 0.78, 0.78, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])

    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.location = (-600, 500); mix.inputs["Factor"].default_value = 1.0
    nt.links.new(hsv_n.outputs["Color"], mix.inputs[6])
    nt.links.new(ramp.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])

    tr = tx("Rough", tex["rough"], "Non-Color", (-1400, 100))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    tn = tx("Nor", tex["nor"], "Non-Color", (-1400, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-1000, -200)
    nm.inputs["Strength"].default_value = 3.0
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-1400, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-800, -350)
    bmp.inputs["Strength"].default_value = 0.55; bmp.inputs["Distance"].default_value = 0.025
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])

    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-1400, -700)
    noise.inputs["Scale"].default_value = 45.0; noise.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])
    bmp2 = nt.nodes.new("ShaderNodeBump"); bmp2.location = (-600, -400)
    bmp2.inputs["Strength"].default_value = 0.05; bmp2.inputs["Distance"].default_value = 0.005
    nt.links.new(noise.outputs["Fac"], bmp2.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], bmp2.inputs["Normal"])
    nt.links.new(bmp2.outputs["Normal"], bsdf.inputs["Normal"])
    mat.displacement_method = 'BUMP'
    return mat


def make_glass(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.68, 0.76, 0.72, 1.0)
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.52
    bsdf.inputs["Roughness"].default_value = 0.003
    bsdf.inputs["Specular IOR Level"].default_value = 0.5
    return mat


def make_simple(name, color, roughness=0.9, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def make_foliage(name, base_color, roughness=0.92):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Subsurface Weight"].default_value = 0.12
    return mat


# ====== SCENE ======
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# HDRI
world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
wnt = world.node_tree; wnt.nodes.clear()
bg = wnt.nodes.new("ShaderNodeBackground"); bg.location = (200, 0)
env = wnt.nodes.new("ShaderNodeTexEnvironment"); env.location = (-400, 0)
env.image = bpy.data.images.load(hdri_path)
mpw = wnt.nodes.new("ShaderNodeMapping"); mpw.location = (-600, 0)
tcw = wnt.nodes.new("ShaderNodeTexCoord"); tcw.location = (-800, 0)
outw = wnt.nodes.new("ShaderNodeOutputWorld"); outw.location = (400, 0)
bg.inputs["Strength"].default_value = 1.0
mpw.inputs["Rotation"].default_value = (0, 0, math.radians(155))
wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])

# Materials
mat_concrete = make_weathered_concrete("ConcreteW", tex_concrete)
mat_wood_clad = make_pbr("WoodClad", tex_wood,
    scale=(2, 0.6, 2), sat=0.78, val=0.72, contrast=0.18,
    nstr=2.5, bstr=0.5, bdist=0.018, hue=0.50)
mat_grass = make_green_grass("GreenGrass", tex_grass)
mat_paving = make_pbr("Paving", tex_paving,
    scale=(2.5, 2.5, 2.5), sat=0.68, val=0.80, contrast=0.14,
    nstr=2.0, bstr=0.35, bdist=0.015)
mat_glass = make_glass("Glass")
mat_roof = make_simple("Roof", (0.04, 0.04, 0.04, 1), roughness=0.60)
mat_frame = make_simple("Frame", (0.02, 0.02, 0.02, 1), roughness=0.28, metallic=0.92)
mat_slab = make_simple("Slab", (0.52, 0.50, 0.47, 1), roughness=0.75)
mat_soffit = make_simple("Soffit", (0.80, 0.78, 0.76, 1), roughness=0.85)
mat_gravel = make_simple("Gravel", (0.45, 0.42, 0.38, 1), roughness=0.95)
mat_fd = make_foliage("FD", (0.02, 0.08, 0.015, 1))
mat_fm = make_foliage("FM", (0.05, 0.14, 0.03, 1))
mat_fl = make_foliage("FL", (0.08, 0.20, 0.05, 1))
mat_fh = make_foliage("FH", (0.03, 0.10, 0.02, 1))
mat_bark = make_simple("Bark", (0.08, 0.05, 0.02, 1), roughness=0.95)

# ====== BUILDING ======
BX = 12.0; BY = 8.0; WH = 3.0; WT = 0.30; ROOF_T = 0.25; OV = 1.0

# Ground (green grass!)
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
bpy.context.active_object.name = "Ground"
bpy.context.active_object.data.materials.append(mat_grass)

# Plinth
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.10))
p = bpy.context.active_object; p.name = "Plinth"
p.scale = (BX + 0.15, BY + 0.15, 0.20)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
p.data.materials.append(mat_slab)

# Paving
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5, -BY/2 - 2.5, 0.012))
pv = bpy.context.active_object; pv.name = "Paving"
pv.scale = (4.5, 4.5, 0.025)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
pv.data.materials.append(mat_paving)

# Gravel borders
for gx, gy, gsx, gsy in [(-0.5, -BY/2 - 5.0, 5.0, 0.5), (-3.25, -BY/2 - 2.5, 0.5, 4.5), (2.25, -BY/2 - 2.5, 0.5, 4.5)]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(gx, gy, 0.008))
    g = bpy.context.active_object; g.name = "Gravel"; g.scale = (gsx, gsy, 0.015)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    g.data.materials.append(mat_gravel)

# Walls
for loc, sc, mat, nm in [
    ((0, BY/2 - WT/2, WH/2 + 0.20), (BX, WT, WH), mat_concrete, "WN"),
    ((-BX/2 + WT/2, 0, WH/2 + 0.20), (WT, BY - 2*WT, WH), mat_concrete, "WW"),
    ((BX/2 - WT/2, 0, WH/2 + 0.20), (WT, BY - 2*WT, WH), mat_wood_clad, "WE"),
    ((-BX/2 + 1.5, -BY/2 + WT/2, WH/2 + 0.20), (3.0, WT, WH), mat_concrete, "WSL"),
    ((BX/2 - 1.5, -BY/2 + WT/2, WH/2 + 0.20), (3.0, WT, WH), mat_wood_clad, "WSR"),
    ((0, -BY/2 + WT/2, WH - 0.12 + 0.20), (6.0, WT, 0.25), mat_concrete, "Lint"),
]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    w = bpy.context.active_object; w.name = nm; w.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    w.data.materials.append(mat)

# Recess
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT - 0.04, WH/2 - 0.12 + 0.20))
r = bpy.context.active_object; r.name = "Recess"; r.scale = (5.9, 0.08, 2.6)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
r.data.materials.append(mat_slab)

# Glass
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + 0.03, WH/2 - 0.12 + 0.20))
gl = bpy.context.active_object; gl.name = "Glass"; gl.scale = (5.8, 0.015, 2.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
gl.data.materials.append(mat_glass)

# Frames
fw = 0.032
for fy, fs in [(0.22, (6.0, 0.05, fw)), (WH - 0.25 + 0.20, (6.0, 0.05, fw))]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + 0.03, fy))
    f = bpy.context.active_object; f.name = "Fr"; f.scale = fs
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    f.data.materials.append(mat_frame)
for fx in [-2.0, 0, 2.0]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, -BY/2 + 0.03, WH/2 + 0.08))
    f = bpy.context.active_object; f.name = "FrV"; f.scale = (fw, 0.05, 2.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    f.data.materials.append(mat_frame)

# Side window
bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - 0.01, -1.5, WH/2 + 0.20))
sw = bpy.context.active_object; sw.name = "SW"; sw.scale = (0.015, 1.5, 1.8)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
sw.data.materials.append(mat_glass)

# Roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, WH + ROOF_T/2 + 0.20))
rf = bpy.context.active_object; rf.name = "Roof"; rf.scale = (BX + 2*OV, BY + 2*OV, ROOF_T)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
rf.data.materials.append(mat_roof)

# Soffit + Fascia
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - OV/2, WH + 0.19))
sf = bpy.context.active_object; sf.name = "Soffit"; sf.scale = (BX + 2*OV, OV + 0.2, 0.015)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
sf.data.materials.append(mat_soffit)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - OV, WH + ROOF_T/2 + 0.20))
fa = bpy.context.active_object; fa.name = "Fascia"; fa.scale = (BX + 2*OV, 0.01, ROOF_T + 0.015)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fa.data.materials.append(mat_frame)

# Steps
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - 0.6 - i*0.40, 0.15 - i*0.05))
    s = bpy.context.active_object; s.name = f"Step{i}"; s.scale = (2.0, 0.40, 0.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    s.data.materials.append(mat_slab)


# ====== VEGETATION ======
random.seed(42)

def add_bush(name, pos, scale, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=scale, location=pos)
    b = bpy.context.active_object; b.name = name
    b.scale = (1 + random.uniform(-0.2, 0.2), 1 + random.uniform(-0.2, 0.2), 0.45 + random.uniform(-0.1, 0.1))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    dm = b.modifiers.new("D", 'DISPLACE')
    nt = bpy.data.textures.new(f"N_{name}", 'CLOUDS')
    nt.noise_scale = 0.20 + random.uniform(-0.08, 0.08); nt.noise_depth = 5
    dm.texture = nt; dm.strength = 0.20 * scale; dm.mid_level = 0.5
    b.data.materials.append(mat)

def add_multi_tree(name, base_pos, height, crown_r, trunk_r, crown_mat):
    bx, by = base_pos
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=trunk_r * 1.3,
        radius2=trunk_r * 0.6, depth=height, location=(bx, by, height/2))
    bpy.context.active_object.name = f"T_{name}"
    bpy.context.active_object.data.materials.append(mat_bark)
    n_lobes = random.randint(5, 7)
    for li in range(n_lobes):
        lr = crown_r * random.uniform(0.45, 0.85)
        lx = bx + random.uniform(-crown_r * 0.6, crown_r * 0.6)
        ly = by + random.uniform(-crown_r * 0.6, crown_r * 0.6)
        lz = height + random.uniform(-crown_r * 0.3, crown_r * 0.5)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=lr, location=(lx, ly, lz))
        c = bpy.context.active_object; c.name = f"L_{name}_{li}"
        c.scale[2] = random.uniform(0.6, 0.85)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        dm = c.modifiers.new("D", 'DISPLACE')
        nt = bpy.data.textures.new(f"TN_{name}_{li}", 'CLOUDS')
        nt.noise_scale = 0.35; nt.noise_depth = 5
        dm.texture = nt; dm.strength = 0.25 * lr
        c.data.materials.append(crown_mat)

# Bushes
add_bush("BL1", (-BX/2 - 1.5, -2, 0.45), 0.80, mat_fd)
add_bush("BL2", (-BX/2 - 2.2, -0.5, 0.4), 0.60, mat_fm)
add_bush("BL3", (-BX/2 - 1.6, 1.0, 0.55), 0.95, mat_fd)
add_bush("BL4", (-BX/2 - 2.4, 2.5, 0.5), 0.85, mat_fl)
add_bush("BL5", (-BX/2 - 1.0, 3.5, 0.35), 0.65, mat_fm)
add_bush("BR1", (BX/2 + 1.4, -2, 0.40), 0.70, mat_fm)
add_bush("BR2", (BX/2 + 2.0, 0.5, 0.50), 0.90, mat_fd)
add_bush("BR3", (BX/2 + 1.6, 3, 0.45), 0.75, mat_fl)
add_bush("BF1", (-1.8, -BY/2 - 3.5, 0.30), 0.50, mat_fl)
add_bush("BF2", (3.5, -BY/2 - 3, 0.35), 0.60, mat_fm)
for hi in range(9):
    add_bush(f"H{hi}", (-BX/2 + 0.5 + hi * 1.5, BY/2 + 1.8, 0.55), 0.80, mat_fh)

# Trees
add_multi_tree("T0", (-BX/2 - 6, -1), 7.5, 3.5, 0.22, mat_fd)
add_multi_tree("T1", (BX/2 + 8, -5), 9.0, 4.5, 0.28, mat_fm)
add_multi_tree("T2", (-6, BY/2 + 7), 7.0, 3.2, 0.20, mat_fd)
add_multi_tree("T3", (BX/2 + 5, BY/2 + 4), 6.5, 3.0, 0.18, mat_fl)
add_multi_tree("T4", (-BX/2 - 10, 4), 10.0, 5.0, 0.30, mat_fm)
add_multi_tree("T5", (BX/2 + 12, 3), 8.5, 4.0, 0.25, mat_fd)
add_multi_tree("T6", (-10, -BY/2 - 8), 8.0, 3.8, 0.24, mat_fl)
add_multi_tree("T7", (8, -BY/2 - 6), 7.0, 3.2, 0.20, mat_fd)


# ====== LIGHTING ======
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object; sun.name = "Sun"
sun.data.energy = 4.0; sun.data.angle = math.radians(0.8)
sun.rotation_euler = (math.radians(35), math.radians(8), math.radians(-55))
sun.data.color = (1.0, 0.92, 0.78)

bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
fill = bpy.context.active_object; fill.name = "Fill"
fill.data.energy = 0.5; fill.data.angle = math.radians(15)
fill.rotation_euler = (math.radians(60), 0, math.radians(30))
fill.data.color = (0.85, 0.90, 1.0)


# ====== CAMERA ======
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_obj.location = (-10, -14, 1.55)
target = Vector((0.5, 0, 1.6))
direction = target - Vector(cam_obj.location)
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam_obj.rotation_euler = rot

cam_data.lens = 30
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 16.0
cam_data.dof.aperture_fstop = 5.6
cam_data.clip_end = 600


# ====== RENDER SETTINGS ======
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '16'

scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium Contrast'
except:
    scene.view_settings.look = 'AgX - Base Contrast'

out_path = os.path.join(OUT_DIR, "iterazione_5.png")
scene.render.filepath = out_path

print("\n=== ARCHVIZ ITER 5 (FINAL) — Green grass, multi-lobe trees, golden hour ===")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {out_path} ===")
