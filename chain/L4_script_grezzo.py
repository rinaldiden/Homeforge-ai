"""
HomeForge AI — L4 Script: Render Grezzo + Depth + Canny
Genera geometria con materiali base grigi, depth map e canny map per pipeline Flux.
"""

import bpy
import bmesh
import math
import os
import sys
from pathlib import Path
from mathutils import Vector

# === CONFIG ===
PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RENDER_GREZZO = str(OUTPUT_DIR / "test_L4_grezzo.png")
RENDER_DEPTH = str(OUTPUT_DIR / "test_L4_depth.png")
RENDER_CANNY = str(OUTPUT_DIR / "test_L4_canny.png")

# Parametri edificio
PIANTA_W = 11.0  # x
PIANTA_D = 8.0   # y
H_GRONDA = 3.0
H_COLMO = 4.8
T_MURO = 0.45
COLMO_OFFSET_Y = 1.5  # verso nord (offset dal centro)
SPORTO = 0.40
SPESSORE_TETTO = 0.18


# === UTILITY ===

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in bpy.data.collections:
        if c.name != 'Scene':
            bpy.data.collections.remove(c)
    for block in [bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights]:
        for item in block:
            block.remove(item)


def make_box(name, w, d, h, x=0, y=0, z=0):
    """Crea un box con dimensioni e posizione specificate."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + w/2, y + d/2, z + h/2))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    return obj


def boolean_cut(target, cutter_name, w, d, h, x, y, z):
    """Taglio booleano su target."""
    cutter = make_box(cutter_name, w, d, h, x, y, z)
    mod = target.modifiers.new(name=cutter_name, type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except RuntimeError as e:
        print(f"  WARN: modifier apply failed: {e}")
        target.modifiers.remove(mod)
    cutter.select_set(True)
    bpy.ops.object.delete()
    return target


# === MATERIALI BASE (grigi per render grezzo) ===

def mat_base_grey(name, color=(0.6, 0.6, 0.6, 1.0), roughness=0.7):
    """Materiale grigio base — la texture vera sarà aggiunta da Flux."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def create_materials():
    """Crea set di materiali base."""
    mats = {}
    mats["pietra"] = mat_base_grey("Pietra", (0.55, 0.53, 0.50, 1.0), 0.85)
    mats["piode"] = mat_base_grey("Piode", (0.35, 0.35, 0.33, 1.0), 0.75)
    mats["legno"] = mat_base_grey("Legno", (0.30, 0.22, 0.15, 1.0), 0.65)
    mats["vetro"] = mat_base_grey("Vetro", (0.7, 0.75, 0.7, 1.0), 0.05)
    mats["terreno"] = mat_base_grey("Terreno", (0.35, 0.45, 0.25, 1.0), 0.90)
    return mats


# === GEOMETRIA ===

def build_walls(mats):
    """Costruisci i 4 muri."""
    walls = []

    # Muro SUD (x=0..11, y=0)
    w_sud = make_box("Muro_Sud", PIANTA_W, T_MURO, H_GRONDA, 0, 0, 0)
    w_sud.data.materials.append(mats["pietra"])
    walls.append(w_sud)

    # Muro NORD (x=0..11, y=8-T)
    w_nord = make_box("Muro_Nord", PIANTA_W, T_MURO, H_GRONDA, 0, PIANTA_D - T_MURO, 0)
    w_nord.data.materials.append(mats["pietra"])
    walls.append(w_nord)

    # Muro OVEST (x=0, y=0..8)
    w_ovest = make_box("Muro_Ovest", T_MURO, PIANTA_D, H_GRONDA, 0, 0, 0)
    w_ovest.data.materials.append(mats["pietra"])
    walls.append(w_ovest)

    # Muro EST (x=11-T, y=0..8)
    w_est = make_box("Muro_Est", T_MURO, PIANTA_D, H_GRONDA, PIANTA_W - T_MURO, 0, 0)
    w_est.data.materials.append(mats["pietra"])
    walls.append(w_est)

    return walls


