"""
HomeForge AI — Training: Tetto in legno + piode + rame — v4
Fix v3: rame molto più scuro (bruno/verde scuro reale), piode con mapping
corretto per effetto tegola, travi sotto-gronda visibili con luce fill,
pluviale più grosso, sottotetto migliorato
"""
import bpy, bmesh, math, time
from pathlib import Path
from mathutils import Vector

PROJ = Path(__file__).parent.parent
TEX_DIR = Path(__file__).parent / "materials" / "textures"
OUTPUT = str(PROJ / "output" / "training_tetto_final.png")

# === CLEAR ===
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in bpy.data.meshes: bpy.data.meshes.remove(m)
for m in bpy.data.materials: bpy.data.materials.remove(m)
for img in bpy.data.images: bpy.data.images.remove(img)

# ============================================================
# MATERIALE 1: PIODE (patterned_slate_tiles)
# ============================================================
mat_piode = bpy.data.materials.new("Piode_PBR")
mat_piode.use_nodes = True
mat_piode.displacement_method = 'BUMP'
nt = mat_piode.node_tree
ns = nt.nodes; lk = nt.links
for n in ns: ns.remove(n)

out_p = ns.new("ShaderNodeOutputMaterial"); out_p.location = (1200, 0)
bsdf_p = ns.new("ShaderNodeBsdfPrincipled"); bsdf_p.location = (800, 0)
lk.new(bsdf_p.outputs["BSDF"], out_p.inputs["Surface"])

tc_p = ns.new("ShaderNodeTexCoord"); tc_p.location = (-800, 0)
map_p = ns.new("ShaderNodeMapping"); map_p.location = (-600, 0)
# Piode: scala media, rotazione 45° per rompere il pattern diagonale
map_p.inputs["Scale"].default_value = (3.0, 3.0, 3.0)
map_p.inputs["Rotation"].default_value = (0, 0, math.radians(90))  # ruota per allineare orizzontale
lk.new(tc_p.outputs["Generated"], map_p.inputs["Vector"])

tex_pd = ns.new("ShaderNodeTexImage"); tex_pd.location = (-200, 300)
tex_pd.image = bpy.data.images.load(str(TEX_DIR / "patterned_slate_tiles_diff_2k.jpg"))
tex_pd.image.colorspace_settings.name = 'sRGB'
tex_pd.projection = 'BOX'; tex_pd.projection_blend = 0.3
lk.new(map_p.outputs["Vector"], tex_pd.inputs["Vector"])

hsv_p = ns.new("ShaderNodeHueSaturation"); hsv_p.location = (200, 300)
hsv_p.inputs["Saturation"].default_value = 0.55   # molto desaturata — piode grigie
hsv_p.inputs["Value"].default_value = 0.70         # scure
lk.new(tex_pd.outputs["Color"], hsv_p.inputs["Color"])
lk.new(hsv_p.outputs["Color"], bsdf_p.inputs["Base Color"])

tex_pr = ns.new("ShaderNodeTexImage"); tex_pr.location = (-200, 0)
tex_pr.image = bpy.data.images.load(str(TEX_DIR / "patterned_slate_tiles_rough_2k.jpg"))
tex_pr.image.colorspace_settings.name = 'Non-Color'
tex_pr.projection = 'BOX'; tex_pr.projection_blend = 0.3
lk.new(map_p.outputs["Vector"], tex_pr.inputs["Vector"])
lk.new(tex_pr.outputs["Color"], bsdf_p.inputs["Roughness"])

tex_pn = ns.new("ShaderNodeTexImage"); tex_pn.location = (-200, -300)
tex_pn.image = bpy.data.images.load(str(TEX_DIR / "patterned_slate_tiles_nor_gl_2k.jpg"))
tex_pn.image.colorspace_settings.name = 'Non-Color'
tex_pn.projection = 'BOX'; tex_pn.projection_blend = 0.3
lk.new(map_p.outputs["Vector"], tex_pn.inputs["Vector"])

nmap_p = ns.new("ShaderNodeNormalMap"); nmap_p.location = (200, -300)
nmap_p.inputs["Strength"].default_value = 2.5  # molto forte per profondità lastre
lk.new(tex_pn.outputs["Color"], nmap_p.inputs["Color"])

