"""
ARCHVIZ WORKFLOW — ITERAZIONE 2
Improvements:
- Stronger PBR textures (higher normal strength, more contrast)
- Displaced ground for realism
- Better vegetation with noise displacement on bushes
- More detailed geometry (window recesses, soffit)
- Warmer tones and better color management
- Additional scene elements for context
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
             micro_noise=True):
    """Full PBR material with optional micro-noise for realism."""
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

    # Diffuse
    td = tx("Diffuse", tex["diff"], "sRGB", (-1200, 500))

    # Color adjustments
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-800, 500)
    bc.inputs["Contrast"].default_value = contrast
    nt.links.new(td.outputs["Color"], bc.inputs["Color"])

    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-600, 500)
    hsv.inputs["Saturation"].default_value = sat
    hsv.inputs["Value"].default_value = val
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    # Roughness
    tr = tx("Rough", tex["rough"], "Non-Color", (-1200, 100))
    if rough_offset != 0.0:
        rmath = nt.nodes.new("ShaderNodeMath"); rmath.location = (-800, 100)
        rmath.operation = 'ADD'; rmath.inputs[1].default_value = rough_offset
        rmath.use_clamp = True
        nt.links.new(tr.outputs["Color"], rmath.inputs[0])
        nt.links.new(rmath.outputs["Value"], bsdf.inputs["Roughness"])
    else:
        nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # Normal map
    tn = tx("Normal", tex["nor"], "Non-Color", (-1200, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-800, -200)
    nm.inputs["Strength"].default_value = nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    # Displacement texture -> Bump
    tdi = tx("Disp", tex["disp"], "Non-Color", (-1200, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-600, -350)
    bmp.inputs["Strength"].default_value = bstr
    bmp.inputs["Distance"].default_value = bdist
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])

    # Micro noise bump (adds grain/imperfection)
    if micro_noise:
        noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-1200, -700)
        noise.inputs["Scale"].default_value = 80.0
        noise.inputs["Detail"].default_value = 8.0
        noise.inputs["Roughness"].default_value = 0.6
        nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])

        bmp2 = nt.nodes.new("ShaderNodeBump"); bmp2.location = (-400, -400)
        bmp2.inputs["Strength"].default_value = 0.04
        bmp2.inputs["Distance"].default_value = 0.005
        nt.links.new(noise.outputs["Fac"], bmp2.inputs["Height"])
        nt.links.new(bmp.outputs["Normal"], bmp2.inputs["Normal"])
        nt.links.new(bmp2.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def make_glass(name):
    """Architectural glass — reflective with slight green tint."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.75, 0.82, 0.78, 1.0)
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.52
    bsdf.inputs["Roughness"].default_value = 0.01
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

bg.inputs["Strength"].default_value = 1.5
mpw.inputs["Rotation"].default_value = (0, 0, math.radians(140))

wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])


# ====== MATERIALS ======
mat_concrete = make_pbr("Concrete", tex_concrete,
    scale=(1.5, 1.5, 1.5), sat=0.80, val=0.90, contrast=0.15,
    nstr=2.5, bstr=0.5, bdist=0.02)

mat_wood_clad = make_pbr("WoodCladding", tex_wood,
    scale=(2, 0.8, 2), sat=0.85, val=0.80, contrast=0.12,
    nstr=2.0, bstr=0.4, bdist=0.012)

mat_grass = make_pbr("Grass", tex_grass,
    scale=(5, 5, 5), sat=1.15, val=1.0, contrast=0.08,
    nstr=1.2, bstr=0.15, bdist=0.005, micro_noise=False)

mat_paving = make_pbr("Paving", tex_paving,
    scale=(2, 2, 2), sat=0.75, val=0.85, contrast=0.10,
    nstr=1.8, bstr=0.3, bdist=0.012)

mat_glass = make_glass("Glass")
mat_roof = make_simple("RoofDark", (0.06, 0.06, 0.06, 1), roughness=0.70)
mat_frame = make_simple("DarkFrame", (0.03, 0.03, 0.03, 1), roughness=0.35, metallic=0.85)
mat_slab = make_simple("ConcreteSlab", (0.60, 0.58, 0.55, 1), roughness=0.80)
mat_soffit = make_simple("Soffit", (0.85, 0.83, 0.80, 1), roughness=0.9)


# ====== BUILDING GEOMETRY ======
BX = 12.0; BY = 8.0; WH = 3.0; WT = 0.30
ROOF_T = 0.25; OVERHANG = 0.90

# Ground
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
ground = bpy.context.active_object; ground.name = "Ground"
ground.data.materials.append(mat_grass)

# Foundation/plinth (visible concrete base)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.10))
plinth = bpy.context.active_object; plinth.name = "Plinth"
plinth.scale = (BX + 0.2, BY + 0.2, 0.20)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
plinth.data.materials.append(mat_slab)

# Paving (smaller, front approach only)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - 2.0, 0.02))
pav = bpy.context.active_object; pav.name = "Paving"
pav.scale = (6.0, 4.0, 0.04)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
pav.data.materials.append(mat_paving)

