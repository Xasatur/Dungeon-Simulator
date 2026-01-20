#!/usr/bin/env python3
"""Dungeon simulator for Das Labyrinth (Pokémon Diamant/Perl/Platin).

This script generates a randomized traversal that respects the dungeon rules:
- After three pillar rooms, the next room is Giratina's room.
- You must not exceed 30 rooms visited or you reset to the entrance.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class DungeonRules:
    max_rooms: int
    pillars: int
    pillar_level_increase: int
    reset_on_overflow: bool


@dataclass(frozen=True)
class DungeonConfig:
    name: str
    game: str
    rules: DungeonRules
    entrance: str
    labyrinth: str
    pillar: str
    boss: str
    entrance_inscription: str
    boss_inscription: str


@dataclass
class Step:
    index: int
    room_type: str
    details: str


@dataclass(frozen=True)
class VisualNode:
    index: int
    room_type: str
    label: str
    x: float
    y: float


def load_config(path: Path) -> DungeonConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = DungeonRules(**data["rules"])
    rooms = data["rooms"]
    inscriptions = data["inscriptions"]
    return DungeonConfig(
        name=data["name"],
        game=data["game"],
        rules=rules,
        entrance=rooms["entrance"],
        labyrinth=rooms["labyrinth"],
        pillar=rooms["pillar"],
        boss=rooms["boss"],
        entrance_inscription=inscriptions["entrance"],
        boss_inscription=inscriptions["boss"],
    )


def generate_labyrinth_lengths(rng: random.Random, pillars: int) -> list[int]:
    """Generate a random distribution of labyrinth rooms between pillars.

    Ensures each segment has at least 1 room and a reasonable spread so
    traversal feels like a maze rather than a straight line.
    """

    remaining = rng.randint(6, 18)
    lengths = []
    for i in range(pillars + 1):
        if i == pillars:
            lengths.append(max(1, remaining))
            break
        max_for_segment = max(1, remaining - (pillars - i))
        segment = rng.randint(1, max_for_segment)
        lengths.append(segment)
        remaining -= segment
    return lengths


def simulate_run(config: DungeonConfig, rng: random.Random) -> Iterable[Step]:
    room_count = 0
    pillar_count = 0
    labyrinth_lengths = generate_labyrinth_lengths(rng, config.rules.pillars)
    length_index = 0

    room_count += 1
    yield Step(1, config.entrance, config.entrance_inscription)

    while True:
        if room_count >= config.rules.max_rooms and config.rules.reset_on_overflow:
            yield Step(room_count + 1, config.entrance, "Zu viele Räume! Rückkehr zum Eingang.")
            return

        if pillar_count >= config.rules.pillars:
            room_count += 1
            yield Step(room_count, config.boss, config.boss_inscription)
            return

        labyrinth_rooms_remaining = labyrinth_lengths[length_index]
        if labyrinth_rooms_remaining > 0:
            room_count += 1
            labyrinth_lengths[length_index] -= 1
            yield Step(room_count, config.labyrinth, "Ein weiterer verwirrender Gang.")
            continue

        pillar_count += 1
        length_index += 1
        room_count += 1
        seen_rooms = room_count
        pillar_details = (
            f"Säule {pillar_count} — Räume gesehen: {seen_rooms}. "
            f"Pokémon werden um {config.rules.pillar_level_increase} Level stärker."
        )
        yield Step(room_count, config.pillar, pillar_details)


def format_steps(steps: Iterable[Step]) -> str:
    lines = []
    for step in steps:
        lines.append(f"{step.index:02d}. {step.room_type}: {step.details}")
    return "\n".join(lines)


def build_visual_nodes(steps: list[Step]) -> list[VisualNode]:
    nodes: list[VisualNode] = []
    angle = 0.0
    radius = 40.0
    for step in steps:
        angle += 0.7
        radius += 18
        jitter = random.Random(step.index)
        x = 350 + radius * math.cos(angle) + jitter.uniform(-24, 24)
        y = 350 + radius * math.sin(angle) + jitter.uniform(-24, 24)
        x = max(60, min(640, x))
        y = max(60, min(640, y))
        nodes.append(
            VisualNode(
                index=step.index,
                room_type=step.room_type,
                label=f"{step.index:02d}",
                x=x,
                y=y,
            )
        )
    return nodes


def render_html(config: DungeonConfig, steps: list[Step]) -> str:
    nodes = build_visual_nodes(steps)
    lines = []
    for idx in range(1, len(nodes)):
        prev = nodes[idx - 1]
        curr = nodes[idx]
        lines.append(
            f'<line class="edge" x1="{prev.x:.1f}" y1="{prev.y:.1f}" '
            f'x2="{curr.x:.1f}" y2="{curr.y:.1f}" />'
        )
    circles = []
    for node, step in zip(nodes, steps, strict=True):
        room_class = step.room_type.lower().replace(" ", "-")
        circles.append(
            f'<g class="node {room_class}">'
            f'<circle cx="{node.x:.1f}" cy="{node.y:.1f}" r="18" />'
            f'<text x="{node.x:.1f}" y="{node.y + 5:.1f}">{node.label}</text>'
            f'</g>'
        )
    steps_text = "\n".join(
        f"<li><strong>{step.index:02d} {step.room_type}</strong> — {step.details}</li>" for step in steps
    )
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{config.name} Visual</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: "Segoe UI", system-ui, sans-serif;
    }}
    body {{
      margin: 0;
      background: radial-gradient(circle at top, #2a1b3d, #0b0d16 55%, #06060a 100%);
      color: #f6f0ff;
    }}
    header {{
      padding: 32px 40px 12px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 2rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .subtitle {{
      opacity: 0.75;
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(320px, 1fr) 320px;
      gap: 24px;
      padding: 12px 40px 40px;
    }}
    .panel {{
      background: rgba(10, 12, 24, 0.75);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 18px;
      padding: 20px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45);
    }}
    svg {{
      width: 100%;
      height: 520px;
    }}
    .edge {{
      stroke: rgba(160, 120, 255, 0.35);
      stroke-width: 3;
      filter: drop-shadow(0 0 6px rgba(120, 80, 255, 0.4));
    }}
    .node circle {{
      fill: rgba(255, 255, 255, 0.08);
      stroke: rgba(255, 255, 255, 0.3);
      stroke-width: 2;
      filter: drop-shadow(0 0 12px rgba(120, 80, 255, 0.55));
    }}
    .node text {{
      font-size: 12px;
      text-anchor: middle;
      fill: #f9f1ff;
      pointer-events: none;
    }}
    .node.giratina-raum circle {{
      fill: rgba(255, 120, 120, 0.25);
      stroke: rgba(255, 120, 120, 0.9);
      filter: drop-shadow(0 0 16px rgba(255, 120, 120, 0.8));
    }}
    .node.säulenraum circle {{
      fill: rgba(90, 180, 255, 0.25);
      stroke: rgba(120, 220, 255, 0.9);
    }}
    .legend {{
      display: grid;
      gap: 12px;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.95rem;
    }}
    .legend-swatch {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      box-shadow: 0 0 10px rgba(120, 80, 255, 0.8);
    }}
    .legend-labyrinth {{
      background: rgba(255, 255, 255, 0.25);
    }}
    .legend-pillar {{
      background: rgba(120, 220, 255, 0.9);
    }}
    .legend-boss {{
      background: rgba(255, 120, 120, 0.9);
    }}
    ol {{
      margin: 12px 0 0;
      padding-left: 20px;
      max-height: 420px;
      overflow: auto;
    }}
    li {{
      margin-bottom: 8px;
      font-size: 0.92rem;
      line-height: 1.4;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{config.name}</h1>
    <div class="subtitle">{config.game} — Visualisierung für eine Spielsitzung</div>
  </header>
  <section class="layout">
    <div class="panel">
      <svg viewBox="0 0 700 700" aria-label="Labyrinth-Visualisierung">
        {"".join(lines)}
        {"".join(circles)}
      </svg>
    </div>
    <aside class="panel">
      <div class="legend">
        <div class="legend-item"><span class="legend-swatch legend-labyrinth"></span> Labyrinthraum</div>
        <div class="legend-item"><span class="legend-swatch legend-pillar"></span> Säulenraum</div>
        <div class="legend-item"><span class="legend-swatch legend-boss"></span> Giratina-Raum</div>
      </div>
      <h2>Abfolge</h2>
      <ol>{steps_text}</ol>
    </aside>
  </section>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate Das Labyrinth dungeon traversal.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/dungeon.json"),
        help="Path to dungeon configuration JSON.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    parser.add_argument(
        "--html-output",
        type=Path,
        default=None,
        help="Optional path to write an HTML visualization.",
    )
    args = parser.parse_args()

    config = load_config(args.data)
    rng = random.Random(args.seed)
    steps = list(simulate_run(config, rng))
    print(f"Dungeon: {config.name} ({config.game})")
    print(format_steps(steps))
    if args.html_output:
        html = render_html(config, steps)
        args.html_output.write_text(html, encoding="utf-8")
        print(f"HTML visualization written to {args.html_output}")


if __name__ == "__main__":
    main()
