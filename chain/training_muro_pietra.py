"""
HomeForge AI — Training: Muro in pietra — ITERAZIONE 3
Texture PBR reali da Poly Haven (broken_wall) + bump forte
"""
import bpy, bmesh, math, time
from pathlib import Path

PROJ = Path(__file__).parent.parent
TEX_DIR = Path(__file__).parent / "materials" / "textures"
OUTPUT = str(PROJ / "output" / "training_muro_final.png")

# === CLEAR ===
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in bpy.data.meshes: bpy.data.meshes.remove(m)
for m in bpy.data.materials: bpy.data.materials.remove(m)
for img in bpy.data.images: bpy.data.images.remove(img)

# === MURO 3m x 2m x 0.45m ===
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.0))
obj = bpy.context.active_object
obj.name = "Muro"
obj.scale = (3.0, 0.45, 2.0)
bpy.ops.object.transform_apply(scale=True)

# === MATERIALE PBR con texture reali ===
mat = bpy.data.materials.new("PietraFiume_PBR")
mat.use_nodes = True
mat.displacement_method = 'BUMP'
nt = mat.node_tree
ns = nt.nodes
lk = nt.links
for n in ns: ns.remove(n)

# --- Nodi base ---
out = ns.new("ShaderNodeOutputMaterial"); out.location = (1200, 0)
bsdf = ns.new("ShaderNodeBsdfPrincipled"); bsdf.location = (800, 0)
lk.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# --- Texture Coordinate + Mapping ---
tc = ns.new("ShaderNodeTexCoord"); tc.location = (-800, 0)
mapping = ns.new("ShaderNodeMapping"); mapping.location = (-600, 0)
# Scala per adattare la texture al muro 3m x 2m
# La texture è quadrata, il muro è 3:2 → scala Y (che in object space è Z) per compensare
mapping.inputs["Scale"].default_value = (1.5, 1.5, 1.5)
lk.new(tc.outputs["Generated"], mapping.inputs["Vector"])

# === DIFFUSE (Color) ===
tex_diff = ns.new("ShaderNodeTexImage"); tex_diff.location = (-200, 300)
tex_diff.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_diff_2k.jpg"))
tex_diff.image.colorspace_settings.name = 'sRGB'
tex_diff.projection = 'BOX'
tex_diff.projection_blend = 0.3
lk.new(mapping.outputs["Vector"], tex_diff.inputs["Vector"])

# Leggero color correction: scalda un po' i grigi per sembrare sasso di fiume alpino
hsv = ns.new("ShaderNodeHueSaturation"); hsv.location = (200, 300)
hsv.inputs["Saturation"].default_value = 0.85  # desatura leggermente
hsv.inputs["Value"].default_value = 0.95  # un po' più scuro
lk.new(tex_diff.outputs["Color"], hsv.inputs["Color"])
lk.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

# === ROUGHNESS ===
tex_rough = ns.new("ShaderNodeTexImage"); tex_rough.location = (-200, 0)
tex_rough.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_rough_2k.jpg"))
tex_rough.image.colorspace_settings.name = 'Non-Color'
tex_rough.projection = 'BOX'
tex_rough.projection_blend = 0.3
lk.new(mapping.outputs["Vector"], tex_rough.inputs["Vector"])
lk.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])

# === NORMAL MAP ===
tex_nor = ns.new("ShaderNodeTexImage"); tex_nor.location = (-200, -300)
tex_nor.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_nor_gl_2k.jpg"))
tex_nor.image.colorspace_settings.name = 'Non-Color'
tex_nor.projection = 'BOX'
tex_nor.projection_blend = 0.3
lk.new(mapping.outputs["Vector"], tex_nor.inputs["Vector"])

normal_map = ns.new("ShaderNodeNormalMap"); normal_map.location = (200, -300)
normal_map.inputs["Strength"].default_value = 2.0  # forte per profondità
lk.new(tex_nor.outputs["Color"], normal_map.inputs["Color"])

# === DISPLACEMENT → Bump (per profondità extra) ===
tex_disp = ns.new("ShaderNodeTexImage"); tex_disp.location = (-200, -600)
tex_disp.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_disp_2k.png"))
tex_disp.image.colorspace_settings.name = 'Non-Color'
tex_disp.projection = 'BOX'
tex_disp.projection_blend = 0.3
lk.new(mapping.outputs["Vector"], tex_disp.inputs["Vector"])

