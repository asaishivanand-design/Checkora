\# Checkora — Hybrid C++17 \& Python AI Chess Platform



Checkora is a full-stack AI Chess platform powered by \*\*Django\*\* and a \*\*Hybrid C++17 / Python Minimax Engine with Alpha-Beta Pruning\*\*.



\## Key Features

\- \*\*Hybrid AI Architecture\*\*: Primary high-speed C++17 Minimax engine (`game/engine/main.cpp`) with automatic fallback to `python-chess` (`game/engine/main.py`).

\- \*\*Configurable Search Depth\*\*: Easy (Depth 1), Medium (Depth 2), and Hard (Depth 3 with center-control heuristics and move ordering).

\- \*\*Interactive Web UI\*\*: Real-time move validation, legal move highlighting, and engine telemetry logs.

\- \*\*Automated Test Suite\*\*: Unit tests covering board initialization, legal/illegal move validation, AI subprocess communication, and REST API endpoints.



\## Quickstart

```bash

pip install -r requirements.txt

g++ -O2 -std=c++17 game/engine/main.cpp -o game/engine/main

python manage.py migrate

python manage.py test

python manage.py runserver

