"""
MURO MISTO ALPI — ITERAZIONE 7
Fix: muro riempie il frame, giunti ancora più scuri, bordo top irregolare,
texture anche sul lato visibile.
"""
import bpy
import os
import math
import bmesh
from mathutils import Vector

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.normpath(os.path.join(BASE, "..", "..", "materials", "textures"))
OUT_DIR = os.path.join(BASE, "iterazioni")
os.makedirs(OUT_DIR, exist_ok=True)
hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

tex = {
    "diff": os.path.join(TEX_DIR, "castle_wall_slates_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "castle_wall_slates_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "castle_wall_slates_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "castle_wall_slates_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "castle_wall_slates_ao_2k.jpg"),
}


def make_misto_alpi(name, tex):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (1000, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1800, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1600, 0)
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

    td = tx("Diff", tex["diff"], "sRGB", (-1200, 500))
    ta = tx("AO", tex["ao"], "Non-Color", (-1200, 300))

    # Very strong gamma on AO → near-black mortar
    ao_gamma = nt.nodes.new("ShaderNodeGamma"); ao_gamma.location = (-1000, 300)
    ao_gamma.inputs["Gamma"].default_value = 0.4  # Aggressive: really darkens mortar
    nt.links.new(ta.outputs["Color"], ao_gamma.inputs["Color"])

    mx_ao = nt.nodes.new("ShaderNodeMix")
    mx_ao.data_type = 'RGBA'; mx_ao.blend_type = 'MULTIPLY'
    mx_ao.location = (-800, 400); mx_ao.inputs["Factor"].default_value = 1.0
    nt.links.new(td.outputs["Color"], mx_ao.inputs[6])
    nt.links.new(ao_gamma.outputs["Color"], mx_ao.inputs[7])

    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-600, 400)
    bc.inputs["Contrast"].default_value = 0.22
    bc.inputs["Bright"].default_value = -0.02
    nt.links.new(mx_ao.outputs[2], bc.inputs["Color"])

    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-400, 400)
    hsv.inputs["Saturation"].default_value = 0.90
    hsv.inputs["Value"].default_value = 1.12
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])

    # Warm/cool patches
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-800, 100)
    noise.inputs["Scale"].default_value = 1.2
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.55
    nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])

    warm_hsv = nt.nodes.new("ShaderNodeHueSaturation"); warm_hsv.location = (-200, 200)
    warm_hsv.inputs["Hue"].default_value = 0.54
    warm_hsv.inputs["Saturation"].default_value = 1.30
    warm_hsv.inputs["Value"].default_value = 1.08
    nt.links.new(hsv.outputs["Color"], warm_hsv.inputs["Color"])

    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location = (-400, 100)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.65
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])

    color_var = nt.nodes.new("ShaderNodeMix")
    color_var.data_type = 'RGBA'; color_var.location = (0, 400)
    nt.links.new(ramp.outputs["Color"], color_var.inputs["Factor"])
    nt.links.new(hsv.outputs["Color"], color_var.inputs[6])
    nt.links.new(warm_hsv.outputs["Color"], color_var.inputs[7])

    # Mortar darkening via displacement
    tdi_color = tx("DispColor", tex["disp"], "Non-Color", (-1200, -700))
    invert = nt.nodes.new("ShaderNodeInvert"); invert.location = (-1000, -700)
    nt.links.new(tdi_color.outputs["Color"], invert.inputs["Color"])

    ramp2 = nt.nodes.new("ShaderNodeValToRGB"); ramp2.location = (-800, -700)
    ramp2.color_ramp.elements[0].position = 0.0
    ramp2.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp2.color_ramp.elements[1].position = 0.30  # Tighter → only deep mortar
    ramp2.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(invert.outputs["Color"], ramp2.inputs["Fac"])

    mortar = nt.nodes.new("ShaderNodeRGB"); mortar.location = (-600, -700)
    mortar.outputs[0].default_value = (0.03, 0.03, 0.025, 1.0)  # Near black

    mortar_mix = nt.nodes.new("ShaderNodeMix")
    mortar_mix.data_type = 'RGBA'; mortar_mix.location = (200, 400)
    nt.links.new(ramp2.outputs["Color"], mortar_mix.inputs["Factor"])
    nt.links.new(color_var.outputs[2], mortar_mix.inputs[6])
    nt.links.new(mortar.outputs[0], mortar_mix.inputs[7])

    nt.links.new(mortar_mix.outputs[2], bsdf.inputs["Base Color"])

    # Roughness
    tr = tx("Rough", tex["rough"], "Non-Color", (-1200, -100))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # Normal + Bump
    tn = tx("Nor", tex["nor"], "Non-Color", (-1200, -300))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-800, -300)
    nm.inputs["Strength"].default_value = 2.5
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-1200, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-600, -450)
    bmp.inputs["Strength"].default_value = 0.6
    bmp.inputs["Distance"].default_value = 0.02
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    # True displacement
    disp_node = nt.nodes.new("ShaderNodeDisplacement"); disp_node.location = (1000, -300)
    disp_node.inputs["Scale"].default_value = 0.04
    disp_node.inputs["Midlevel"].default_value = 0.5
    nt.links.new(tdi.outputs["Color"], disp_node.inputs["Height"])
    nt.links.new(disp_node.outputs["Displacement"], out.inputs["Displacement"])

    mat.displacement_method = 'BOTH'
    return mat