def cut_openings(walls):
    """Taglia aperture nei muri."""
    w_sud, w_nord, w_ovest, w_est = walls
    T4 = T_MURO * 4  # cutter spessore

    # Vetrata angolo SW — SUD (da x=0 a x=2.4, h=0.4..2.8)
    boolean_cut(w_sud, "Cut_VetrSW_S", 2.4, T4, 2.4, 0, -T4/2 + T_MURO/2, 0.4)
    # Vetrata angolo SW — OVEST (da y=0 a y=2.4)
    boolean_cut(w_ovest, "Cut_VetrSW_O", T4, 2.4, 2.4, -T4/2 + T_MURO/2, 0, 0.4)

    # Finestra sud centrale (x=5.5, w=1.2, h=1.4, dav=0.9)
    boolean_cut(w_sud, "Cut_FinSud", 1.2, T4, 1.4, 5.5 - 0.6, -T4/2 + T_MURO/2, 0.9)

    # Porta ingresso (x=3.5, w=1.0, h=2.2)
    boolean_cut(w_sud, "Cut_Porta", 1.0, T4, 2.2, 3.5 - 0.5, -T4/2 + T_MURO/2, 0.0)

    # Finestra ovest (y=5.0, w=1.0, h=1.2, dav=0.9)
    boolean_cut(w_ovest, "Cut_FinOvest", T4, 1.0, 1.2, -T4/2 + T_MURO/2, 5.0 - 0.5, 0.9)

    # Finestre est (y=3.0 e y=7.0)
    boolean_cut(w_est, "Cut_FinEst1", T4, 1.0, 1.2,
                PIANTA_W - T_MURO - T4/2 + T_MURO/2, 3.0 - 0.5, 0.9)
    boolean_cut(w_est, "Cut_FinEst2", T4, 1.0, 1.2,
                PIANTA_W - T_MURO - T4/2 + T_MURO/2, 7.0 - 0.5, 0.9)

    # Finestre nord (piccole: x=3.5 e x=7.5, w=0.8, h=1.0, dav=1.2)
    boolean_cut(w_nord, "Cut_FinNord1", 0.8, T4, 1.0,
                3.5 - 0.4, PIANTA_D - T_MURO - T4/2 + T_MURO/2, 1.2)
    boolean_cut(w_nord, "Cut_FinNord2", 0.8, T4, 1.0,
                7.5 - 0.4, PIANTA_D - T_MURO - T4/2 + T_MURO/2, 1.2)


def build_glazing(mats):
    """Vetri nelle aperture."""
    # Vetrata angolo SW — 2 lastre
    v1 = make_box("Vetro_SW_S", 2.4, 0.03, 2.4, 0, T_MURO/2 - 0.015, 0.4)
    v1.data.materials.append(mats["vetro"])
    v2 = make_box("Vetro_SW_O", 0.03, 2.4, 2.4, T_MURO/2 - 0.015, 0, 0.4)
    v2.data.materials.append(mats["vetro"])

    # Finestra sud
    v3 = make_box("Vetro_FinSud", 1.2, 0.03, 1.4, 5.5 - 0.6, T_MURO/2 - 0.015, 0.9)
    v3.data.materials.append(mats["vetro"])


def build_frames(mats):
    """Telai finestre in legno scuro."""
    frame_t = 0.06
    # Telaio porta
    # Stipiti
    make_box("Telaio_Porta_L", frame_t, frame_t, 2.2, 3.5 - 0.5 - frame_t, T_MURO/2 - frame_t/2, 0).data.materials.append(mats["legno"])
    make_box("Telaio_Porta_R", frame_t, frame_t, 2.2, 3.5 + 0.5, T_MURO/2 - frame_t/2, 0).data.materials.append(mats["legno"])
    # Architrave
    make_box("Telaio_Porta_T", 1.0 + 2*frame_t, frame_t, frame_t, 3.5 - 0.5 - frame_t, T_MURO/2 - frame_t/2, 2.2).data.materials.append(mats["legno"])

    # Telaio finestra sud
    make_box("Telaio_FinSud_L", frame_t, frame_t, 1.4, 5.5 - 0.6 - frame_t, T_MURO/2 - frame_t/2, 0.9).data.materials.append(mats["legno"])
    make_box("Telaio_FinSud_R", frame_t, frame_t, 1.4, 5.5 + 0.6, T_MURO/2 - frame_t/2, 0.9).data.materials.append(mats["legno"])
    make_box("Telaio_FinSud_T", 1.2 + 2*frame_t, frame_t, frame_t, 5.5 - 0.6 - frame_t, T_MURO/2 - frame_t/2, 0.9 + 1.4).data.materials.append(mats["legno"])
    make_box("Telaio_FinSud_B", 1.2 + 2*frame_t, frame_t, frame_t, 5.5 - 0.6 - frame_t, T_MURO/2 - frame_t/2, 0.9 - frame_t).data.materials.append(mats["legno"])


