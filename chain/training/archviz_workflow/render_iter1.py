"""
ARCHVIZ WORKFLOW — ITERAZIONE 1
Modern house: clean geometry, PBR materials, HDRI sky, professional camera.
Following archviz best practices: concrete walls, wood cladding, glass, paving, grass.
"""
import bpy
import os
import math

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
             nstr=1.5, bstr=0.3, bdist=0.01, rough_offset=0.0):
    """Create a full PBR material with diffuse, normal, roughness, displacement."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1200, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (800, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1400, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1200, 0)
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
    td = tx("Diffuse", tex["diff"], "sRGB", (-800, 400))

    # Color adjustments
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-400, 400)
    bc.inputs["Contrast"].default_value = contrast
    nt.links.new(td.outputs["Color"], bc.inputs["Color"])

    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-200, 400)
    hsv.inputs["Saturation"].default_value = sat
    hsv.inputs["Value"].default_value = val
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    # Roughness
    tr = tx("Rough", tex["rough"], "Non-Color", (-800, 0))
    if rough_offset != 0.0:
        rmath = nt.nodes.new("ShaderNodeMath"); rmath.location = (-400, 0)
        rmath.operation = 'ADD'
        rmath.inputs[1].default_value = rough_offset
        rmath.use_clamp = True
        nt.links.new(tr.outputs["Color"], rmath.inputs[0])
        nt.links.new(rmath.outputs["Value"], bsdf.inputs["Roughness"])
    else:
        nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # Normal + Bump chain
    tn = tx("Normal", tex["nor"], "Non-Color", (-800, -200))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-400, -200)
    nm.inputs["Strength"].default_value = nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-800, -400))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-200, -350)
    bmp.inputs["Strength"].default_value = bstr
    bmp.inputs["Distance"].default_value = bdist
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def make_glass(name):
    """Create architectural glass material."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.85, 0.9, 1.0)
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.45
    bsdf.inputs["Roughness"].default_value = 0.0
    bsdf.inputs["Alpha"].default_value = 0.15
    mat.blend_method = 'OPAQUE'
    return mat


def make_simple(name, color, roughness=0.9, metallic=0.0):
    """Simple solid color material."""
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
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
wnt.nodes.clear()

bg = wnt.nodes.new("ShaderNodeBackground"); bg.location = (200, 0)
env = wnt.nodes.new("ShaderNodeTexEnvironment"); env.location = (-400, 0)
env.image = bpy.data.images.load(hdri_path)
mpw = wnt.nodes.new("ShaderNodeMapping"); mpw.location = (-600, 0)
tcw = wnt.nodes.new("ShaderNodeTexCoord"); tcw.location = (-800, 0)
outw = wnt.nodes.new("ShaderNodeOutputWorld"); outw.location = (400, 0)

bg.inputs["Strength"].default_value = 1.8
mpw.inputs["Rotation"].default_value = (0, 0, math.radians(120))

wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])


# ====== MATERIALS ======
mat_concrete = make_pbr("Concrete", tex_concrete,
    scale=(2, 2, 2), sat=0.85, val=0.95, contrast=0.1,
    nstr=2.0, bstr=0.4, bdist=0.015)

mat_wood_clad = make_pbr("WoodCladding", tex_wood,
    scale=(3, 1.5, 3), sat=0.9, val=0.85, contrast=0.08,
    nstr=1.5, bstr=0.3, bdist=0.01)

mat_grass = make_pbr("Grass", tex_grass,
    scale=(4, 4, 4), sat=1.1, val=0.95, contrast=0.05,
    nstr=1.0, bstr=0.2, bdist=0.008)

mat_paving = make_pbr("Paving", tex_paving,
    scale=(3, 3, 3), sat=0.8, val=0.9, contrast=0.08,
    nstr=1.5, bstr=0.25, bdist=0.01)

mat_glass = make_glass("Glass")

mat_roof = make_simple("RoofDark", (0.08, 0.08, 0.08, 1), roughness=0.75)
mat_frame = make_simple("DarkFrame", (0.04, 0.04, 0.04, 1), roughness=0.4, metallic=0.8)
mat_slab = make_simple("ConcreteSlab", (0.65, 0.63, 0.60, 1), roughness=0.85)


