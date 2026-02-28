"""
ARCHVIZ WORKFLOW — ITERAZIONE 3
Major improvements:
- Wider camera, showing full building + garden
- Much better vegetation (varied greens, larger trees, layered bushes)
- Stronger grass ground visibility
- More dramatic golden-hour lighting (lower sun)
- Removed planter box (too distracting)
- Better color grading and atmosphere
- Added water/rain stains on concrete for weathering
- 512 samples for cleaner result
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

# Texture sets
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
             nstr=1.5, bstr=0.3, bdist=0.01, rough_offset=0.0,
             micro_noise=True, hue=0.5):
    """Full PBR material."""
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

    td = tx("Diffuse", tex["diff"], "sRGB", (-1200, 500))

    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-800, 500)
    bc.inputs["Contrast"].default_value = contrast
    nt.links.new(td.outputs["Color"], bc.inputs["Color"])

    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-600, 500)
    hsv.inputs["Hue"].default_value = hue
    hsv.inputs["Saturation"].default_value = sat
    hsv.inputs["Value"].default_value = val
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    tr = tx("Rough", tex["rough"], "Non-Color", (-1200, 100))
    if rough_offset != 0.0:
        rmath = nt.nodes.new("ShaderNodeMath"); rmath.location = (-800, 100)
        rmath.operation = 'ADD'; rmath.inputs[1].default_value = rough_offset
        rmath.use_clamp = True
        nt.links.new(tr.outputs["Color"], rmath.inputs[0])
        nt.links.new(rmath.outputs["Value"], bsdf.inputs["Roughness"])
    else:
        nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    tn = tx("Normal", tex["nor"], "Non-Color", (-1200, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-800, -200)
    nm.inputs["Strength"].default_value = nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-1200, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-600, -350)
    bmp.inputs["Strength"].default_value = bstr
    bmp.inputs["Distance"].default_value = bdist
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])

    if micro_noise:
        noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-1200, -700)
        noise.inputs["Scale"].default_value = 60.0
        noise.inputs["Detail"].default_value = 8.0
        noise.inputs["Roughness"].default_value = 0.65
        nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])

        bmp2 = nt.nodes.new("ShaderNodeBump"); bmp2.location = (-400, -400)
        bmp2.inputs["Strength"].default_value = 0.05
        bmp2.inputs["Distance"].default_value = 0.005
        nt.links.new(noise.outputs["Fac"], bmp2.inputs["Height"])
        nt.links.new(bmp.outputs["Normal"], bmp2.inputs["Normal"])
        nt.links.new(bmp2.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def make_weathered_concrete(name, tex, scale=(1.5,1.5,1.5)):
    """Concrete with rain stain darkening at top/bottom edges."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (1000, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-2000, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1800, 0)
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

    td = tx("Diff", tex["diff"], "sRGB", (-1400, 500))

    # Brightness/contrast
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-1000, 500)
    bc.inputs["Contrast"].default_value = 0.18
    nt.links.new(td.outputs["Color"], bc.inputs["Color"])

    # HSV
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-800, 500)
    hsv.inputs["Saturation"].default_value = 0.80
    hsv.inputs["Value"].default_value = 0.88
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])

    # Weathering: darken via vertical gradient (rain stains at edges)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-1400, -800)
    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])

    # Use Z coordinate for vertical weathering
    ramp_w = nt.nodes.new("ShaderNodeValToRGB"); ramp_w.location = (-1200, -800)
    ramp_w.color_ramp.elements[0].position = 0.0
    ramp_w.color_ramp.elements[0].color = (0.6, 0.6, 0.6, 1)  # Dark at bottom
    ramp_w.color_ramp.elements[1].position = 0.15
    ramp_w.color_ramp.elements[1].color = (1, 1, 1, 1)  # Clean center
    # Add element for top darkening
    el = ramp_w.color_ramp.elements.new(0.9)
    el.color = (0.85, 0.85, 0.85, 1)
    nt.links.new(sep.outputs["Z"], ramp_w.inputs["Fac"])

    # Multiply base color by weathering
    mix_w = nt.nodes.new("ShaderNodeMix")
    mix_w.data_type = 'RGBA'; mix_w.blend_type = 'MULTIPLY'
    mix_w.location = (-600, 500); mix_w.inputs["Factor"].default_value = 1.0
    nt.links.new(hsv.outputs["Color"], mix_w.inputs[6])
    nt.links.new(ramp_w.outputs["Color"], mix_w.inputs[7])
    nt.links.new(mix_w.outputs[2], bsdf.inputs["Base Color"])

    # Roughness
    tr = tx("Rough", tex["rough"], "Non-Color", (-1400, 100))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # Normal + Bump
    tn = tx("Nor", tex["nor"], "Non-Color", (-1400, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-1000, -200)
    nm.inputs["Strength"].default_value = 2.8
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-1400, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-800, -350)
    bmp.inputs["Strength"].default_value = 0.5
    bmp.inputs["Distance"].default_value = 0.02
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])

    # Micro noise
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-1400, -700)
    noise.inputs["Scale"].default_value = 50.0
    noise.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])
    bmp2 = nt.nodes.new("ShaderNodeBump"); bmp2.location = (-600, -400)
    bmp2.inputs["Strength"].default_value = 0.04
    bmp2.inputs["Distance"].default_value = 0.004
    nt.links.new(noise.outputs["Fac"], bmp2.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], bmp2.inputs["Normal"])
    nt.links.new(bmp2.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def make_glass(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.72, 0.80, 0.76, 1.0)
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.52
    bsdf.inputs["Roughness"].default_value = 0.005
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


# ====== SCENE SETUP ======
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ====== HDRI WORLD ======
world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
wnt = world.node_tree; wnt.nodes.clear()

bg = wnt.nodes.new("ShaderNodeBackground"); bg.location = (200, 0)
env = wnt.nodes.new("ShaderNodeTexEnvironment"); env.location = (-400, 0)
env.image = bpy.data.images.load(hdri_path)
mpw = wnt.nodes.new("ShaderNodeMapping"); mpw.location = (-600, 0)
tcw = wnt.nodes.new("ShaderNodeTexCoord"); tcw.location = (-800, 0)
outw = wnt.nodes.new("ShaderNodeOutputWorld"); outw.location = (400, 0)

bg.inputs["Strength"].default_value = 1.2  # Slightly dimmer HDRI, let sun dominate
mpw.inputs["Rotation"].default_value = (0, 0, math.radians(160))

wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])