tex_pdisp = ns.new("ShaderNodeTexImage"); tex_pdisp.location = (-200, -600)
tex_pdisp.image = bpy.data.images.load(str(TEX_DIR / "patterned_slate_tiles_disp_2k.png"))
tex_pdisp.image.colorspace_settings.name = 'Non-Color'
tex_pdisp.projection = 'BOX'; tex_pdisp.projection_blend = 0.3
lk.new(map_p.outputs["Vector"], tex_pdisp.inputs["Vector"])

bump_p = ns.new("ShaderNodeBump"); bump_p.location = (500, -500)
bump_p.inputs["Strength"].default_value = 1.0
bump_p.inputs["Distance"].default_value = 0.05
lk.new(tex_pdisp.outputs["Color"], bump_p.inputs["Height"])
lk.new(nmap_p.outputs["Normal"], bump_p.inputs["Normal"])

noise_p = ns.new("ShaderNodeTexNoise"); noise_p.location = (200, -750)
noise_p.inputs["Scale"].default_value = 100.0
noise_p.inputs["Detail"].default_value = 12.0
lk.new(map_p.outputs["Vector"], noise_p.inputs["Vector"])

bump_p2 = ns.new("ShaderNodeBump"); bump_p2.location = (700, -600)
bump_p2.inputs["Strength"].default_value = 0.04
bump_p2.inputs["Distance"].default_value = 0.001
lk.new(noise_p.outputs["Fac"], bump_p2.inputs["Height"])
lk.new(bump_p.outputs["Normal"], bump_p2.inputs["Normal"])
lk.new(bump_p2.outputs["Normal"], bsdf_p.inputs["Normal"])

# ============================================================
# MATERIALE 2: LEGNO TRAVI
# ============================================================
mat_legno = bpy.data.materials.new("Legno_Travi_PBR")
mat_legno.use_nodes = True
mat_legno.displacement_method = 'BUMP'
nt2 = mat_legno.node_tree
ns2 = nt2.nodes; lk2 = nt2.links
for n in ns2: ns2.remove(n)

out_l = ns2.new("ShaderNodeOutputMaterial"); out_l.location = (1200, 0)
bsdf_l = ns2.new("ShaderNodeBsdfPrincipled"); bsdf_l.location = (800, 0)
lk2.new(bsdf_l.outputs["BSDF"], out_l.inputs["Surface"])

tc_l = ns2.new("ShaderNodeTexCoord"); tc_l.location = (-800, 0)
map_l = ns2.new("ShaderNodeMapping"); map_l.location = (-600, 0)
map_l.inputs["Scale"].default_value = (3.0, 0.8, 3.0)
lk2.new(tc_l.outputs["Generated"], map_l.inputs["Vector"])

tex_ld = ns2.new("ShaderNodeTexImage"); tex_ld.location = (-200, 300)
tex_ld.image = bpy.data.images.load(str(TEX_DIR / "weathered_brown_planks_diff_2k.jpg"))
tex_ld.image.colorspace_settings.name = 'sRGB'
tex_ld.projection = 'BOX'; tex_ld.projection_blend = 0.3
lk2.new(map_l.outputs["Vector"], tex_ld.inputs["Vector"])

hsv_l = ns2.new("ShaderNodeHueSaturation"); hsv_l.location = (200, 300)
hsv_l.inputs["Saturation"].default_value = 0.65
hsv_l.inputs["Value"].default_value = 0.55
lk2.new(tex_ld.outputs["Color"], hsv_l.inputs["Color"])
lk2.new(hsv_l.outputs["Color"], bsdf_l.inputs["Base Color"])

tex_lr = ns2.new("ShaderNodeTexImage"); tex_lr.location = (-200, 0)
tex_lr.image = bpy.data.images.load(str(TEX_DIR / "weathered_brown_planks_rough_2k.jpg"))
tex_lr.image.colorspace_settings.name = 'Non-Color'
tex_lr.projection = 'BOX'; tex_lr.projection_blend = 0.3
lk2.new(map_l.outputs["Vector"], tex_lr.inputs["Vector"])
lk2.new(tex_lr.outputs["Color"], bsdf_l.inputs["Roughness"])