# ====== BUILDING GEOMETRY ======
# Modern house: 12x8m footprint, 3m walls, flat roof with slight overhang
BX = 12.0   # Length (X)
BY = 8.0    # Width (Y)
WH = 3.0    # Wall height
WT = 0.30   # Wall thickness
ROOF_T = 0.25  # Roof slab thickness
OVERHANG = 0.80  # Roof overhang

# --- Ground plane (grass) ---
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
ground = bpy.context.active_object; ground.name = "Ground"
ground.data.materials.append(mat_grass)

# --- Foundation slab ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.075))
slab = bpy.context.active_object; slab.name = "Slab"
slab.scale = (BX + 0.4, BY + 0.4, 0.15)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
slab.data.materials.append(mat_slab)

# --- Paving area in front (south side) ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - 2.5, 0.02))
pav = bpy.context.active_object; pav.name = "Paving"
pav.scale = (BX + 2, 5.0, 0.04)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
pav.data.materials.append(mat_paving)

# --- Floor inside ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.15))
floor = bpy.context.active_object; floor.name = "Floor"
floor.scale = (BX, BY, 0.01)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
floor.data.materials.append(mat_paving)

# --- Walls ---
# Back wall (north) - full concrete
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, BY/2 - WT/2, WH/2 + 0.15))
w = bpy.context.active_object; w.name = "WallN"
w.scale = (BX, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Left wall (west) - concrete
bpy.ops.mesh.primitive_cube_add(size=1, location=(-BX/2 + WT/2, 0, WH/2 + 0.15))
w = bpy.context.active_object; w.name = "WallW"
w.scale = (WT, BY - 2*WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Right wall (east) - wood cladding
bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - WT/2, 0, WH/2 + 0.15))
w = bpy.context.active_object; w.name = "WallE"
w.scale = (WT, BY - 2*WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_wood_clad)

# Front wall (south) - two segments with opening in center
# Left segment
bpy.ops.mesh.primitive_cube_add(size=1, location=(-BX/2 + 1.5, -BY/2 + WT/2, WH/2 + 0.15))
w = bpy.context.active_object; w.name = "WallS_L"
w.scale = (3.0, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# Right segment
bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - 1.5, -BY/2 + WT/2, WH/2 + 0.15))
w = bpy.context.active_object; w.name = "WallS_R"
w.scale = (3.0, WT, WH)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_wood_clad)

# Above-door lintel
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT/2, WH - 0.3 + 0.15))
w = bpy.context.active_object; w.name = "WallS_Top"
w.scale = (6.0, WT, 0.6)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
w.data.materials.append(mat_concrete)

# --- Large glass window (front, center) ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT/2, WH/2 - 0.3 + 0.15))
glass_win = bpy.context.active_object; glass_win.name = "GlassMain"
glass_win.scale = (5.8, 0.04, 2.4)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
glass_win.data.materials.append(mat_glass)

# Window frames (dark metal)
# Bottom frame
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT/2, 0.15 + 0.025))
fr = bpy.context.active_object; fr.name = "FrameBot"
fr.scale = (6.0, 0.06, 0.05)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fr.data.materials.append(mat_frame)

# Top frame
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 + WT/2, WH - 0.6 + 0.15))
fr = bpy.context.active_object; fr.name = "FrameTop"
fr.scale = (6.0, 0.06, 0.05)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fr.data.materials.append(mat_frame)