# === SCENE ===
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# HDRI
world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
wnt = world.node_tree; wnt.nodes.clear()
bg = wnt.nodes.new("ShaderNodeBackground")
env = wnt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(hdri_path)
mpw = wnt.nodes.new("ShaderNodeMapping")
tcw = wnt.nodes.new("ShaderNodeTexCoord")
outw = wnt.nodes.new("ShaderNodeOutputWorld")
bg.inputs["Strength"].default_value = 2.0
mpw.inputs["Rotation"].default_value = (0, 0, math.radians(40))
wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])

# Light grey backdrop
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 3, 5))
bpy.context.active_object.rotation_euler = (math.radians(90), 0, 0)
bg_mat = bpy.data.materials.new("BG"); bg_mat.use_nodes = True
bg_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.85, 0.85, 1)
bg_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
bpy.context.active_object.data.materials.append(bg_mat)

# Light grey ground
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
gnd = bpy.context.active_object
mg = bpy.data.materials.new("Ground"); mg.use_nodes = True
mg.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.75, 0.75, 0.75, 1)
mg.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
gnd.data.materials.append(mg)

# Wall — build with irregular top edge
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))
wall = bpy.context.active_object; wall.name = "Wall"
wall.scale = (3.0, 0.45, 2.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Irregularize top edge
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(wall.data)
bm.verts.ensure_lookup_table()
import random
random.seed(42)
for v in bm.verts:
    if v.co.z > 0.95:  # Top vertices (wall height ~1.0 from center)
        v.co.z += random.uniform(-0.04, 0.06)
bmesh.update_edit_mesh(wall.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Rotate for 3/4 view
wall.rotation_euler = (0, 0, math.radians(-20))

# Subdivision for displacement
subsurf = wall.modifiers.new("SubSurf", 'SUBSURF')
subsurf.subdivision_type = 'SIMPLE'
subsurf.levels = 0
subsurf.render_levels = 6

wall.data.materials.append(make_misto_alpi("MistoAlpi", tex))

# Camera — MUCH closer, wall fills the frame
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (2.0, -3.0, 1.2)    # Closer!
cam_obj.rotation_euler = (math.radians(80), 0, math.radians(20))
cam_data.lens = 50

# Render — 512 samples
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

out_path = os.path.join(OUT_DIR, "misto_alpi_iter7_closeup.png")
scene.render.filepath = out_path

print(f"\n=== MISTO ALPI ITER 7 — Closeup, dark mortar, irregular top ===")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {out_path} ===")