bump = ns.new("ShaderNodeBump"); bump.location = (500, -500)
bump.inputs["Strength"].default_value = 0.8  # forte
bump.inputs["Distance"].default_value = 0.04  # 4cm di profondità percepita
lk.new(tex_disp.outputs["Color"], bump.inputs["Height"])
lk.new(normal_map.outputs["Normal"], bump.inputs["Normal"])

# Micro noise aggiuntivo per rugosità singolo sasso
noise_micro = ns.new("ShaderNodeTexNoise"); noise_micro.location = (200, -700)
noise_micro.inputs["Scale"].default_value = 150.0
noise_micro.inputs["Detail"].default_value = 16.0
noise_micro.inputs["Roughness"].default_value = 0.8
lk.new(mapping.outputs["Vector"], noise_micro.inputs["Vector"])

bump2 = ns.new("ShaderNodeBump"); bump2.location = (700, -600)
bump2.inputs["Strength"].default_value = 0.05
bump2.inputs["Distance"].default_value = 0.002
lk.new(noise_micro.outputs["Fac"], bump2.inputs["Height"])
lk.new(bump.outputs["Normal"], bump2.inputs["Normal"])

lk.new(bump2.outputs["Normal"], bsdf.inputs["Normal"])

# Assegna materiale
obj.data.materials.append(mat)

# ============================================================
# PIANO TERRA
# ============================================================
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object; ground.name = "Ground"
mat_g = bpy.data.materials.new("Ground"); mat_g.use_nodes = True
bsdf_g = mat_g.node_tree.nodes["Principled BSDF"]
bsdf_g.inputs["Base Color"].default_value = (0.25, 0.28, 0.20, 1)  # terra/erba
bsdf_g.inputs["Roughness"].default_value = 0.95
ground.data.materials.append(mat_g)

# ============================================================
# CAMERA — 50mm, vista 3/4 per mostrare la profondità
# ============================================================
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50
cam_data.sensor_width = 36; cam_data.clip_end = 100
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
# Vista leggermente di 3/4 per mostrare la profondità dei sassi
cam.location = (1.0, -3.5, 1.3)

target = bpy.data.objects.new("CamTarget", None)
bpy.context.collection.objects.link(target)
target.location = (0, 0, 1.0)
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'
bpy.context.scene.camera = cam

# ============================================================
# ILLUMINAZIONE — sole laterale per micro-ombre sui sassi
# ============================================================
world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
wnt = world.node_tree
for n in wnt.nodes: wnt.nodes.remove(n)

w_out = wnt.nodes.new("ShaderNodeOutputWorld"); w_out.location = (400, 0)
w_bg = wnt.nodes.new("ShaderNodeBackground"); w_bg.location = (200, 0)
w_bg.inputs["Strength"].default_value = 0.7
wnt.links.new(w_bg.outputs["Background"], w_out.inputs["Surface"])

w_sky = wnt.nodes.new("ShaderNodeTexSky"); w_sky.location = (0, 0)
w_sky.sky_type = 'HOSEK_WILKIE'
w_sky.turbidity = 3.0
w_sky.sun_direction = (0.4, -0.6, 0.35)  # sole basso, laterale sx
wnt.links.new(w_sky.outputs["Color"], w_bg.inputs["Color"])

# Sun lamp — laterale basso → ombre nette sui sassi sporgenti
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.5
sun_data.angle = 0.012  # sole piccolo = ombre nette
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), math.radians(12), math.radians(-40))

# Fill leggera dall'altro lato
fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 8; fill_data.size = 5
fill_data.color = (0.85, 0.88, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (5, 0, 4)
fill.rotation_euler = (math.radians(40), math.radians(30), math.radians(25))

# ============================================================
# RENDER — Cycles, 512 samples
# ============================================================
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
except:
    scene.cycles.device = 'CPU'

scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = OUTPUT

# Color management
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Base Contrast'

print("=" * 60)
print("HomeForge AI — Training: Muro pietra v3 (PBR textures)")
print(f"Output: {OUTPUT}")
print("=" * 60)

start = time.time()
bpy.ops.render.render(write_still=True)
elapsed = time.time() - start
print(f"\nRender completato in {elapsed:.1f}s")
print(f"Salvato: {OUTPUT}")

# Salva il .blend
blend_path = str(Path(__file__).parent / "materials" / "test_stone_wall.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"Blend salvato: {blend_path}")
