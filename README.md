# Dungeon Simulator – Das Labyrinth

This repo contains a lightweight prototype for simulating **Das Labyrinth** from Pokémon Diamant/Perl/Platin so it can be used as a visual aid during tabletop sessions. It now ships with a Streamlit mini-game where you control an NPC through the maze.

## What the simulator models

The rules are encoded from the dungeon description:

- The labyrinth contains multiple maze rooms and **three pillar rooms**.
- After visiting the **third pillar**, the **next room is Giratina's room**.
- You must not visit more than **30 rooms** total; otherwise, you are reset to the entrance.
- Each pillar records the pillar number and the number of rooms seen.
- After every pillar, Pokémon are 10 levels stronger (tracked in the narration).

These rules are stored in `data/dungeon.json` so you can tweak them easily.

## Quick start (CLI)

```bash
python src/simulator.py --seed 42
```

### HTML visualization

Generate a standalone HTML visualization (suitable for opening in a browser during your session):

```bash
python src/simulator.py --seed 42 --html-output docs/labyrinth.html
```

Open `docs/labyrinth.html` in your browser to view the glowing dungeon path.

Sample output:

```
Dungeon: Das Labyrinth (Pokémon Diamant/Perl/Platin)
01. Eingang: ...Nach drei Säulen... zum schlafenden... ...30 nicht überschreiten...
02. Labyrinthraum: Ein weiterer verwirrender Gang.
03. Labyrinthraum: Ein weiterer verwirrender Gang.
04. Säulenraum: Säule 1 — Räume gesehen: 4. Pokémon werden um 10 Level stärker.
05. Labyrinthraum: Ein weiterer verwirrender Gang.
06. Labyrinthraum: Ein weiterer verwirrender Gang.
07. Säulenraum: Säule 2 — Räume gesehen: 7. Pokémon werden um 10 Level stärker.
08. Labyrinthraum: Ein weiterer verwirrender Gang.
09. Säulenraum: Säule 3 — Räume gesehen: 9. Pokémon werden um 10 Level stärker.
10. Giratina-Raum: Dies ist...Wo Leben funkelt...Wo Leben schwindet...Ein Ort, an dem sich zwei Welten überlappen...
```

## Quick start (Streamlit game)

```bash
streamlit run src/app.py
```

### Game rules

- Start at the entrance and explore a 6×5 dungeon grid.
- **Find all 3 pillars within 30 rooms** to win.
- If you **re-enter any previously visited room**, the dungeon resets.
- If you **visit more than 30 rooms**, the dungeon resets.

## Next steps to expand the game-session visual

1. **Design a room graph.**
   - Represent labyrinth rooms as nodes and create multiple edges for alternative paths.
   - Add three pillar nodes and a boss node.

2. **Build a renderer.**
   - For quick iteration, render the graph with a simple web UI (e.g., canvas/SVG with React or vanilla JS).
   - Each step in the simulation reveals the next room.

3. **Session controls.**
   - Add a “Next Room” button that advances the simulation.
   - Add “Reset” to start over if 30 rooms are exceeded.

4. **Content tweaks.**
   - Expand the inscriptions with localized text.
   - Add additional maze room variants for more visual flavor.

## Project layout

- `data/dungeon.json` — dungeon rules and inscriptions.
- `src/simulator.py` — CLI prototype to generate a randomized traversal.
- `docs/` — future design notes.
