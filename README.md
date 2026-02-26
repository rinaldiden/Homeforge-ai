# 🏠 HomeForge AI

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Blender](https://img.shields.io/badge/Blender-5.0-orange.svg)](https://www.blender.org/)
[![Claude](https://img.shields.io/badge/Claude-Opus_4-purple.svg)](https://claude.ai)

**AI-powered multi-agent system that helps you design and build your house.**

HomeForge AI is an open-source team of **6 specialized AI agents** + a **4-level render chain** that work together to help you design, engineer, and get approval for your house construction project. Upload your site data and the agents produce structural calculations, energy compliance, landscape documents, and photorealistic 3D renders via Blender.

---

## The 6 Project Agents

| # | Agent | Role | Output |
|---|-------|------|--------|
| 🔩 | **Structural Engineer** | Steel frame design, laser-cut joints, load analysis | Calculations, SVG drawings, FEM input |
| ⚡ | **Energy Engineer** | nZEB compliance, PV sizing, HVAC design | Energy report (Law 10), energy balance |
| 🏛️ | **Architect** | Space planning, material choices, facades | Floor plans, elevations, general project |
| 🏔️ | **Landscape Commission** | Heritage compliance, visual impact assessment | Landscape report (DPCM), photo insertions |
| 📐 | **Surveyor** | Zoning, permits, bureaucracy, timelines | Permit strategy, fee estimates |
| 🎨 | **3D Renderer** | Photorealistic renders with Blender 5.0 | PNG renders, photo composites |

## The Render Chain

The 3D Renderer agent uses a 4-level pipeline to generate photorealistic renders:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                             │
│         "Render the house from the south meadow"            │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │  L1 — ARCHITECT         │
          │  Interprets request     │
          │  Makes design decisions │
          │  Checks constraints     │
          └────────────┬────────────┘
                       │  architect_decisions.md
          ┌────────────▼────────────┐
          │  L2 — GEOMETRY          │
          │  3D coordinates         │
          │  Wall centers, openings │
          │  Roof vertices, camera  │
          └────────────┬────────────┘
                       │  geometry_spec.md
          ┌────────────▼────────────┐
          │  L3 — TRANSLATOR        │
          │  Blender bpy operations │
          │  Material node trees    │
          │  Modifier stack order   │
          └────────────┬────────────┘
                       │  blender_ops.md
          ┌────────────▼────────────┐
          │  L4 — EXECUTOR          │
          │  Complete Python script │
          │  Runs in Blender 5.0   │
          │  Pixel-based composite  │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │      OUTPUT             │
          │  render_model.png       │
          │  1_render.png (composite│
          │  on real site photo)    │
          └─────────────────────────┘
```

## How It Works

HomeForge AI uses a **persistent knowledge base** that stores all real project data — cadastral info, structural calculations, energy specs, and document status. Every agent reads this shared knowledge before acting.

```
1. You provide: site photos, cadastral data, zoning info, your requirements
2. Knowledge base: agents store and update shared project data
3. Agents work: in parallel where possible, sequentially where needed
4. Conflict resolution: most restrictive constraint wins
5. Output: professional documents + photorealistic renders
```

### Core Principles

- **Outside = 100% tradition.** Stone walls, slate roof, dark wood — heritage compliance.
- **Inside = 100% innovation.** Hidden steel frame, triple glazing, nZEB energy class.
- **Knowledge-first.** Every agent reads the shared knowledge base before acting.
- **Iterative.** Change a decision → only affected levels re-run, not the whole chain.

## Quick Start

### Prerequisites

- [Blender 5.0+](https://www.blender.org/download/) — for 3D rendering
- [Claude Desktop](https://claude.ai/download) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — to run the agents
- Python 3.10+ (bundled with Blender)

### Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/rinaldiden/Homeforge-ai.git
   cd Homeforge-ai
   ```

2. **Add your project data** to `knowledge/`:
   - `00-sito-progetto.md` — site location, zoning, constraints
   - `01-calcoli-strutturali.md` — structural parameters
   - `02-dati-energetici.md` — energy targets
   - `03-documenti-prodotti.md` — document status tracker

3. **Add site photos** to `photos/` for photo insertion renders.

4. **Load the skill** in Claude Desktop or Claude Code:
   - Point Claude to the `SKILL.md` file as a teammate/skill
   - Or copy the project folder and reference it in your conversation

5. **Start designing:**
   ```
   "Generate the complete project for my house"
   "Render the house from the south meadow with photo insertion"
   "Calculate the structural frame"
   "Prepare the landscape report for the commission"
   ```

### Running a Render Manually

```bash
blender --background --python chain/L4_script.py
```

The script is fully autonomous — it creates geometry, materials, camera, lighting, renders, and composites the result on the site photo.

## Project Structure

```
homeforge-ai/
├── SKILL.md                    # Orchestrator — routes requests to agents
├── README.md
├── LICENSE
│
├── agents/                     # Render chain agent definitions
│   ├── L1_architect.md         #   Natural language → design decisions
│   ├── L2_geometry.md          #   Decisions → 3D coordinates
│   ├── L3_translator.md        #   Coordinates → Blender operations
│   └── L4_executor.md          #   Operations → Python script + execution
│
├── references/                 # Project agent definitions
│   ├── 01-strutturista.md      #   Structural engineer
│   ├── 02-energy.md            #   Energy engineer
│   ├── 03-architetto.md        #   Architect
│   ├── 04-commissione.md       #   Landscape commission
│   ├── 05-geometra.md          #   Surveyor / admin
│   └── 06-render-blender.md    #   3D render specs
│
├── knowledge/                  # Persistent project data (shared by all agents)
│   ├── 00-sito-progetto.md     #   Site, cadastral, zoning, constraints
│   ├── 01-calcoli-strutturali.md #  Structural calculations
│   ├── 02-dati-energetici.md   #   Energy data
│   └── 03-documenti-prodotti.md #  Document status tracker
│
├── photos/                     # Site photos for photo insertion
├── chain/                      # Render chain intermediate files (runtime)
├── output/                     # Final renders
│
└── deliverables/               # Generated project documents
    ├── 01-progetto-generale/   #   Master project document (DOCX)
    ├── 02-calcoli-strutturali/ #   Structural calculations (DOCX)
    ├── 03-tavole-strutturali/  #   Structural drawings (SVG)
    ├── 04-geotecnica-FEM/      #   Geotechnics + FEM input (DOCX)
    ├── 05-planimetrie-prospetti/ # Floor plans + elevations (SVG)
    ├── 06-legge10-energia/     #   Energy report (DOCX)
    ├── 07-relazione-paesaggistica/ # Landscape report (DOCX)
    ├── 08-render-fotoinserimenti/  # Renders + photo insertions (PNG)
    ├── 09-computo-metrico/     #   Cost estimate (DOCX)
    └── 10-concept-board/       #   Interactive dashboard (JSX)
```

## Blender 5.0 Compatibility

HomeForge AI is built for **Blender 5.0** and handles its breaking API changes:

| Issue | Fix |
|-------|-----|
| `scene.node_tree` removed | Pixel-based compositing via `bpy.data.images` |
| `NISHITA` sky type removed | Uses `HOSEK_WILKIE` with `sun_direction` |
| Boolean solver `FAST` removed | Uses `EXACT` solver |
| `Material.use_nodes` deprecated | Still works, will be removed in 6.0 |

## Example Output

The render pipeline produces:
- **Model render** (RGBA with transparent background)
- **Photo composite** (model alpha-composited over real site photo)

The system generates procedural materials:
- **Stone walls** — Voronoi DISTANCE_TO_EDGE for individual stones with mortar lines
- **Slate roof (piode)** — Voronoi pattern with bump mapping
- **Glass** — Fresnel-based reflections mixing Glass BSDF + metallic Principled
- **Dark wood** — For frames and eave beams

## Adapting to Your Project

1. Replace `knowledge/*.md` files with your project data
2. Replace `photos/` with your site photos
3. Update building dimensions in `SKILL.md` (search for "Parametri edificio FISSI")
4. Update agent references in `references/` for your local building codes
5. Run the pipeline

The system is designed for **Italian alpine heritage zones** (NAF — Nuclei di Antica Formazione) but the agent architecture works for any building project by swapping the knowledge base and reference files.

## Contributing

Contributions are welcome! Areas where help is needed:

- Support for more building codes (beyond Italian NTC 2018)
- Additional procedural materials (brick, concrete, metal cladding)
- GPU-accelerated compositing (current pixel loop is slow for large images)
- Blender 6.0 compatibility when released
- MCP (Model Context Protocol) integration for live Blender control

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Claude](https://claude.ai) by Anthropic
- 3D rendering powered by [Blender](https://www.blender.org/)
- Inspired by the LL3M multi-agent pattern (Planner → Coder → Critic → Verifier)
- Project: Ca' del Papa, Mazzo di Valtellina (SO), Italy