tex_ln = ns2.new("ShaderNodeTexImage"); tex_ln.location = (-200, -300)
tex_ln.image = bpy.data.images.load(str(TEX_DIR / "weathered_brown_planks_nor_gl_2k.jpg"))
tex_ln.image.colorspace_settings.name = 'Non-Color'
tex_ln.projection = 'BOX'; tex_ln.projection_blend = 0.3
lk2.new(map_l.outputs["Vector"], tex_ln.inputs["Vector"])
nmap_l = ns2.new("ShaderNodeNormalMap"); nmap_l.location = (200, -300)
nmap_l.inputs["Strength"].default_value = 2.0
lk2.new(tex_ln.outputs["Color"], nmap_l.inputs["Color"])

tex_ldisp = ns2.new("ShaderNodeTexImage"); tex_ldisp.location = (-200, -600)
tex_ldisp.image = bpy.data.images.load(str(TEX_DIR / "weathered_brown_planks_disp_2k.png"))
tex_ldisp.image.colorspace_settings.name = 'Non-Color'
tex_ldisp.projection = 'BOX'; tex_ldisp.projection_blend = 0.3
lk2.new(map_l.outputs["Vector"], tex_ldisp.inputs["Vector"])
bump_l = ns2.new("ShaderNodeBump"); bump_l.location = (500, -500)
bump_l.inputs["Strength"].default_value = 0.7
bump_l.inputs["Distance"].default_value = 0.015
lk2.new(tex_ldisp.outputs["Color"], bump_l.inputs["Height"])
lk2.new(nmap_l.outputs["Normal"], bump_l.inputs["Normal"])
lk2.new(bump_l.outputs["Normal"], bsdf_l.inputs["Normal"])

# ============================================================
# MATERIALE 3: RAME BRUNITO — v6: rame semi-ossidato bruno/marrone scuro
# Rame alpino tipico: non verde-rame, ma bruno scuro con macchie
# ============================================================
mat_rame = bpy.data.materials.new("Rame_Brunito")
mat_rame.use_nodes = True
nt3 = mat_rame.node_tree
ns3 = nt3.nodes; lk3 = nt3.links
for n in ns3: ns3.remove(n)

out_r = ns3.new("ShaderNodeOutputMaterial"); out_r.location = (1400, 0)
bsdf_r = ns3.new("ShaderNodeBsdfPrincipled"); bsdf_r.location = (1000, 0)
bsdf_r.inputs["Metallic"].default_value = 0.95  # rame è sempre metallico
bsdf_r.inputs["Roughness"].default_value = 0.35  # semi-lucido
lk3.new(bsdf_r.outputs["BSDF"], out_r.inputs["Surface"])

tc_r = ns3.new("ShaderNodeTexCoord"); tc_r.location = (-800, 0)
map_r = ns3.new("ShaderNodeMapping"); map_r.location = (-600, 0)
map_r.inputs["Scale"].default_value = (10.0, 10.0, 10.0)
lk3.new(tc_r.outputs["Generated"], map_r.inputs["Vector"])

# Noise per variazione colore
noise_r = ns3.new("ShaderNodeTexNoise"); noise_r.location = (-300, 200)
noise_r.inputs["Scale"].default_value = 6.0
noise_r.inputs["Detail"].default_value = 10.0
noise_r.inputs["Roughness"].default_value = 0.6
lk3.new(map_r.outputs["Vector"], noise_r.inputs["Vector"])

# ColorRamp: SOLO toni rame brunito (NO verde!)
# Rame dopo 5-15 anni: marrone scuro con zone più chiare
ramp_r = ns3.new("ShaderNodeValToRGB"); ramp_r.location = (200, 200)
ramp_r.color_ramp.elements[0].position = 0.20
ramp_r.color_ramp.elements[0].color = (0.55, 0.30, 0.15, 1.0)   # rame caldo chiaro
ramp_r.color_ramp.elements[1].position = 0.50
ramp_r.color_ramp.elements[1].color = (0.35, 0.18, 0.08, 1.0)   # rame bruno medio
el1 = ramp_r.color_ramp.elements.new(0.75)
el1.color = (0.22, 0.12, 0.06, 1.0)   # rame scuro
el2 = ramp_r.color_ramp.elements.new(0.92)
el2.color = (0.15, 0.08, 0.04, 1.0)   # molto scuro
lk3.new(noise_r.outputs["Fac"], ramp_r.inputs["Fac"])
lk3.new(ramp_r.outputs["Color"], bsdf_r.inputs["Base Color"])