# Paving path (side approach)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-4, -BY/2 - 5, 0.02))
path = bpy.context.active_object; path.name = "Path"
path.scale = (1.5, 6.0, 0.04)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
path.data.materials.append(mat_paving)

# ---- WALLS ----
# Back wall (north) - concrete
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, BY/2 - WT/2, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallN"
w.scale = (BX, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Left wall (west) - concrete
bpy.ops.mesh.primitive_cube_add(size=1, location=(-BX/2 + WT/2, 0, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallW"
w.scale = (WT, BY - 2*WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Right wall (east) - wood cladding
bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - WT/2, 0, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallE"
w.scale = (WT, BY - 2*WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_wood_clad)

# Front wall (south) - split with large glazing
# Left concrete segment
bpy.ops.mesh.primitive_cube_add(size=1, location=(-BX/2 + 1.5, -BY/2 + WT/2, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallS_L"
w.scale = (3.0, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Right wood segment
bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - 1.5, -BY/2 + WT/2, WH/2 + 0.20))
w = bpy.context.active_object; w.name = "WallS_R"
w.scale = (3.0, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_wood_clad)

# Lintel above glazing
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT/2, WH - 0.20 + 0.20))
w = bpy.context.active_object; w.name = "Lintel"
w.scale = (6.0, WT, 0.40)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# ---- WINDOW RECESS (adds depth) ----
recess_depth = 0.10
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT - recess_depth/2, WH/2 - 0.20 + 0.20))
recess = bpy.context.active_object; recess.name = "Recess"
recess.scale = (5.9, recess_depth, 2.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
recess.data.materials.append(mat_slab)

# ---- GLASS ----
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + 0.05, WH/2 - 0.20 + 0.20))
glass_win = bpy.context.active_object; glass_win.name = "GlassMain"
glass_win.scale = (5.8, 0.02, 2.4)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
glass_win.data.materials.append(mat_glass)

# Window frames
frame_w = 0.04
# Bottom
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + 0.05, 0.22))
fr = bpy.context.active_object; fr.name = "FrBot"
fr.scale = (6.0, 0.06, frame_w)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fr.data.materials.append(mat_frame)

# Top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + 0.05, WH - 0.4 + 0.20))
fr = bpy.context.active_object; fr.name = "FrTop"
fr.scale = (6.0, 0.06, frame_w)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fr.data.materials.append(mat_frame)

# Verticals (3 panes)
for fx in [-2.0, 0, 2.0]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, -BY/2 + 0.05, WH/2 - 0.10 + 0.20))
    fr = bpy.context.active_object; fr.name = f"FrV_{fx:.0f}"
    fr.scale = (frame_w, 0.06, 2.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    fr.data.materials.append(mat_frame)

# ---- ROOF ----
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, WH + ROOF_T/2 + 0.20))
roof = bpy.context.active_object; roof.name = "Roof"
roof.scale = (BX + 2*OVERHANG, BY + 2*OVERHANG, ROOF_T)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
roof.data.materials.append(mat_roof)

# Soffit (underside of overhang - visible)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - OVERHANG/2, WH + 0.19))
soffit = bpy.context.active_object; soffit.name = "Soffit"
soffit.scale = (BX + 2*OVERHANG, OVERHANG, 0.02)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
soffit.data.materials.append(mat_soffit)

# Fascia
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - OVERHANG, WH + ROOF_T/2 + 0.20))
fascia = bpy.context.active_object; fascia.name = "Fascia"
fascia.scale = (BX + 2*OVERHANG, 0.015, ROOF_T + 0.03)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fascia.data.materials.append(mat_frame)


# ====== ENTRY ======
# Steps
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - 0.6 - i*0.40, 0.15 - i*0.05))
    step = bpy.context.active_object; step.name = f"Step_{i}"
    step.scale = (2.0, 0.40, 0.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    step.data.materials.append(mat_slab)

# Entry canopy (small glass plane above door)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - 0.8, WH + 0.10))
canopy = bpy.context.active_object; canopy.name = "Canopy"
canopy.scale = (2.5, 1.2, 0.03)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
canopy.data.materials.append(mat_glass)


# ====== VEGETATION ======
# Organic bush material with subsurface for leaf translucency
mat_bush = bpy.data.materials.new("Bush"); mat_bush.use_nodes = True
bsdf_bush = mat_bush.node_tree.nodes["Principled BSDF"]
bsdf_bush.inputs["Base Color"].default_value = (0.08, 0.18, 0.04, 1)
bsdf_bush.inputs["Roughness"].default_value = 0.90
bsdf_bush.inputs["Subsurface Weight"].default_value = 0.15

# Bushes with noise displacement for organic shape
bush_data = [
    (-BX/2 - 1.8, -2.0, 0.5, 0.9),
    (-BX/2 - 2.2, 1.8, 0.6, 1.1),
    (BX/2 + 1.5, -1.5, 0.4, 0.75),
    (BX/2 + 2.0, 2.5, 0.65, 1.15),
    (-1.5, -BY/2 - 2.5, 0.4, 0.7),
    (2.5, -BY/2 - 2.0, 0.35, 0.6),
    (-BX/2 - 1.0, -BY/2 - 1.0, 0.3, 0.55),
    (BX/2 + 2.5, -BY/2, 0.5, 0.85),
]

random.seed(42)
for bi, (bx, by, bz, bscale) in enumerate(bush_data):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=bscale,
                                           location=(bx, by, bz))
    bush = bpy.context.active_object; bush.name = f"Bush_{bi}"
    bush.scale = (1.0 + random.uniform(-0.15, 0.15),
                  1.0 + random.uniform(-0.15, 0.15),
                  0.55 + random.uniform(-0.1, 0.1))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()

    # Add noise displacement modifier
    disp_mod = bush.modifiers.new("Displace", 'DISPLACE')
    noise_tex = bpy.data.textures.new(f"BushNoise_{bi}", 'CLOUDS')
    noise_tex.noise_scale = 0.3 + random.uniform(-0.1, 0.1)
    noise_tex.noise_depth = 3
    disp_mod.texture = noise_tex
    disp_mod.strength = 0.15 * bscale
    disp_mod.mid_level = 0.5

    bush.data.materials.append(mat_bush)