# Vertical dividers (3 panes)
for fx in [-1.93, 0, 1.93]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, -BY/2 + WT/2, WH/2 - 0.3 + 0.15))
    fr = bpy.context.active_object; fr.name = f"FrameV_{fx:.1f}"
    fr.scale = (0.04, 0.06, 2.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    fr.data.materials.append(mat_frame)

# --- Side window (east wall) ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(BX/2 - WT/2, -1.5, WH/2 + 0.15))
sw = bpy.context.active_object; sw.name = "SideWindow"
sw.scale = (0.04, 1.5, 1.8)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
sw.data.materials.append(mat_glass)

# --- Roof slab (flat with overhang) ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, WH + ROOF_T/2 + 0.15))
roof = bpy.context.active_object; roof.name = "Roof"
roof.scale = (BX + 2*OVERHANG, BY + 2*OVERHANG, ROOF_T)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
roof.data.materials.append(mat_roof)

# Roof edge detail (visible fascia)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - OVERHANG, WH + ROOF_T/2 + 0.15))
fascia = bpy.context.active_object; fascia.name = "Fascia"
fascia.scale = (BX + 2*OVERHANG, 0.02, ROOF_T + 0.04)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
fascia.data.materials.append(mat_frame)


# ====== ENTRY STEPS ======
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -BY/2 - 0.5 - i*0.35, 0.075 - i*0.05))
    step = bpy.context.active_object; step.name = f"Step_{i}"
    step.scale = (2.5, 0.35, 0.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    step.data.materials.append(mat_slab)


# ====== PROCEDURAL VEGETATION ======
# Simple bush shapes (icospheres with green material)
mat_bush = make_simple("Bush", (0.12, 0.22, 0.08, 1), roughness=0.95)

bush_positions = [
    (-BX/2 - 1.5, -2, 0.4, 0.8),   # Left side
    (-BX/2 - 2.0, 1.5, 0.5, 1.0),  # Left back
    (BX/2 + 1.2, -1.0, 0.35, 0.7), # Right front
    (BX/2 + 1.8, 2.0, 0.55, 1.1),  # Right back
    (-2.0, -BY/2 - 4.0, 0.6, 1.2), # Front garden
    (3.0, -BY/2 - 3.5, 0.45, 0.9), # Front garden right
]

for bi, (bx, by, bz, bscale) in enumerate(bush_positions):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=bscale, location=(bx, by, bz))
    bush = bpy.context.active_object; bush.name = f"Bush_{bi}"
    # Flatten slightly
    bush.scale[2] = 0.65
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Smooth shading
    bpy.ops.object.shade_smooth()
    bush.data.materials.append(mat_bush)


# ====== SIMPLE TREES (cylinder trunk + icosphere crown) ======
mat_bark = make_simple("Bark", (0.15, 0.10, 0.06, 1), roughness=0.95)
mat_crown = make_simple("Crown", (0.10, 0.20, 0.06, 1), roughness=0.95)

tree_positions = [
    (-BX/2 - 4, 0, 5.0, 2.5),      # Left
    (BX/2 + 5, -2, 6.0, 3.0),       # Right
    (-3, BY/2 + 4, 4.5, 2.2),       # Back left
]

for ti, (tx_, ty, theight, tcrown_r) in enumerate(tree_positions):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=theight, location=(tx_, ty, theight/2))
    trunk = bpy.context.active_object; trunk.name = f"Trunk_{ti}"
    trunk.data.materials.append(mat_bark)

    # Crown
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=tcrown_r,
                                           location=(tx_, ty, theight + tcrown_r * 0.5))
    crown = bpy.context.active_object; crown.name = f"Crown_{ti}"
    crown.scale[2] = 0.7
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    crown.data.materials.append(mat_crown)


# ====== SUN LIGHT (supplemental to HDRI) ======
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object; sun.name = "Sun"
sun.data.energy = 3.0
sun.data.angle = math.radians(2.0)  # Sharp shadows
sun.rotation_euler = (math.radians(55), math.radians(15), math.radians(-30))


# ====== CAMERA ======
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Position: eye-level, front-left 3/4 view, 15m away
cam_obj.location = (-9, -12, 1.65)
# Look at center of house, slightly above ground
target = (0, 0, 2.0)
direction = (target[0] - cam_obj.location[0],
             target[1] - cam_obj.location[1],
             target[2] - cam_obj.location[2])
import mathutils
rot = mathutils.Vector(direction).to_track_quat('-Z', 'Y').to_euler()
cam_obj.rotation_euler = rot

cam_data.lens = 32  # Archviz standard
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 15.0
cam_data.dof.aperture_fstop = 5.6  # Slight DOF


# ====== RENDER SETTINGS ======
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 256
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

# Film
scene.render.film_transparent = False

out_path = os.path.join(OUT_DIR, "iterazione_1.png")
scene.render.filepath = out_path

print("\n=== ARCHVIZ ITER 1 — Modern house, PBR materials, HDRI ===")
print(f"Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"Samples: {scene.cycles.samples}")
print(f"Camera: lens={cam_data.lens}mm, f/{cam_data.dof.aperture_fstop}")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {out_path} ===")