# Roughness variabile per effetto usura
ramp_rr = ns3.new("ShaderNodeValToRGB"); ramp_rr.location = (200, -100)
ramp_rr.color_ramp.elements[0].position = 0.25
ramp_rr.color_ramp.elements[0].color = (0.20, 0.20, 0.20, 1.0)  # lucido
ramp_rr.color_ramp.elements[1].position = 0.70
ramp_rr.color_ramp.elements[1].color = (0.50, 0.50, 0.50, 1.0)  # opaco
lk3.new(noise_r.outputs["Fac"], ramp_rr.inputs["Fac"])
lk3.new(ramp_rr.outputs["Color"], bsdf_r.inputs["Roughness"])

# Bump sottile — rame è liscio ma con piccole imperfezioni
bump_r = ns3.new("ShaderNodeBump"); bump_r.location = (600, -300)
bump_r.inputs["Strength"].default_value = 0.15
bump_r.inputs["Distance"].default_value = 0.003
noise_micro = ns3.new("ShaderNodeTexNoise"); noise_micro.location = (200, -400)
noise_micro.inputs["Scale"].default_value = 100.0
noise_micro.inputs["Detail"].default_value = 14.0
lk3.new(map_r.outputs["Vector"], noise_micro.inputs["Vector"])
lk3.new(noise_micro.outputs["Fac"], bump_r.inputs["Height"])
lk3.new(bump_r.outputs["Normal"], bsdf_r.inputs["Normal"])

# ============================================================
# MATERIALE 4: MURO PIETRA (rock_wall_08)
# ============================================================
mat_muro = bpy.data.materials.new("Pietra_Muro")
mat_muro.use_nodes = True
mat_muro.displacement_method = 'BUMP'
nt4 = mat_muro.node_tree
ns4 = nt4.nodes; lk4 = nt4.links
for n in ns4: ns4.remove(n)

out_m = ns4.new("ShaderNodeOutputMaterial"); out_m.location = (1200, 0)
bsdf_m = ns4.new("ShaderNodeBsdfPrincipled"); bsdf_m.location = (800, 0)
lk4.new(bsdf_m.outputs["BSDF"], out_m.inputs["Surface"])

tc_m = ns4.new("ShaderNodeTexCoord"); tc_m.location = (-800, 0)
map_m = ns4.new("ShaderNodeMapping"); map_m.location = (-600, 0)
map_m.inputs["Scale"].default_value = (1.5, 1.5, 1.5)
lk4.new(tc_m.outputs["Generated"], map_m.inputs["Vector"])

tex_md = ns4.new("ShaderNodeTexImage"); tex_md.location = (-200, 300)
tex_md.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_diff_2k.jpg"))
tex_md.image.colorspace_settings.name = 'sRGB'
tex_md.projection = 'BOX'; tex_md.projection_blend = 0.3
lk4.new(map_m.outputs["Vector"], tex_md.inputs["Vector"])

hsv_m = ns4.new("ShaderNodeHueSaturation"); hsv_m.location = (200, 300)
hsv_m.inputs["Saturation"].default_value = 0.85
hsv_m.inputs["Value"].default_value = 0.95
lk4.new(tex_md.outputs["Color"], hsv_m.inputs["Color"])
lk4.new(hsv_m.outputs["Color"], bsdf_m.inputs["Base Color"])

tex_mr = ns4.new("ShaderNodeTexImage"); tex_mr.location = (-200, 0)
tex_mr.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_rough_2k.jpg"))
tex_mr.image.colorspace_settings.name = 'Non-Color'
tex_mr.projection = 'BOX'; tex_mr.projection_blend = 0.3
lk4.new(map_m.outputs["Vector"], tex_mr.inputs["Vector"])
lk4.new(tex_mr.outputs["Color"], bsdf_m.inputs["Roughness"])

