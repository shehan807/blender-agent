# blender-agent

A domain knowledge layer for AI-assisted molecular visualization and MD trajectory animation in Blender. Built on top of [BlenderMCP](https://github.com/ahujasid/blender-mcp).

Point an AI agent (Claude Code, Cursor, etc.) at this repo, describe what you want to see, and it handles the rest: structure conversion, Blender scripting, rendering, and video assembly.

## What It Does

- **Molecule rendering**: Give it a SMILES string or PDB file, get a publication-quality ball-and-stick render
- **Trajectory animation**: Give it a DCD trajectory + topology, get a movie of your MD simulation
- **Iterative design**: The agent writes Blender scripts, screenshots the result, adjusts, and re-renders until it matches your vision

## Quick Start

```bash
# 1. Clone and set up the Python environment
git clone <this-repo> && cd blender-agent
micromamba create -f environment.yml
micromamba activate blender-agent

# 2. Install the BlenderMCP bridge
pip install blender-mcp

# 3. Launch Blender with the MCP server
./launch_blender.sh

# 4. In a separate terminal, start Claude Code
cd blender-agent
claude
# Inside Claude Code, run:  /mcp
```

That's it. You're connected. Start prompting.

## Setup (Detailed)

### 1. Blender (4.x or 5.x)

Download from [blender.org](https://www.blender.org/download/) or install via `brew install --cask blender`.

### 2. Molecular Nodes Addon

Install inside Blender:
1. Edit > Preferences > Get Extensions
2. Search "Molecular Nodes"
3. Install and enable

### 3. Python Environment

Create the conda/micromamba environment with the scientific packages (RDKit, MDAnalysis, ffmpeg):

```bash
micromamba create -f environment.yml
micromamba activate blender-agent
```

Or with conda:
```bash
conda env create -f environment.yml
conda activate blender-agent
```

### 4. BlenderMCP (MCP Server + Blender Socket Bridge)

BlenderMCP has two parts: a **socket server** that runs inside Blender, and an **MCP server** that Claude Code connects to. This repo bundles both.

**Install the MCP server** (one time, in the blender-agent env):

```bash
pip install blender-mcp
```

**The socket server** (`start_mcp_server.py`) is included in this repo. It gets loaded into Blender automatically by the launch script — no manual addon installation needed.

### 5. Configure Claude Code

The `.mcp.json` file in this repo tells Claude Code how to find the MCP server. After installing `blender-mcp`, find the path to the binary:

```bash
which blender-mcp
```

If the path in `.mcp.json` doesn't match your system, update it:

```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "/path/to/your/blender-mcp",
      "args": []
    }
  }
}
```

If you have `uv` installed, you can use `uvx` instead:

```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

## Usage

### 1. Launch Blender

```bash
./launch_blender.sh
```

This opens Blender and starts the MCP socket server on port 9876. You'll see:

```
Starting Blender with MCP server on port 9876...
MCP server is ready on port 9876.
```

To open an existing .blend file:

```bash
./launch_blender.sh myfile.blend
```

### 2. Start Claude Code

In a separate terminal:

```bash
cd /path/to/blender-agent
claude
```

Once inside Claude Code, reconnect to the MCP server:

```
/mcp
```

Claude will automatically read the `CLAUDE.md` file and understand its available tools and workflows.

### 3. Prompt

**Render a molecule:**
```
Render aspirin as ball-and-stick with a dark background, publication quality
```

**Animate a trajectory:**
```
Here is my MD trajectory at /path/to/simulation.dcd with topology /path/to/system.psf.
Make a 10-second movie, cartoon style for the protein, rotating camera, dark background, 1080p.
```

**Custom visualization:**
```
Load the PDB file at /path/to/protein.pdb, render it cartoon style with
depth of field focused on the active site, warm lighting, cinematic composition.
```

## Troubleshooting

### "Failed to reconnect to blender-mcp"

The MCP server can't reach Blender's socket server. Make sure:
1. Blender was launched with `./launch_blender.sh` (not opened normally)
2. The script printed "MCP server is ready on port 9876"
3. Blender is still running

Test the connection manually:
```bash
python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('localhost',9876)); print('OK'); s.close()"
```

### "command not found: blender-mcp"

The MCP server isn't installed or the path in `.mcp.json` is wrong:
```bash
pip install blender-mcp
which blender-mcp  # Update .mcp.json with this path
```

### Blender addon "Install from Disk" doesn't work (Blender 5.x)

This repo does **not** require installing the BlenderMCP addon manually. The `launch_blender.sh` script loads `start_mcp_server.py` directly into Blender at startup, bypassing the addon system entirely.

## Repository Structure

```
launch_blender.sh          -- Start Blender + MCP server (run this first)
start_mcp_server.py        -- Socket server loaded into Blender by launch script
.mcp.json                  -- Claude Code MCP server config
CLAUDE.md                  -- Agent instructions (workflow, tool routing, rules)
environment.yml            -- Conda/micromamba environment spec
knowledge/                 -- Domain knowledge docs the agent reads on-demand
  molecular_nodes.md       -- Molecular Nodes Python API reference
  blender_pitfalls.md      -- Blender scripting gotchas
  animation.md             -- Keyframing, camera paths, trajectory pipeline
  materials_and_lighting.md -- Shaders, lighting rigs, render settings
scripts/                   -- Local Python scripts (run in conda env)
  smiles_to_pdb.py         -- SMILES string to 3D PDB file
  convert_trajectory.py    -- DCD + topology to multi-model PDB
templates/                 -- Blender script templates (sent via BlenderMCP)
  scene_setup.py           -- Clean scene, camera, lights, renderer
  ball_and_stick.py        -- Molecule render with CPK colors
  trajectory_animation.py  -- Trajectory playback with camera orbit
```

## How It Works

The agent operates across two Python environments:

| Environment | Runs via | Packages |
|---|---|---|
| **Local (conda)** | Bash | RDKit, MDAnalysis, ffmpeg |
| **Blender** | BlenderMCP `execute_blender_code` | bpy, Molecular Nodes |

1. Structure prep (SMILES/DCD conversion) runs locally
2. Blender scripting (scene setup, rendering) runs inside Blender via MCP
3. The agent screenshots the viewport to verify results before final render
4. Video assembly (ffmpeg) runs locally

## License

MIT
