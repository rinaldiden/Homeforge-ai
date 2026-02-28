"""
HomeForge AI — Prompt Engineer per Flux
Trasforma decisioni architettoniche L1 in prompt ottimizzati per rendering archviz fotorealistico.
"""

import re
from pathlib import Path


# ── Mappature materiali → descrizioni fotorealistiche ────────────────

MATERIAL_MAP = {
    "sasso locale": "natural rough-cut alpine stone masonry, irregular grey-beige stones with lime mortar joints",
    "pietra locale": "natural rough-cut alpine stone masonry, irregular grey-beige stones with lime mortar joints",
    "piode": "traditional heavy slate stone roof tiles (piode), thick irregular dark grey stone slabs",
    "lose in pietra": "traditional heavy slate stone roof tiles (piode), thick irregular dark grey stone slabs",
    "legno scuro": "dark weathered aged brown wood, matte finish",
    "legno": "natural wood, warm brown tones",
    "vetro": "architectural glass with subtle reflections, triple glazing",
    "alluminio nero": "black anodized aluminum frames, minimal profile",
    "rame brunito": "aged burnished copper, dark brown patina",
}

STYLE_TEMPLATE = (
    "photorealistic architectural photography, professional 8k photo, "
    "shot with Canon EOS R5 and 24-70mm f/2.8 lens, "
    "natural overcast alpine lighting, soft shadows, "
    "Italian Alps Valtellina valley background with mountains, "
    "autumn atmosphere, crisp air"
)

NEGATIVE_CONCEPTS = (
    "cartoon, illustration, 3d render, CGI look, plastic, "
    "oversaturated, unrealistic colors, blurry, low quality"
)