tex_mn = ns4.new("ShaderNodeTexImage"); tex_mn.location = (-200, -300)
tex_mn.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_nor_gl_2k.jpg"))
tex_mn.image.colorspace_settings.name = 'Non-Color'
tex_mn.projection = 'BOX'; tex_mn.projection_blend = 0.3
lk4.new(map_m.outputs["Vector"], tex_mn.inputs["Vector"])
nmap_m = ns4.new("ShaderNodeNormalMap"); nmap_m.location = (200, -300)
nmap_m.inputs["Strength"].default_value = 2.0
lk4.new(tex_mn.outputs["Color"], nmap_m.inputs["Color"])

tex_mdisp = ns4.new("ShaderNodeTexImage"); tex_mdisp.location = (-200, -600)
tex_mdisp.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_disp_2k.png"))
tex_mdisp.image.colorspace_settings.name = 'Non-Color'
tex_mdisp.projection = 'BOX'; tex_mdisp.projection_blend = 0.3
lk4.new(map_m.outputs["Vector"], tex_mdisp.inputs["Vector"])
bump_m = ns4.new("ShaderNodeBump"); bump_m.location = (500, -500)
bump_m.inputs["Strength"].default_value = 0.8
bump_m.inputs["Distance"].default_value = 0.04
lk4.new(tex_mdisp.outputs["Color"], bump_m.inputs["Height"])
lk4.new(nmap_m.outputs["Normal"], bump_m.inputs["Normal"])
lk4.new(bump_m.outputs["Normal"], bsdf_m.inputs["Normal"])

# ============================================================
# GEOMETRIA
# ============================================================
FALDA_L = 5.0
TETTO_W = 4.5
ANGOLO = math.radians(35)
SPORTO = 0.45
PIODE_SP = 0.045
TRAVE_W = 0.22
TRAVE_H = 0.26
TRAVE_SPA = 0.50
TAVOLATO_SP = 0.025
BASE_Z = 2.5

dx = FALDA_L * math.cos(ANGOLO)
dz = FALDA_L * math.sin(ANGOLO)

# --- MURO FRONTALE ---
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(TETTO_W/2, 0.225, BASE_Z/2))
muro = bpy.context.active_object; muro.name = "MuroFrontale"
muro.scale = (TETTO_W + 0.10, 0.45, BASE_Z)
bpy.ops.object.transform_apply(scale=True)
muro.data.materials.append(mat_muro)

# --- MURO LATERALE SX ---
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.175, dx/2, BASE_Z/2 + dz/4))
muro_lat = bpy.context.active_object; muro_lat.name = "MuroLaterale"
muro_lat.scale = (0.45, dx + 0.5, BASE_Z + dz/2)
bpy.ops.object.transform_apply(scale=True)
muro_lat.data.materials.append(mat_muro)

# --- DORMIENTE ---
bpy.ops.mesh.primitive_cube_add(size=1.0)
dorm = bpy.context.active_object; dorm.name = "Dormiente"
dorm.scale = (TETTO_W + 0.10, 0.18, 0.14)
bpy.ops.object.transform_apply(scale=True)
dorm.location = (TETTO_W/2, 0.09, BASE_Z - 0.07)
dorm.data.materials.append(mat_legno)

# --- TRAVI PRINCIPALI (puntoni) ---
n_travi = int(TETTO_W / TRAVE_SPA) + 1
for i in range(n_travi + 1):
    x = i * TRAVE_SPA
    if x > TETTO_W: x = TETTO_W

    bpy.ops.mesh.primitive_cube_add(size=1.0)
    trave = bpy.context.active_object
    trave.name = f"Trave_{i:02d}"
    lunghezza = FALDA_L + SPORTO
    trave.scale = (TRAVE_W, lunghezza, TRAVE_H)
    bpy.ops.object.transform_apply(scale=True)

    mid_local = (FALDA_L - SPORTO) / 2
    mid_y = mid_local * math.cos(ANGOLO)
    mid_z = BASE_Z + mid_local * math.sin(ANGOLO)
    trave.location = (x, mid_y, mid_z)
    trave.rotation_euler = (ANGOLO, 0, 0)
    trave.data.materials.append(mat_legno)

# --- TAVOLATO ---
bpy.ops.mesh.primitive_cube_add(size=1.0)
tav = bpy.context.active_object; tav.name = "Tavolato"
tav.scale = (TETTO_W + 0.06, FALDA_L + SPORTO, TAVOLATO_SP)
bpy.ops.object.transform_apply(scale=True)