def build_roof(mats):
    """Tetto asimmetrico con piode."""
    cx = PIANTA_W / 2
    cy = PIANTA_D / 2 + COLMO_OFFSET_Y  # colmo offset nord

    # Vertices del tetto (mesh custom)
    verts = [
        # Base sud
        (-SPORTO, -SPORTO, H_GRONDA),                          # 0 SW basso
        (PIANTA_W + SPORTO, -SPORTO, H_GRONDA),                 # 1 SE basso
        # Colmo
        (-SPORTO, cy, H_COLMO),                                  # 2 W colmo
        (PIANTA_W + SPORTO, cy, H_COLMO),                       # 3 E colmo
        # Base nord
        (-SPORTO, PIANTA_D + SPORTO, H_GRONDA),                 # 4 NW basso
        (PIANTA_W + SPORTO, PIANTA_D + SPORTO, H_GRONDA),       # 5 NE basso
    ]

    faces = [
        (0, 1, 3, 2),  # Falda sud
        (2, 3, 5, 4),  # Falda nord
    ]

    mesh = bpy.data.meshes.new("Tetto_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    tetto = bpy.data.objects.new("Tetto", mesh)
    bpy.context.collection.objects.link(tetto)
    tetto.data.materials.append(mats["piode"])

    # Spessore tetto via solidify
    mod = tetto.modifiers.new("Solidify", 'SOLIDIFY')
    mod.thickness = SPESSORE_TETTO
    mod.offset = -1
    bpy.context.view_layer.objects.active = tetto
    bpy.ops.object.modifier_apply(modifier=mod.name)

    return tetto


def build_timpani(mats):
    """Timpani est e ovest (triangolo sopra gronda)."""
    cy = PIANTA_D / 2 + COLMO_OFFSET_Y

    for side, x_pos in [("Ovest", 0), ("Est", PIANTA_W - T_MURO)]:
        verts = [
            (x_pos, 0, H_GRONDA),
            (x_pos, PIANTA_D, H_GRONDA),
            (x_pos, cy, H_COLMO),
            (x_pos + T_MURO, 0, H_GRONDA),
            (x_pos + T_MURO, PIANTA_D, H_GRONDA),
            (x_pos + T_MURO, cy, H_COLMO),
        ]
        faces = [
            (0, 1, 2),
            (3, 5, 4),
            (0, 3, 4, 1),
            (0, 2, 5, 3),
            (1, 4, 5, 2),
        ]
        mesh = bpy.data.meshes.new(f"Timpano_{side}_Mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(f"Timpano_{side}", mesh)
        bpy.context.collection.objects.link(obj)
        obj.data.materials.append(mats["pietra"])


def build_beams(mats):
    """Travi gronda a vista."""
    beam_w = 0.15
    beam_h = 0.20
    beam_spacing = 0.60
    sporto_extra = 0.10  # sporgenza teste

    cy = PIANTA_D / 2 + COLMO_OFFSET_Y
    n_beams = int(PIANTA_W / beam_spacing) + 1

    for i in range(n_beams):
        x = i * beam_spacing
        if x > PIANTA_W:
            break
        # Trave sud (dalla gronda al colmo, solo la parte visibile allo sporto)
        obj = make_box(f"Trave_S_{i}", beam_w, SPORTO + sporto_extra, beam_h,
                       x - beam_w/2, -SPORTO, H_GRONDA - beam_h)
        obj.data.materials.append(mats["legno"])

        # Trave nord
        obj = make_box(f"Trave_N_{i}", beam_w, SPORTO + sporto_extra, beam_h,
                       x - beam_w/2, PIANTA_D, H_GRONDA - beam_h)
        obj.data.materials.append(mats["legno"])


def build_chimney(mats):
    """Comignolo in pietra."""
    cx = PIANTA_W / 2
    cy = PIANTA_D / 2 + COLMO_OFFSET_Y
    ch = 1.0  # altezza comignolo sopra colmo

    obj = make_box("Comignolo", 0.60, 0.60, ch, cx - 0.30, cy - 0.30, H_COLMO)
    obj.data.materials.append(mats["pietra"])


def build_ground(mats):
    """Piano terreno."""
    obj = make_box("Terreno", 30, 30, 0.1, -10, -15, -0.1)
    obj.data.materials.append(mats["terreno"])


# === CAMERA & LIGHTING ===

def setup_camera():
    """Camera dal prato sud, altezza occhi."""
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 35
    cam_data.clip_start = 0.1
    cam_data.clip_end = 500

    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Posizione: 16m a sud, altezza occhi
    cam_obj.location = (PIANTA_W / 2, -16.0, 1.6)

    # Punta al centro dell'edificio
    target_point = Vector((PIANTA_W / 2, PIANTA_D / 2, H_GRONDA / 2 + 0.5))
    direction = target_point - cam_obj.location
    rot = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot.to_euler()

    return cam_obj


def setup_lighting():
    """Illuminazione overcast naturale."""
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    # Background node
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.7, 0.75, 0.85, 1.0)
    bg.inputs["Strength"].default_value = 1.5

    output = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg.outputs["Background"], output.inputs["Surface"])

    # Sun light per ombre morbide
    sun_data = bpy.data.lights.new("Sun", type='SUN')
    sun_data.energy = 3.0
    sun_data.angle = math.radians(15)  # soft shadows

    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (20, -10, 25)
    sun_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))