class PromptEngineerFlux:
    """Genera prompt Flux ottimizzati dalle decisioni architettoniche L1."""

    def __init__(self, chain_dir=None):
        if chain_dir is None:
            chain_dir = Path(__file__).parent / "chain"
        self.chain_dir = Path(chain_dir)

    def read_l1_decisions(self):
        """Legge e parsa L1_architect_decisions.md."""
        l1_path = self.chain_dir / "L1_architect_decisions.md"
        if not l1_path.exists():
            raise FileNotFoundError(f"L1 decisions non trovate: {l1_path}")
        return l1_path.read_text(encoding="utf-8")

    def extract_building_info(self, l1_text):
        """Estrae informazioni chiave dal markdown L1."""
        info = {
            "dimensions": "",
            "materials": [],
            "roof_type": "",
            "windows": [],
            "special_elements": [],
            "view_point": "",
        }

        # Dimensioni
        m = re.search(r"Pianta:\s*([\d.]+)\s*[×x]\s*([\d.]+)\s*m", l1_text)
        if m:
            info["dimensions"] = f"{m.group(1)}x{m.group(2)}m single story building"

        # Altezze
        m_g = re.search(r"Altezza gronda:\s*([\d.]+)\s*m", l1_text)
        m_c = re.search(r"Altezza colmo:\s*([\d.]+)\s*m", l1_text)
        if m_g and m_c:
            info["dimensions"] += f", {m_g.group(1)}m eaves height, {m_c.group(1)}m ridge height"

        # Materiali
        for keyword, desc in MATERIAL_MAP.items():
            if keyword.lower() in l1_text.lower():
                info["materials"].append(desc)

        # Tetto
        if "asimmetric" in l1_text.lower():
            info["roof_type"] = "asymmetric gabled roof with offset ridge"
        elif "piode" in l1_text.lower():
            info["roof_type"] = "traditional slate stone roof"

        # Vetrata angolo
        if "vetrata angolo" in l1_text.lower() or "corner" in l1_text.lower():
            m = re.search(r"(\d+\.?\d*)\s*[×x]\s*(\d+\.?\d*)\s*m.*angolo", l1_text, re.IGNORECASE)
            if m:
                info["special_elements"].append(
                    f"large corner glazing {m.group(1)}x{m.group(2)}m on southwest corner, "
                    "frameless glass corner joint"
                )

        # Finestre
        windows = re.findall(r"Finestra\s+\w+.*?Dimensioni:\s*([\d.]+\s*[×x]\s*[\d.]+\s*m)", l1_text, re.DOTALL)
        if windows:
            info["windows"] = [f"small traditional window {w}" for w in windows[:3]]

        # Comignolo
        if "comignolo" in l1_text.lower():
            info["special_elements"].append("traditional stone chimney")

        # Travi
        if "travi" in l1_text.lower():
            info["special_elements"].append("exposed dark wood beam ends at eaves")

        # Vista
        m = re.search(r"Punto di vista:\s*(.+?)$", l1_text, re.MULTILINE)
        if m:
            info["view_point"] = m.group(1).strip()

        return info

    def generate_prompt(self, l1_text=None, custom_view=None):
        """
        Genera il prompt Flux completo.

        Args:
            l1_text: Testo L1 (se None, legge da file)
            custom_view: Override per il punto di vista

        Returns:
            dict con 'positive' e 'negative' prompt
        """
        if l1_text is None:
            l1_text = self.read_l1_decisions()

        info = self.extract_building_info(l1_text)

        # Costruisci prompt
        parts = [STYLE_TEMPLATE]

        # Edificio
        if info["dimensions"]:
            parts.append(info["dimensions"])

        # Materiali (deduplica)
        seen = set()
        for mat in info["materials"]:
            if mat not in seen:
                parts.append(mat)
                seen.add(mat)

        # Tetto
        if info["roof_type"]:
            parts.append(info["roof_type"])

        # Elementi speciali
        for elem in info["special_elements"]:
            parts.append(elem)

        # Finestre (riassumi)
        if info["windows"]:
            parts.append(f"{len(info['windows'])} small traditional windows with dark wood frames")

        # Vista
        if custom_view:
            parts.append(custom_view)
        elif info["view_point"]:
            parts.append(f"viewed from {info['view_point']}")

        # Contesto alpino
        parts.append("rural alpine village setting, traditional stone buildings nearby")
        parts.append("green meadow foreground, mountain peaks in background")

        positive = ", ".join(parts)
        return {"positive": positive, "negative": NEGATIVE_CONCEPTS}

    def generate_prompt_for_view(self, view_name, l1_text=None):
        """Genera prompt per una delle 6 viste standard della commissione."""
        views = {
            "V1_via_orti": "aerial view from north looking down, showing only stone and slate roof, traditional village rooftops context",
            "V2_prato_sud": "ground level view from south meadow at 1.6m height, 16m distance, showing full south facade",
            "V3_valle": "distant telephoto view from 600m away in valley, building among village rooftops",
            "V4_nucleo": "street level view from east at 28mm wide angle, showing integration with adjacent stone buildings",
            "V5_prima_dopo": "before and after comparison, same viewpoint showing restoration from ruin to completed building",
            "V6_interno": "interior view through corner glazing looking out at valley, 20mm ultra wide angle",
        }
        custom_view = views.get(view_name, view_name)
        return self.generate_prompt(l1_text=l1_text, custom_view=custom_view)


# ── CLI Test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    engineer = PromptEngineerFlux()
    try:
        result = engineer.generate_prompt()
        print("=== POSITIVE PROMPT ===")
        print(result["positive"])
        print()
        print("=== NEGATIVE PROMPT ===")
        print(result["negative"])
        print()

        # Test viste commissione
        for view in ["V2_prato_sud", "V1_via_orti"]:
            print(f"\n=== {view} ===")
            r = engineer.generate_prompt_for_view(view)
            print(r["positive"][:200] + "...")
    except FileNotFoundError as e:
        print(f"NOTA: {e}")
        print("Generazione prompt demo senza L1...")
        # Demo prompt statico
        demo = (
            f"{STYLE_TEMPLATE}, "
            "11x8m single story alpine stone house, "
            "natural rough-cut stone masonry walls, "
            "traditional heavy slate piode roof, asymmetric gable, "
            "large corner glazing on southwest, dark wood window frames, "
            "exposed wood beam ends at eaves, stone chimney, "
            "viewed from south meadow at eye level, "
            "mountain village setting, green meadow foreground"
        )
        print(demo)