# ====== MATERIALS ======
mat_concrete = make_weathered_concrete("ConcreteW", tex_concrete)

mat_wood_clad = make_pbr("WoodCladding", tex_wood,
    scale=(2, 0.7, 2), sat=0.80, val=0.75, contrast=0.15,
    nstr=2.2, bstr=0.45, bdist=0.015, hue=0.50)

mat_grass = make_pbr("Grass", tex_grass,
    scale=(6, 6, 6), sat=1.25, val=1.05, contrast=0.10,
    nstr=1.0, bstr=0.1, bdist=0.003, micro_noise=False, hue=0.50)

mat_paving = make_pbr("Paving", tex_paving,
    scale=(2.5, 2.5, 2.5), sat=0.70, val=0.82, contrast=0.12,
    nstr=2.0, bstr=0.35, bdist=0.015)

mat_glass = make_glass("Glass")
mat_roof = make_simple("RoofDark", (0.05, 0.05, 0.05, 1), roughness=0.65)
mat_frame = make_simple("DarkFrame", (0.025, 0.025, 0.025, 1), roughness=0.30, metallic=0.90)
mat_slab = make_simple("Slab", (0.55, 0.53, 0.50, 1), roughness=0.78)
mat_soffit = make_simple("Soffit", (0.82, 0.80, 0.78, 1), roughness=0.88)


# ====== BUILDING ======
BX = 12.0; BY = 8.0; WH = 3.0; WT = 0.30
ROOF_T = 0.25; OVERHANG = 1.0

# Ground
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object; ground.name = "Ground"
ground.data.materials.append(mat_grass)

# Plinth
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.10))
plinth = bpy.context.active_object; plinth.name = "Plinth"
plinth.scale = (BX + 0.2, BY + 0.2, 0.20)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
plinth.data.materials.append(mat_slab)

# Paving — irregular approach
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5, -BY/2 - 2.5, 0.015))
pav = bpy.context.active_object; pav.name = "Paving"
pav.scale = (5.0, 5.0, 0.03)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
pav.data.materials.append(mat_paving)

