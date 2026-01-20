#!/usr/bin/env python3
"""Dungeon simulator for Das Labyrinth (Pokémon Diamant/Perl/Platin).

This script generates a randomized traversal that respects the dungeon rules:
- After three pillar rooms, the next room is Giratina's room.
- You must not exceed 30 rooms visited or you reset to the entrance.
"""

from __future__ import annotations

import argparse
import json
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate Das Labyrinth dungeon traversal.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/dungeon.json"),
        help="Path to dungeon configuration JSON.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    args = parser.parse_args()

    config = load_config(args.data)
    rng = random.Random(args.seed)
    steps = list(simulate_run(config, rng))
    print(f"Dungeon: {config.name} ({config.game})")
    print(format_steps(steps))


if __name__ == "__main__":
    main()
