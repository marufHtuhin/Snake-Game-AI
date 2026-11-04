# Snake Game AI

A Python Snake game built with Pygame. It includes Player Mode and AI Mode.
The AI uses A* pathfinding, Manhattan distance, flood-fill safety analysis,
and a fallback move selector.

## Features
- Player-controlled mode (arrow keys)
- AI mode with A* food seeking
- Flood-fill reachable-space safety check
- Safe fallback movement when a food path is unavailable or unsafe
- Score and persistent high score
- Pause, restart, instructions, and menu screens
- Dark UI with neon accents

## Play online
After deploying: `https://<your-username>.github.io/Snake-Game-AI/`

## Setup (Windows PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Controls
- Player Mode: Arrow keys
- Space: Pause / resume
- `+` / `-`: Speed up / slow down
- Escape: Return to main menu
- Enter: Restart after game over

## Project structure
- `main.py`: application entry point
- `game.py`: game loop, states, rendering, scoring
- `snake.py`: snake movement and growth
- `food.py`: random food placement
- `ai/astar.py`: A* pathfinding
- `ai/ai_controller.py`: AI decision-making and safety checks
- `settings.py`: window, grid, and colors

## AI notes
A* uses Manhattan distance on a four-direction grid. The controller then
checks whether the first move leaves enough reachable space for the snake.
If the planned route is not judged safe, it chooses a legal move with the
largest reachable area. This is a practical heuristic, not a mathematical
guarantee that the snake can never lose.

## Deploy (GitHub Pages)
```bash
git init && git add . && git commit -m "Snake Game AI"
git branch -M main
git remote add origin https://github.com/<your-username>/Snake-Game-AI.git
git push -u origin main
```
Then in the repo: **Settings > Pages > Source: GitHub Actions**. The included
workflow builds a WebAssembly version with pygbag and publishes it.

## AI improvements
- Path is validated by simulating the snake eating, then requiring the tail stay reachable
- Tail-following stall mode when no safe food path exists
- Anti-loop fallback; blue dots show the planned A* path