# ---- WALLS ----
# Back wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, BY/2 - WT/2, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallN"
w.scale = (BX, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Left wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(-BX/2 + WT/2, 0, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallW"
w.scale = (WT, BY - 2*WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Right wall — wood
bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - WT/2, 0, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallE"
w.scale = (WT, BY - 2*WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_wood_clad)

# Front: left concrete, right wood, center glazing
bpy.ops.mesh.primitive_cube_add(size=1, location=(-BX/2 + 1.5, -BY/2 + WT/2, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallS_L"
w.scale = (3.0, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - 1.5, -BY/2 + WT/2, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallS_R"
w.scale = (3.0, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_wood_clad)

# Lintel
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT/2, WH - 0.15 + 0.20))
w = bpy.context.active_object; w.name = "Lintel"
w.scale = (6.0, WT, 0.30)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Recess
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT - 0.05, WH/2 - 0.15 + 0.20))
recess = bpy.context.active_object; recess.name = "Recess"
recess.scale = (5.9, 0.10, 2.6)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
recess.data.materials.append(mat_slab)

# Glass
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + 0.04, WH/2 - 0.15 + 0.20))
glass_win = bpy.context.active_object; glass_win.name = "GlassMain"
glass_win.scale = (5.8, 0.02, 2.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
glass_win.data.materials.append(mat_glass)

# Frames
fw = 0.035
# Bottom
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + 0.04, 0.22))
fr = bpy.context.active_object; fr.name = "FrBot"
fr.scale = (6.0, 0.055, fw)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fr.data.materials.append(mat_frame)
# Top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + 0.04, WH - 0.30 + 0.20))
fr = bpy.context.active_object; fr.name = "FrTop"
fr.scale = (6.0, 0.055, fw)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fr.data.materials.append(mat_frame)
# Verticals
for fx in [-2.0, 0, 2.0]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, -BY/2 + 0.04, WH/2 - 0.05 + 0.20))
    fr = bpy.context.active_object; fr.name = f"FrV"
    fr.scale = (fw, 0.055, 2.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    fr.data.materials.append(mat_frame)

# Side window
bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - 0.01, -1.5, WH/2 + 0.20))
sw = bpy.context.active_object; sw.name = "SideWin"
sw.scale = (0.02, 1.5, 1.8)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
sw.data.materials.append(mat_glass)

# Roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, WH + ROOF_T/2 + 0.20))
roof = bpy.context.active_object; roof.name = "Roof"
roof.scale = (BX + 2*OVERHANG, BY + 2*OVERHANG, ROOF_T)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
roof.data.materials.append(mat_roof)

# Soffit
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - OVERHANG/2, WH + 0.19))
soffit = bpy.context.active_object; soffit.name = "Soffit"
soffit.scale = (BX + 2*OVERHANG, OVERHANG + 0.2, 0.02)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
soffit.data.materials.append(mat_soffit)

# Fascia
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - OVERHANG, WH + ROOF_T/2 + 0.20))
fascia = bpy.context.active_object; fascia.name = "Fascia"
fascia.scale = (BX + 2*OVERHANG, 0.012, ROOF_T + 0.02)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fascia.data.materials.append(mat_frame)


