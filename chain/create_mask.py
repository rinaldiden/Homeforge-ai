"""
Crea la maschera del rudere dalla foto del sito.
BIANCO = rudere da sostituire
NERO = tutto il resto (prato, alberi, montagne, cielo, edificio adiacente)

La foto è 2040x1530. Il rudere occupa la parte centro-sinistra dell'immagine.
Coordinate stimate analizzando la foto:
- Il rudere inizia da circa x=480 e arriva a x=1220
- Va da circa y=180 (tetto) a y=950 (base muri)
- L'edificio adiacente a destra (con catasta legna) NON va mascherato
- Il prato davanti NON va mascherato
- Bisogna includere: tetto sfondato, muri crepati, vegetazione sul rudere
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# Carica foto
photo_path = "C:/Users/Stramba/casa/homeforge-ai/photos/site_photo.jpg"
output_mask = "C:/Users/Stramba/casa/homeforge-ai/output/mask_rudere.png"

img = Image.open(photo_path)
w, h = img.size  # 2040 x 1530
print(f"Photo: {w}x{h}")

# Crea maschera nera (tutto protetto)
mask = Image.new("L", (w, h), 0)
draw = ImageDraw.Draw(mask)

# Poligono del rudere — coordinate precise dalla foto (2040x1530)
# Il rudere è il corpo principale a sinistra.
# L'edificio adiacente (con catasta legna e tetto scuro) a DESTRA NON va incluso.
# Il rudere ha:
# - Muro sinistro visibile con crepe
# - Tetto parzialmente crollato
# - Facciata frontale con finestre vuote
# - Confine destro dove incontra l'edificio adiacente (~x=1250)
rudere_polygon = [
    # Base sinistra del muro - livello terreno
    (540, 930),
    # Muro sinistro sale
    (540, 700),
    (545, 530),
    # Angolo superiore sinistro muro
    (545, 440),
    # Bordo tetto sinistro
    (520, 420),
    # Tetto sale verso il colmo — seguendo la linea esatta
    (550, 340),
    (620, 260),
    (680, 220),
    # Colmo del tetto
    (740, 200),
    # Tetto scende verso destra
    (850, 210),
    (950, 250),
    (1050, 300),
    (1150, 360),
    # Bordo tetto destro — il rudere continua a destra
    (1250, 400),
    (1350, 350),
    # Confine con l'edificio adiacente (con tetto scuro)
    # L'edificio buono inizia circa a x=1420 con il tetto nero
    (1400, 310),
    # Scendere lungo il confine destro
    (1410, 450),
    (1410, 600),
    (1400, 750),
    (1390, 880),
    # Base destra, livello terreno
    (1390, 930),
    # Chiudi lungo il terreno
    (540, 930),
]

# Disegna il poligono riempito di bianco
draw.polygon(rudere_polygon, fill=255)

# Feathering: sfuma i bordi di 12px per transizione morbida
mask = mask.filter(ImageFilter.GaussianBlur(radius=12))

# Ri-soglia per mantenere la maschera netta al centro ma sfumata ai bordi
mask_arr = np.array(mask, dtype=np.float32)
# Clamp: tutto sopra 200 → 255, tutto sotto 30 → 0, gradiente in mezzo
mask_arr = np.clip((mask_arr - 30) / (200 - 30) * 255, 0, 255).astype(np.uint8)
mask = Image.fromarray(mask_arr)

mask.save(output_mask)
print(f"Mask saved: {output_mask}")

# Verifica: overlay maschera sulla foto
overlay = img.copy()
mask_rgb = Image.merge("RGB", [mask, Image.new("L", (w, h), 0), Image.new("L", (w, h), 0)])
overlay = Image.blend(overlay, mask_rgb, 0.4)
overlay.save(output_mask.replace(".png", "_overlay.png"))
print(f"Overlay saved: {output_mask.replace('.png', '_overlay.png')}")