# Trees
mat_bark = make_simple("Bark", (0.12, 0.08, 0.04, 1), roughness=0.95)
mat_crown_light = make_simple("CrownL", (0.06, 0.16, 0.04, 1), roughness=0.92)
mat_crown_dark = make_simple("CrownD", (0.04, 0.12, 0.03, 1), roughness=0.95)

tree_data = [
    (-BX/2 - 5, 0, 5.5, 2.8, 0.18, mat_crown_dark),
    (BX/2 + 6, -3, 7.0, 3.5, 0.22, mat_crown_light),
    (-4, BY/2 + 5, 5.0, 2.5, 0.16, mat_crown_dark),
    (BX/2 + 3, BY/2 + 2, 4.5, 2.2, 0.14, mat_crown_light),
]

for ti, (tx_, ty, theight, tcrown_r, trunk_r, crown_mat) in enumerate(tree_data):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=trunk_r,
                                         depth=theight, location=(tx_, ty, theight/2))
    trunk = bpy.context.active_object; trunk.name = f"Trunk_{ti}"
    trunk.data.materials.append(mat_bark)

    # Crown (main + secondary for volume)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=tcrown_r,
                                           location=(tx_, ty, theight + tcrown_r * 0.4))
    crown = bpy.context.active_object; crown.name = f"Crown_{ti}"
    crown.scale = (1.0, 1.0, 0.75)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    # Noise displacement for organic shape
    disp_mod = crown.modifiers.new("Displace", 'DISPLACE')
    noise_tex = bpy.data.textures.new(f"TreeNoise_{ti}", 'CLOUDS')
    noise_tex.noise_scale = 0.5
    noise_tex.noise_depth = 4
    disp_mod.texture = noise_tex
    disp_mod.strength = 0.3 * tcrown_r
    crown.data.materials.append(crown_mat)

    # Secondary crown volume
    offset_x = random.uniform(-0.5, 0.5)
    offset_z = random.uniform(-0.3, 0.3)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=tcrown_r * 0.65,
        location=(tx_ + offset_x, ty, theight + tcrown_r * 0.8 + offset_z))
    c2 = bpy.context.active_object; c2.name = f"Crown2_{ti}"
    bpy.ops.object.shade_smooth()
    disp_mod2 = c2.modifiers.new("Displace", 'DISPLACE')
    disp_mod2.texture = noise_tex
    disp_mod2.strength = 0.25 * tcrown_r
    c2.data.materials.append(crown_mat)


# ====== OUTDOOR FURNITURE / CONTEXT ======
# Simple planter box (left of entry)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.8, -BY/2 - 0.5, 0.25))
planter = bpy.context.active_object; planter.name = "Planter"
planter.scale = (0.6, 0.6, 0.50)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
planter.data.materials.append(mat_slab)

# Planter soil/plants
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.3, location=(-1.8, -BY/2 - 0.5, 0.55))
plant = bpy.context.active_object; plant.name = "PlanterPlant"
plant.scale = (1.0, 1.0, 0.6)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.shade_smooth()
plant.data.materials.append(mat_bush)


# ====== SUN LIGHT ======
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object; sun.name = "Sun"
sun.data.energy = 2.5
sun.data.angle = math.radians(1.5)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-40))


# ====== CAMERA ======
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Eye-level 3/4 view from southwest, closer
cam_obj.location = (-8, -10, 1.65)
target = Vector((1, 0, 1.8))
direction = target - Vector(cam_obj.location)
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam_obj.rotation_euler = rot

cam_data.lens = 28
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 12.0
cam_data.dof.aperture_fstop = 4.0


# ====== RENDER SETTINGS ======
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 300
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '16'

# Color management
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium Contrast'
except:
    scene.view_settings.look = 'AgX - Base Contrast'

scene.render.film_transparent = False

out_path = os.path.join(OUT_DIR, "iterazione_2.png")
scene.render.filepath = out_path

print("\n=== ARCHVIZ ITER 2 — Stronger textures, organic vegetation, more detail ===")
print(f"Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"Samples: {scene.cycles.samples}")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {out_path} ===")
