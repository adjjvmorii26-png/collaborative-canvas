import random, math, os, hashlib

PASSES = [
    {"id": "pulse-01", "name": "Virtual Pulse", "rarity": "common", "price": 25, "color": "#22d3a8"},
    {"id": "pulse-02", "name": "Symbiont Node", "rarity": "common", "price": 25, "color": "#22d3a8"},
    {"id": "pulse-03", "name": "Synapse Weaver", "rarity": "uncommon", "price": 50, "color": "#60a5fa"},
    {"id": "pulse-04", "name": "Membrane Rider", "rarity": "uncommon", "price": 50, "color": "#60a5fa"},
    {"id": "pulse-05", "name": "Organism Core", "rarity": "rare", "price": 100, "color": "#fbbf24"},
    {"id": "pulse-06", "name": "Genesis Pulse", "rarity": "mythic", "price": 250, "color": "#a78bfa"},
]

SIZE = 400
CX, CY = SIZE // 2, SIZE // 2

def seed_from_id(pass_id):
    return int(hashlib.sha256(pass_id.encode()).hexdigest()[:8], 16)

def gen_svg(p):
    rng = random.Random(seed_from_id(p["id"]))
    color = p["color"]
    rings = rng.randint(3, 7)
    nodes = rng.randint(5, 12)
    edges = []
    node_positions = []
    for i in range(nodes):
        angle = (2 * math.pi * i / nodes) + rng.uniform(-0.3, 0.3)
        dist = rng.uniform(60, 150)
        x = CX + dist * math.cos(angle)
        y = CY + dist * math.sin(angle)
        node_positions.append((x, y))

    edge_lines = []
    for i in range(nodes):
        for j in range(i + 1, nodes):
            dx = node_positions[i][0] - node_positions[j][0]
            dy = node_positions[i][1] - node_positions[j][1]
            d = math.sqrt(dx * dx + dy * dy)
            if d < 120 and rng.random() < 0.5:
                edge_lines.append((i, j))

    rings_svg = ""
    for r in range(1, rings + 1):
        radius = 40 + r * 22
        opacity = 0.15 + rng.uniform(0, 0.25)
        rings_svg += f'    <circle cx="{CX}" cy="{CY}" r="{radius}" fill="none" stroke="{color}" stroke-width="1" opacity="{opacity}" />\n'

    edges_svg = ""
    for i, j in edge_lines:
        x1, y1 = node_positions[i]
        x2, y2 = node_positions[j]
        edges_svg += f'    <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="0.8" opacity="0.25" />\n'

    nodes_svg = ""
    for x, y in node_positions:
        r = rng.uniform(3, 6)
        nodes_svg += f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}" opacity="0.8" />\n'

    glow = f'    <circle cx="{CX}" cy="{CY}" r="25" fill="{color}" opacity="0.12" />\n'
    core = f'    <circle cx="{CX}" cy="{CY}" r="8" fill="{color}" opacity="0.9" />\n'

    label_y = SIZE - 30
    rarity_colors = {"common": "#5b6b85", "uncommon": "#60a5fa", "rarity": "#fbbf24", "rare": "#fbbf24", "mythic": "#a78bfa"}
    rarity_color = rarity_colors.get(p["rarity"], "#5b6b85")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">
  <defs>
    <radialGradient id="bg-{p['id']}" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#0a0e17" stop-opacity="0" />
    </radialGradient>
  </defs>
  <rect width="{SIZE}" height="{SIZE}" rx="20" fill="#0d1320" />
  <rect width="{SIZE}" height="{SIZE}" rx="20" fill="url(#bg-{p['id']})" />
  {rings_svg}{edges_svg}{nodes_svg}{glow}{core}
  <text x="{CX}" y="{label_y}" text-anchor="middle" fill="{rarity_color}" font-family="monospace" font-size="11" font-weight="bold" opacity="0.9">{p["rarity"].upper()}</text>
</svg>'''
    return svg

outdir = os.path.join(os.path.dirname(__file__), "..", "public", "nft")
os.makedirs(outdir, exist_ok=True)
for p in PASSES:
    svg = gen_svg(p)
    path = os.path.join(outdir, f"{p['id']}.svg")
    with open(path, "w") as f:
        f.write(svg)
    print(f"wrote {path}")
