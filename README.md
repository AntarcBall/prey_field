# Predator-Prey Simulation (Killing Field)

This project simulates a predator-prey ecosystem with foxes and rabbits based on the Lotka-Volterra model dynamics.

## Visualization
- **Simulation Window**: A `pygame` window showing agents moving in a field.
  - Foxes are represented by red triangles.
  - Rabbits are represented by green circles.
- **Graph Window**: A `PyQtGraph` window showing the population of each species over time.

## Core Mechanics
- **Movement**: Agents move in straight lines and bounce off walls elastically.
- **Rabbit Reproduction**: Rabbits reproduce over time at a fixed rate.
- **Fox Reproduction**: Foxes reproduce only after consuming a rabbit. The number of offspring is probabilistic.
- **Collision**: When a fox gets close to a rabbit, the rabbit is consumed, and the fox reproduces.

## How to Run
1. Install dependencies:
   ```bash
   pip install pygame pyqtgraph numpy PyQt5
   ```
2. Run the simulation:
   ```bash
   python main.py
   ```

## Configuration
All simulation parameters can be adjusted in the `config.py` file.

- `FIELD_WIDTH`, `FIELD_HEIGHT`: Size of the simulation area.
- `INITIAL_FOXES`, `INITIAL_RABBITS`: Starting population counts.
- `AGENT_SPEED_PIXELS_PER_SEC`: Movement speed for all agents.
- `FOX_REPLICATION_MEAN`: The average number of new foxes created after a successful hunt.
- `FOX_REPLICATION_SIGMA`: The standard deviation of the fox replication number. A higher value means more randomness.
- `RABBIT_REPLICATION_RATE_PER_MIN`: The average number of offspring a single rabbit produces per minute.
- `COLLISION_DISTANCE`: The distance (in pixels) at which a fox consumes a rabbit.