# ====== STEPS ======
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - 0.6 - i*0.40, 0.15 - i*0.05))
    step = bpy.context.active_object; step.name = f"Step_{i}"
    step.scale = (2.0, 0.40, 0.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    step.data.materials.append(mat_slab)


# ====== VEGETATION ======
random.seed(42)

# Multiple green shades for variety
def make_foliage(name, base_color, roughness=0.92):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Subsurface Weight"].default_value = 0.1
    return mat

mat_bush_dark = make_foliage("BushDark", (0.03, 0.10, 0.02, 1))
mat_bush_mid = make_foliage("BushMid", (0.06, 0.15, 0.04, 1))
mat_bush_light = make_foliage("BushLight", (0.10, 0.20, 0.06, 1))
mat_hedge = make_foliage("Hedge", (0.04, 0.12, 0.03, 1))

def add_bush(name, pos, scale, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=scale, location=pos)
    b = bpy.context.active_object; b.name = name
    b.scale = (1.0 + random.uniform(-0.2, 0.2),
               1.0 + random.uniform(-0.2, 0.2),
               0.5 + random.uniform(-0.1, 0.1))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    dm = b.modifiers.new("D", 'DISPLACE')
    nt = bpy.data.textures.new(f"N_{name}", 'CLOUDS')
    nt.noise_scale = 0.25 + random.uniform(-0.1, 0.1)
    nt.noise_depth = 4
    dm.texture = nt; dm.strength = 0.18 * scale; dm.mid_level = 0.5
    b.data.materials.append(mat)
    return b

# Garden bushes — layered groups
# Left garden
add_bush("BL1", (-BX/2 - 1.5, -2, 0.5), 0.85, mat_bush_dark)
add_bush("BL2", (-BX/2 - 2.3, -1.2, 0.45), 0.65, mat_bush_mid)
add_bush("BL3", (-BX/2 - 1.8, 0.5, 0.6), 1.0, mat_bush_dark)
add_bush("BL4", (-BX/2 - 2.5, 2.0, 0.55), 0.9, mat_bush_light)
add_bush("BL5", (-BX/2 - 1.2, 3.0, 0.4), 0.7, mat_bush_mid)

# Right garden
add_bush("BR1", (BX/2 + 1.5, -1.8, 0.45), 0.75, mat_bush_mid)
add_bush("BR2", (BX/2 + 2.2, 0, 0.55), 0.95, mat_bush_dark)
add_bush("BR3", (BX/2 + 1.8, 2.5, 0.5), 0.8, mat_bush_light)
add_bush("BR4", (BX/2 + 2.5, -3.0, 0.4), 0.6, mat_bush_dark)

# Front garden
add_bush("BF1", (-2.0, -BY/2 - 3.0, 0.35), 0.55, mat_bush_light)
add_bush("BF2", (3.0, -BY/2 - 2.5, 0.4), 0.65, mat_bush_mid)
add_bush("BF3", (1.0, -BY/2 - 4.0, 0.3), 0.50, mat_bush_dark)

# Hedge along back
for hi in range(8):
    hx = -BX/2 + 1 + hi * 1.6
    add_bush(f"H_{hi}", (hx, BY/2 + 1.5, 0.5), 0.75, mat_hedge)

# Trees
mat_bark = make_simple("Bark", (0.10, 0.07, 0.03, 1), roughness=0.95)
mat_crown_a = make_foliage("CrownA", (0.04, 0.13, 0.03, 1))
mat_crown_b = make_foliage("CrownB", (0.06, 0.16, 0.04, 1))
mat_crown_c = make_foliage("CrownC", (0.03, 0.10, 0.02, 1))

tree_data = [
    (-BX/2 - 5, -2, 7.0, 3.2, 0.20, mat_crown_a),
    (BX/2 + 7, -4, 8.5, 4.0, 0.25, mat_crown_b),
    (-5, BY/2 + 6, 6.5, 3.0, 0.18, mat_crown_c),
    (BX/2 + 4, BY/2 + 3, 6.0, 2.8, 0.16, mat_crown_a),
    (-BX/2 - 8, 3, 9.0, 4.5, 0.28, mat_crown_b),
    (BX/2 + 10, 2, 7.5, 3.5, 0.22, mat_crown_c),
]

for ti, (tx_, ty, theight, tcrown_r, trunk_r, crown_mat) in enumerate(tree_data):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=trunk_r,
                                         depth=theight, location=(tx_, ty, theight/2))
    trunk = bpy.context.active_object; trunk.name = f"Trunk_{ti}"
    trunk.data.materials.append(mat_bark)

    # Main crown
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=tcrown_r,
                                           location=(tx_, ty, theight + tcrown_r * 0.3))
    crown = bpy.context.active_object; crown.name = f"Crown_{ti}"
    crown.scale = (1.0, 1.0, 0.70)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    dm = crown.modifiers.new("D", 'DISPLACE')
    nt = bpy.data.textures.new(f"TN_{ti}", 'CLOUDS')
    nt.noise_scale = 0.4; nt.noise_depth = 5
    dm.texture = nt; dm.strength = 0.35 * tcrown_r
    crown.data.materials.append(crown_mat)

    # Secondary lobe
    ox = random.uniform(-0.8, 0.8)
    oz = random.uniform(-0.5, 0.5)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=tcrown_r * 0.55,
        location=(tx_ + ox, ty, theight + tcrown_r * 0.9 + oz))
    c2 = bpy.context.active_object; c2.name = f"C2_{ti}"
    bpy.ops.object.shade_smooth()
    dm2 = c2.modifiers.new("D", 'DISPLACE')
    dm2.texture = nt; dm2.strength = 0.3 * tcrown_r
    c2.data.materials.append(crown_mat)


# ====== LIGHTING ======
# Golden hour sun — low angle, warm
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object; sun.name = "Sun"
sun.data.energy = 3.5
sun.data.angle = math.radians(1.0)  # Sharp shadows
# Low sun from southwest
sun.rotation_euler = (math.radians(38), math.radians(12), math.radians(-50))
# Warm color
sun.data.color = (1.0, 0.93, 0.82)


# ====== CAMERA ======
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Wider view, showing full building + garden
cam_obj.location = (-12, -16, 2.0)
target = Vector((0, 0, 1.8))
direction = target - Vector(cam_obj.location)
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam_obj.rotation_euler = rot

cam_data.lens = 28
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 18.0
cam_data.dof.aperture_fstop = 5.6
cam_data.clip_end = 500


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

scene.render.film_transparent = False

out_path = os.path.join(OUT_DIR, "iterazione_3.png")
scene.render.filepath = out_path

print("\n=== ARCHVIZ ITER 3 — Golden hour, weathered concrete, organic vegetation ===")
print(f"Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"Samples: {scene.cycles.samples}")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {out_path} ===")