mid_local = (FALDA_L - SPORTO) / 2
tav_y = mid_local * math.cos(ANGOLO)
tav_z = BASE_Z + mid_local * math.sin(ANGOLO) + TRAVE_H/2 + TAVOLATO_SP/2
tav.location = (TETTO_W/2, tav_y, tav_z)
tav.rotation_euler = (ANGOLO, 0, 0)
tav.data.materials.append(mat_legno)

# --- PIODE ---
bpy.ops.mesh.primitive_cube_add(size=1.0)
piode = bpy.context.active_object; piode.name = "Piode"
piode.scale = (TETTO_W + 0.14, FALDA_L + SPORTO + 0.06, PIODE_SP)
bpy.ops.object.transform_apply(scale=True)
piode_z = tav_z + TAVOLATO_SP/2 + PIODE_SP/2
piode.location = (TETTO_W/2, tav_y, piode_z)
piode.rotation_euler = (ANGOLO, 0, 0)
piode.data.materials.append(mat_piode)

# --- GRONDAIA RAME (profilo semicircolare) ---
bm = bmesh.new()
gronda_r = 0.10
n_seg = 16
verts_L = []; verts_R = []
for j in range(n_seg + 1):
    a = math.pi * j / n_seg
    yl = gronda_r * math.cos(a)
    zl = -gronda_r * math.sin(a)
    verts_L.append(bm.verts.new((0, yl, zl)))
    verts_R.append(bm.verts.new((TETTO_W + 0.20, yl, zl)))

for j in range(n_seg):
    bm.faces.new([verts_L[j], verts_L[j+1], verts_R[j+1], verts_R[j]])
bm.faces.new(verts_L)
bm.faces.new(list(reversed(verts_R)))

mesh_gr = bpy.data.meshes.new("Grondaia_mesh")
bm.to_mesh(mesh_gr); bm.free()

grondaia = bpy.data.objects.new("Grondaia", mesh_gr)
bpy.context.collection.objects.link(grondaia)
gr_y = -SPORTO * math.cos(ANGOLO) - 0.05
gr_z = BASE_Z - SPORTO * math.sin(ANGOLO) - gronda_r * 0.3
grondaia.location = (-0.10, gr_y, gr_z)
grondaia.data.materials.append(mat_rame)

# --- STAFFETTE ---
n_st = 6
for s in range(n_st):
    sx = 0.2 + s * (TETTO_W - 0.1) / (n_st - 1)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    st = bpy.context.active_object; st.name = f"Staffa_{s:02d}"
    st.scale = (0.025, 0.04, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    st.location = (sx, gr_y, gr_z + gronda_r * 0.8)
    st.data.materials.append(mat_rame)

# --- PLUVIALE (più grosso) ---
bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=BASE_Z * 0.85,
    location=(TETTO_W + 0.06, gr_y + 0.02, BASE_Z * 0.42))
pluv = bpy.context.active_object; pluv.name = "Pluviale"
pluv.data.materials.append(mat_rame)

# Gomito
bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.22,
    location=(TETTO_W + 0.06, gr_y + 0.02, BASE_Z * 0.87))
gomito = bpy.context.active_object; gomito.name = "Gomito"
gomito.rotation_euler = (math.radians(50), 0, 0)
gomito.data.materials.append(mat_rame)

# --- SCOSSALINA COLMO ---
bpy.ops.mesh.primitive_cube_add(size=1.0)
scoss = bpy.context.active_object; scoss.name = "Scossalina"
scoss.scale = (TETTO_W + 0.14, 0.25, 0.003)
bpy.ops.object.transform_apply(scale=True)
scoss_local = FALDA_L + 0.02
scoss_y = scoss_local * math.cos(ANGOLO)
scoss_z = BASE_Z + scoss_local * math.sin(ANGOLO) + TRAVE_H/2 + TAVOLATO_SP + PIODE_SP
scoss.location = (TETTO_W/2, scoss_y, scoss_z)
scoss.rotation_euler = (ANGOLO, 0, 0)
scoss.data.materials.append(mat_rame)

