"""
ELEMENTO 2 — Tetto Piode — ITERAZIONE 4
Texture vincente: castle_wall_slates
Raffinamento: piode più grandi (scale ridotto), camera centrata sul tetto,
              bordo gronda visibile, muro sotto con rock_wall_08
"""
import bpy
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.normpath(os.path.join(BASE, "..", "..", "materials", "textures"))
OUT_DIR = os.path.join(BASE, "iterazioni")
os.makedirs(OUT_DIR, exist_ok=True)
hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

piode_tex = {
    "diff": os.path.join(TEX_DIR, "castle_wall_slates_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "castle_wall_slates_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "castle_wall_slates_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "castle_wall_slates_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "castle_wall_slates_ao_2k.jpg"),
}
wall_tex = {
    "diff": os.path.join(TEX_DIR, "rock_wall_08_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "rock_wall_08_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "rock_wall_08_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "rock_wall_08_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "rock_wall_08_ao_2k.jpg"),
}
wood_tex = {
    "diff": os.path.join(TEX_DIR, "weathered_brown_planks_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "weathered_brown_planks_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "weathered_brown_planks_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "weathered_brown_planks_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "weathered_brown_planks_ao_2k.jpg"),
}

for t in [piode_tex, wall_tex, wood_tex]:
    for p in t.values():
        assert os.path.exists(p), f"Missing: {p}"


def make_pbr_mat(name, tex_files, scale=(1.5,1.5,1.5), sat=0.75, val=1.1,
                 contrast=0.1, normal_str=2.0, bump_str=0.8, bump_dist=0.05):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1000, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (600, 0)
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

    td = tx("Diff", tex_files["diff"], "sRGB", (-800, 400))
    ta = tx("AO", tex_files["ao"], "Non-Color", (-800, 200))
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'
    mx.location = (-400, 300); mx.inputs["Factor"].default_value = 1.0
    nt.links.new(td.outputs["Color"], mx.inputs[6])
    nt.links.new(ta.outputs["Color"], mx.inputs[7])

    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location=(-200, 300)
    bc.inputs["Contrast"].default_value = contrast
    nt.links.new(mx.outputs[2], bc.inputs["Color"])

    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location=(0, 300)
    hsv.inputs["Saturation"].default_value = sat
    hsv.inputs["Value"].default_value = val
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    tr = tx("Rough", tex_files["rough"], "Non-Color", (-800, -50))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    tn = tx("Nor", tex_files["nor"], "Non-Color", (-800, -250))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location=(-400,-250)
    nm.inputs["Strength"].default_value = normal_str
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdisp = tx("Disp", tex_files["disp"], "Non-Color", (-800, -450))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location=(-200,-400)
    bmp.inputs["Strength"].default_value = bump_str
    bmp.inputs["Distance"].default_value = bump_dist
    nt.links.new(tdisp.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


# === SCENE ===
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# HDRI
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wnt = world.node_tree; wnt.nodes.clear()
bg = wnt.nodes.new("ShaderNodeBackground")
env = wnt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(hdri_path)
mp_w = wnt.nodes.new("ShaderNodeMapping")
tc_w = wnt.nodes.new("ShaderNodeTexCoord")
out_w = wnt.nodes.new("ShaderNodeOutputWorld")
bg.inputs["Strength"].default_value = 2.0
mp_w.inputs["Rotation"].default_value = (0, 0, math.radians(60))
wnt.links.new(tc_w.outputs["Generated"], mp_w.inputs["Vector"])
wnt.links.new(mp_w.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], out_w.inputs["Surface"])

# === GROUND ===
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
gnd = bpy.context.active_object
mat_gnd = bpy.data.materials.new("Ground")
mat_gnd.use_nodes = True
mat_gnd.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.08, 0.11, 0.04, 1)
mat_gnd.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
gnd.data.materials.append(mat_gnd)

# === STONE WALL (base) — 5m wide, 2.5m tall, 0.45m thick ===
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.25))
wall = bpy.context.active_object
wall.name = "StoneWall"
wall.scale = (5.0, 0.45, 2.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mat_wall = make_pbr_mat("WallStone", wall_tex, scale=(1.2,1.2,1.2),
                         sat=0.85, val=1.20, contrast=0.15)
wall.data.materials.append(mat_wall)

# === ROOF SLAB — 5.5m wide, 4m slope, 5cm thick ===
# Pitched 30° forward (towards camera)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
roof = bpy.context.active_object
roof.name = "RoofPiode"
roof.scale = (5.5, 4.0, 0.05)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
# Rotate: front edge goes DOWN (negative rotation around X)
roof.rotation_euler = (math.radians(30), 0, 0)
# Position: back edge sits at top of wall (z=2.5), overhangs 30cm front
roof.location = (0, 0.5, 3.5)

mat_piode = make_pbr_mat("Piode", piode_tex, scale=(1.0, 1.0, 1.0),  # Bigger stones
                          sat=0.65, val=1.05, contrast=0.15,
                          normal_str=2.0, bump_str=1.0, bump_dist=0.06)
roof.data.materials.append(mat_piode)

# === WOOD FASCIA BOARD along front edge ===
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.6, 2.15))
fascia = bpy.context.active_object
fascia.name = "Fascia"
fascia.scale = (5.6, 0.06, 0.15)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mat_fascia = make_pbr_mat("WoodFascia", wood_tex, scale=(1.0, 4.0, 1.0),
                           sat=0.85, val=1.05)
fascia.data.materials.append(mat_fascia)

# === CAMERA — from front-above-right, looking at roof slope + wall ===
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (4.0, -7.0, 5.0)
cam_obj.rotation_euler = (math.radians(55), 0, math.radians(16))
cam_data.lens = 35

# === RENDER ===
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium Contrast'
except:
    scene.view_settings.look = 'AgX - Base Contrast'

out_path = os.path.join(OUT_DIR, "iter4_piode_complete.png")
scene.render.filepath = out_path

print(f"\n=== ITER 4 — Piode roof with wall and fascia ===")
print(f"  Roof: castle_wall_slates, scale 1.0 (large piode)")
print(f"  Wall: rock_wall_08")
print(f"  Fascia: weathered_brown_planks")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {out_path} ===")