def setup_render_grezzo():
    """Setup render per output grezzo."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64  # Basso per render grezzo (è solo guida)
    scene.cycles.use_denoising = True

    scene.render.resolution_x = 1024
    scene.render.resolution_y = 768
    scene.render.film_transparent = False  # Sfondo visibile nel grezzo

    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'

    # Color management
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'

    # GPU fallback CPU
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'CUDA'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = 'GPU'
        print("[L4] Using GPU rendering")
    except Exception:
        scene.cycles.device = 'CPU'
        print("[L4] Using CPU rendering")


# === RENDER PASSES ===

def render_grezzo():
    """Render principale con materiali base."""
    scene = bpy.context.scene
    scene.render.filepath = RENDER_GREZZO
    bpy.ops.render.render(write_still=True)
    print(f"[L4] Render grezzo salvato: {RENDER_GREZZO}")


def render_depth_map():
    """Genera depth map usando materiale Camera Data (Blender 5.0 safe, NO scene.node_tree)."""
    scene = bpy.context.scene
    cam = scene.camera

    # Calcola range di profondità
    cam_near = 1.0
    cam_far = 50.0

    # Salva materiali originali
    original_mats = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.data.materials:
            original_mats[obj.name] = [m for m in obj.data.materials]

    # Crea materiale depth (bianco=vicino, nero=lontano)
    mat_depth = bpy.data.materials.new("DepthMat")
    mat_depth.use_nodes = True
    nt = mat_depth.node_tree
    nt.nodes.clear()

    # Camera Data → View Z Depth
    cam_data = nt.nodes.new("ShaderNodeCameraData")

    # Map Range: normalizza la distanza
    map_range = nt.nodes.new("ShaderNodeMapRange")
    map_range.inputs["From Min"].default_value = cam_near
    map_range.inputs["From Max"].default_value = cam_far
    map_range.inputs["To Min"].default_value = 1.0   # vicino = bianco
    map_range.inputs["To Max"].default_value = 0.0   # lontano = nero
    map_range.clamp = True
    nt.links.new(cam_data.outputs["View Z Depth"], map_range.inputs["Value"])

    # Emission shader (no lighting influence)
    emission = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(map_range.outputs["Result"], emission.inputs["Strength"])
    emission.inputs["Color"].default_value = (1, 1, 1, 1)

    output = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(emission.outputs["Emission"], output.inputs["Surface"])

    # Applica a tutti gli oggetti
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(mat_depth)

    # Sfondo nero
    world = bpy.context.scene.world
    old_world_settings = None
    if world and world.use_nodes:
        for node in world.node_tree.nodes:
            if node.type == 'BACKGROUND':
                old_world_settings = (
                    list(node.inputs["Color"].default_value),
                    node.inputs["Strength"].default_value
                )
                node.inputs["Color"].default_value = (0, 0, 0, 1)
                node.inputs["Strength"].default_value = 0.0
                break

    # Disabilita luci (il depth è emission-based)
    hidden_lights = []
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and not obj.hide_render:
            obj.hide_render = True
            hidden_lights.append(obj)

    # Render
    scene.render.filepath = RENDER_DEPTH
    scene.render.image_settings.color_mode = 'BW'
    bpy.ops.render.render(write_still=True)
    scene.render.image_settings.color_mode = 'RGB'
    print(f"[L4] Depth map salvata: {RENDER_DEPTH}")

    # Ripristina
    for obj in hidden_lights:
        obj.hide_render = False
    for obj_name, mat_list in original_mats.items():
        obj = bpy.data.objects.get(obj_name)
        if obj:
            obj.data.materials.clear()
            for m in mat_list:
                obj.data.materials.append(m)
    if world and world.use_nodes and old_world_settings:
        for node in world.node_tree.nodes:
            if node.type == 'BACKGROUND':
                node.inputs["Color"].default_value = old_world_settings[0]
                node.inputs["Strength"].default_value = old_world_settings[1]
                break
    bpy.data.materials.remove(mat_depth)


def render_canny_map():
    """Genera canny edge map dal render grezzo usando filtri semplici.
    Semplificato: usa il normale render con materiali ad alto contrasto.
    """
    scene = bpy.context.scene

    # Salva materiali originali
    original_mats = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.data.materials:
            original_mats[obj.name] = [m for m in obj.data.materials]

    # Crea materiale bianco per edge detection via Freestyle
    mat_white = bpy.data.materials.new("EdgeWhite")
    mat_white.use_nodes = True
    bsdf = mat_white.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
    bsdf.inputs["Roughness"].default_value = 1.0

    # Applica bianco a tutti gli oggetti
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(mat_white)

    # Sfondo nero
    world = bpy.context.scene.world
    if world and world.use_nodes:
        bg = None
        for node in world.node_tree.nodes:
            if node.type == 'BACKGROUND':
                bg = node
                break
        if bg:
            old_color = list(bg.inputs["Color"].default_value)
            old_strength = bg.inputs["Strength"].default_value
            bg.inputs["Color"].default_value = (0, 0, 0, 1)
            bg.inputs["Strength"].default_value = 0.0

    # Abilita Freestyle per bordi
    scene.render.use_freestyle = True
    vl = scene.view_layers[0]
    vl.freestyle_settings.linesets[0].select_silhouette = True
    vl.freestyle_settings.linesets[0].select_border = True
    vl.freestyle_settings.linesets[0].select_crease = True
    vl.freestyle_settings.linesets[0].linestyle.color = (0, 0, 0)
    vl.freestyle_settings.linesets[0].linestyle.thickness = 2.0

    # Render canny-like
    scene.render.filepath = RENDER_CANNY
    scene.render.film_transparent = True
    bpy.ops.render.render(write_still=True)

    # Ripristina
    scene.render.use_freestyle = False
    scene.render.film_transparent = False
    for obj_name, mat_list in original_mats.items():
        obj = bpy.data.objects.get(obj_name)
        if obj:
            obj.data.materials.clear()
            for m in mat_list:
                obj.data.materials.append(m)

    if world and world.use_nodes and bg:
        bg.inputs["Color"].default_value = old_color
        bg.inputs["Strength"].default_value = old_strength

    bpy.data.materials.remove(mat_white)
    print(f"[L4] Canny map salvata: {RENDER_CANNY}")


# === MAIN ===

def main():
    print("=" * 60)
    print("HomeForge AI — L4 Render Grezzo + Depth + Canny")
    print("=" * 60)

    # 1. Clear
    clear_scene()
    print("[L4] Scene cleared")

    # 2. Materiali
    mats = create_materials()
    print("[L4] Materials created")

    # 3. Geometria
    walls = build_walls(mats)
    print("[L4] Walls built")

    cut_openings(walls)
    print("[L4] Openings cut")

    build_glazing(mats)
    print("[L4] Glazing added")

    build_frames(mats)
    print("[L4] Frames added")

    build_roof(mats)
    print("[L4] Roof built")

    build_timpani(mats)
    print("[L4] Gable walls built")

    build_beams(mats)
    print("[L4] Beams added")

    build_chimney(mats)
    print("[L4] Chimney added")

    build_ground(mats)
    print("[L4] Ground added")

    # 4. Camera & Lighting
    setup_camera()
    print("[L4] Camera set")

    setup_lighting()
    print("[L4] Lighting set")

    # 5. Render setup
    setup_render_grezzo()
    print("[L4] Render settings configured")

    # 6. Render grezzo
    print("[L4] Rendering grezzo...")
    render_grezzo()

    # 7. Depth map
    print("[L4] Rendering depth map...")
    render_depth_map()

    # 8. Canny map
    print("[L4] Rendering canny map...")
    render_canny_map()

    print("=" * 60)
    print("[L4] COMPLETATO — 3 output generati:")
    print(f"  - Grezzo: {RENDER_GREZZO}")
    print(f"  - Depth:  {RENDER_DEPTH}")
    print(f"  - Canny:  {RENDER_CANNY}")
    print("=" * 60)


if __name__ == "__main__":
    main()
