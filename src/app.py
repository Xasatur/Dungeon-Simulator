#!/usr/bin/env python3
"""Streamlit dungeon simulator with a controllable NPC."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

import streamlit as st

GRID_WIDTH = 6
GRID_HEIGHT = 5
MAX_ROOMS = GRID_WIDTH * GRID_HEIGHT
PILLAR_COUNT = 3


@dataclass(frozen=True)
class Room:
    x: int
    y: int

    def neighbors(self) -> Iterable["Room"]:
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                yield Room(nx, ny)


@dataclass
class GameState:
    position: Room
    visited: set[Room]
    pillars: set[Room]
    pillars_found: int
    rooms_seen: int
    message: str


def create_game_state(rng: random.Random) -> GameState:
    rooms = [Room(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH)]
    start = Room(0, 0)
    rooms.remove(start)
    pillars = set(rng.sample(rooms, PILLAR_COUNT))
    return GameState(
        position=start,
        visited={start},
        pillars=pillars,
        pillars_found=0,
        rooms_seen=1,
        message="Welcome to the dungeon. Find all three pillars!",
    )


def reset_game(reason: str) -> None:
    rng = random.Random()
    st.session_state.game = create_game_state(rng)
    st.session_state.game.message = reason


def handle_move(direction: str) -> None:
    state: GameState = st.session_state.game
    offsets = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
    dx, dy = offsets[direction]
    next_room = Room(state.position.x + dx, state.position.y + dy)

    if not (0 <= next_room.x < GRID_WIDTH and 0 <= next_room.y < GRID_HEIGHT):
        state.message = "A wall blocks your path."
        return

    if next_room in state.visited:
        reset_game("You backtracked. The dungeon resets to the entrance!")
        return

    state.position = next_room
    state.visited.add(next_room)
    state.rooms_seen += 1

    if state.rooms_seen > MAX_ROOMS:
        reset_game("You wandered too long. Back to the entrance!")
        return

    if next_room in state.pillars:
        state.pillars_found += 1
        state.message = f"Pillar discovered! ({state.pillars_found}/{PILLAR_COUNT})"
        if state.pillars_found >= PILLAR_COUNT:
            state.message = "All pillars found! You win!"
    else:
        state.message = "You move deeper into the maze."


def render_grid(state: GameState) -> None:
    rows = []
    for y in range(GRID_HEIGHT):
        row = []
        for x in range(GRID_WIDTH):
            room = Room(x, y)
            if room == state.position:
                icon = "🧙"
            elif room in state.pillars and room in state.visited:
                icon = "🗿"
            elif room in state.visited:
                icon = "⬜"
            else:
                icon = "⬛"
            row.append(icon)
        rows.append(" ".join(row))
    st.markdown("<br>".join(rows), unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Dungeon Simulator", page_icon="🧭", layout="centered")
    st.title("Dungeon Simulator")
    st.caption(
        "Find 3 pillar rooms within 30 rooms. Backtracking or hitting 30 rooms sends you back."  # noqa: E501
    )

    if "game" not in st.session_state:
        st.session_state.game = create_game_state(random.Random())

    state: GameState = st.session_state.game

    st.markdown(
        f"**Rooms seen:** {state.rooms_seen}/{MAX_ROOMS} | "
        f"**Pillars found:** {state.pillars_found}/{PILLAR_COUNT}"
    )

    st.info(state.message)
    render_grid(state)

    col1, col2, col3 = st.columns(3)
    with col2:
        st.button("⬆️", on_click=handle_move, args=("up",))
    with col1:
        st.button("⬅️", on_click=handle_move, args=("left",))
    with col3:
        st.button("➡️", on_click=handle_move, args=("right",))
    _, col_down, _ = st.columns(3)
    with col_down:
        st.button("⬇️", on_click=handle_move, args=("down",))

    st.button("Reset dungeon", on_click=reset_game, args=("Dungeon reset.",))


if __name__ == "__main__":
    main()