# --- BORDO RAME GRONDA ---
bpy.ops.mesh.primitive_cube_add(size=1.0)
bordo = bpy.context.active_object; bordo.name = "BordoRame"
bordo.scale = (TETTO_W + 0.14, 0.10, 0.002)
bpy.ops.object.transform_apply(scale=True)
bordo_local = -SPORTO - 0.01
bordo_y = bordo_local * math.cos(ANGOLO)
bordo_z = BASE_Z + bordo_local * math.sin(ANGOLO) + TRAVE_H/2 + TAVOLATO_SP + PIODE_SP
bordo.location = (TETTO_W/2, bordo_y, bordo_z)
bordo.rotation_euler = (ANGOLO, 0, 0)
bordo.data.materials.append(mat_rame)

# ============================================================
# PIANO TERRA
# ============================================================
bpy.ops.mesh.primitive_plane_add(size=20, location=(2, 2, 0))
ground = bpy.context.active_object; ground.name = "Ground"
mat_g = bpy.data.materials.new("Ground"); mat_g.use_nodes = True
bsdf_g = mat_g.node_tree.nodes["Principled BSDF"]
bsdf_g.inputs["Base Color"].default_value = (0.22, 0.26, 0.18, 1)
bsdf_g.inputs["Roughness"].default_value = 0.95
ground.data.materials.append(mat_g)

# ============================================================
# CAMERA
# ============================================================
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_data.sensor_width = 36; cam_data.clip_end = 100
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
# Vista dal basso 3/4 — mostra sottotetto, travi, grondaia, piode
cam.location = (-1.5, -5.5, 1.4)

target = bpy.data.objects.new("CamTarget", None)
bpy.context.collection.objects.link(target)
target.location = (2.0, 0.8, BASE_Z + 0.3)
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'
bpy.context.scene.camera = cam

# ============================================================
# ILLUMINAZIONE — sole + fill forte per illuminare sottotetto
# ============================================================
world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
wnt = world.node_tree
for n in wnt.nodes: wnt.nodes.remove(n)

w_out = wnt.nodes.new("ShaderNodeOutputWorld"); w_out.location = (400, 0)
w_bg = wnt.nodes.new("ShaderNodeBackground"); w_bg.location = (200, 0)
w_bg.inputs["Strength"].default_value = 0.9
wnt.links.new(w_bg.outputs["Background"], w_out.inputs["Surface"])

w_sky = wnt.nodes.new("ShaderNodeTexSky"); w_sky.location = (0, 0)
w_sky.sky_type = 'HOSEK_WILKIE'
w_sky.turbidity = 2.5
w_sky.sun_direction = (0.35, -0.5, 0.45)
wnt.links.new(w_sky.outputs["Color"], w_bg.inputs["Color"])

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 5.0
sun_data.angle = 0.012
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(48), math.radians(12), math.radians(-30))

# Fill forte dal basso per illuminare sotto-gronda e travi
fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 20; fill_data.size = 6
fill_data.color = (0.90, 0.92, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-2, -3, 1.0)
fill.rotation_euler = (math.radians(60), math.radians(20), math.radians(10))

# Rim light per bordi
rim_data = bpy.data.lights.new("Rim", 'AREA')
rim_data.energy = 10; rim_data.size = 3
rim_data.color = (1.0, 0.95, 0.88)
rim = bpy.data.objects.new("Rim", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (6, 2, 6)
rim.rotation_euler = (math.radians(55), math.radians(25), math.radians(30))

# ============================================================
# RENDER
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

scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Base Contrast'

print("=" * 60)
print("HomeForge AI — Training: Tetto piode v6")
print(f"Output: {OUTPUT}")
print("=" * 60)

start = time.time()
bpy.ops.render.render(write_still=True)
elapsed = time.time() - start
print(f"\nRender completato in {elapsed:.1f}s")
print(f"Salvato: {OUTPUT}")

# Salva il .blend
blend_path = str(Path(__file__).parent / "materials" / "test_roof_piode.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"Blend salvato: {blend_path}")

# Copia render come preview
import shutil
preview_path = str(Path(__file__).parent / "materials" / "roof_piode_preview.png")
shutil.copy2(OUTPUT, preview_path)
print(f"Preview salvata: {preview_path}")
