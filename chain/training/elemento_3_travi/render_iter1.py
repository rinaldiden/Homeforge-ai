"""
ELEMENTO 3 — Travi legno — ITERAZIONE 1
5 travi sezione 15x20cm sporgenti 40cm dal muro, con tavolato sopra.
Confronto: rough_wood vs weathered_brown_planks
Vista dal basso-laterale per vedere le travi sporgenti.
"""
import bpy
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.normpath(os.path.join(BASE, "..", "..", "materials", "textures"))
OUT_DIR = os.path.join(BASE, "iterazioni")
os.makedirs(OUT_DIR, exist_ok=True)
hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

wood_A = {
    "diff": os.path.join(TEX_DIR, "rough_wood_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "rough_wood_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "rough_wood_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "rough_wood_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "rough_wood_ao_2k.jpg"),
}
wood_B = {
    "diff": os.path.join(TEX_DIR, "weathered_brown_planks_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "weathered_brown_planks_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "weathered_brown_planks_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "weathered_brown_planks_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "weathered_brown_planks_ao_2k.jpg"),
}
wall_tex = {
    "diff": os.path.join(TEX_DIR, "rock_wall_08_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "rock_wall_08_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "rock_wall_08_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "rock_wall_08_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "rock_wall_08_ao_2k.jpg"),
}


def make_pbr(name, tex, scale=(1,1,1), sat=0.85, val=1.1, contrast=0.1,
             nstr=2.0, bstr=0.8, bdist=0.05):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location=(1000,0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location=(600,0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location=(-1400,0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location=(-1200,0)
    mp.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    def tx(l, p, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label=l; n.location=loc
        n.image = bpy.data.images.load(p)
        n.image.colorspace_settings.name = cs
        n.projection='BOX'; n.projection_blend=0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n
    td = tx("D", tex["diff"], "sRGB", (-800,400))
    ta = tx("A", tex["ao"], "Non-Color", (-800,200))
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'
    mx.location=(-400,300); mx.inputs["Factor"].default_value=1.0
    nt.links.new(td.outputs["Color"], mx.inputs[6])
    nt.links.new(ta.outputs["Color"], mx.inputs[7])
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location=(-200,300)
    bc.inputs["Contrast"].default_value=contrast
    nt.links.new(mx.outputs[2], bc.inputs["Color"])
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location=(0,300)
    hsv.inputs["Saturation"].default_value=sat; hsv.inputs["Value"].default_value=val
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])
    tr = tx("R", tex["rough"], "Non-Color", (-800,-50))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])
    tn = tx("N", tex["nor"], "Non-Color", (-800,-250))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location=(-400,-250)
    nm.inputs["Strength"].default_value=nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    tdi = tx("Di", tex["disp"], "Non-Color", (-800,-450))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location=(-200,-400)
    bmp.inputs["Strength"].default_value=bstr; bmp.inputs["Distance"].default_value=bdist
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
    mat.displacement_method = 'BUMP'
    return mat


TESTS = {
    "A_rough_wood": wood_A,
    "B_weathered_planks": wood_B,
}

for tname, wood_tex in TESTS.items():
    print(f"\n{'='*60}")
    print(f"Rendering {tname}")
    print(f"{'='*60}")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # HDRI
    world = bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True; wnt = world.node_tree; wnt.nodes.clear()
    bg = wnt.nodes.new("ShaderNodeBackground")
    env = wnt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(hdri_path)
    mpw = wnt.nodes.new("ShaderNodeMapping")
    tcw = wnt.nodes.new("ShaderNodeTexCoord")
    outw = wnt.nodes.new("ShaderNodeOutputWorld")
    bg.inputs["Strength"].default_value = 2.0
    mpw.inputs["Rotation"].default_value = (0, 0, math.radians(60))
    wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
    wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
    wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
    wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])

    # Ground
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0,0,0))
    gnd = bpy.context.active_object
    mg = bpy.data.materials.new("Gnd"); mg.use_nodes=True
    mg.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.08,0.11,0.04,1)
    mg.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=0.95
    gnd.data.materials.append(mg)

    # Stone wall 4m x 2.5m x 0.45m
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.25))
    wall = bpy.context.active_object; wall.name="Wall"
    wall.scale = (4.0, 0.45, 2.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    wall.data.materials.append(make_pbr("Stone", wall_tex,
        scale=(1.2,1.2,1.2), sat=0.85, val=1.20, contrast=0.15))

    # Wood material for beams — scale stretched along beam length (Y)
    mat_beam = make_pbr(f"Beam_{tname}", wood_tex,
        scale=(2.0, 0.5, 2.0),  # Compressed along Y = grain runs along beam
        sat=0.90, val=1.0, contrast=0.12, nstr=1.5, bstr=0.6, bdist=0.03)

    # 5 travi sezione 0.15 x 0.20m, sporgenti 0.40m dal muro
    # Beams run perpendicular to wall (along Y), spaced 0.8m apart
    # Wall front face at Y = -0.225, beam protrudes 0.4m beyond
    beam_x_positions = [-1.6, -0.8, 0.0, 0.8, 1.6]
    beam_top_z = 2.5  # Top of wall

    for i, bx in enumerate(beam_x_positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, -0.35, beam_top_z - 0.10))
        beam = bpy.context.active_object
        beam.name = f"Beam_{i}"
        # 0.15 wide (X), 1.2 deep (Y: 0.8m inside wall + 0.4m protruding), 0.20 tall (Z)
        beam.scale = (0.15, 1.2, 0.20)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        beam.data.materials.append(mat_beam)

    # Tavolato (planking) on top of beams — thin board spanning all beams
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.35, beam_top_z + 0.02))
    tavolato = bpy.context.active_object
    tavolato.name = "Tavolato"
    tavolato.scale = (4.2, 1.2, 0.03)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mat_tav = make_pbr(f"Tavolato_{tname}", wood_tex,
        scale=(1.0, 0.5, 1.0), sat=0.80, val=0.90, contrast=0.08)
    tavolato.data.materials.append(mat_tav)

    # Camera — from below-front looking up at protruding beams
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (2.0, -3.5, 1.8)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(15))
    cam_data.lens = 28

    # Render
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

    out_path = os.path.join(OUT_DIR, f"iter1_{tname}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"SAVED: {out_path}")

print("\n=== ITER 1 COMPLETA ===")
