from dataclasses import dataclass, field
import numpy as np

@dataclass
class SimConfig:
    # --- Field Parameters ---
    FIELD_WIDTH: int = 400
    FIELD_HEIGHT: int = 400
    FIELD_COLOR: tuple = (20, 20, 20)  # Dark Grey

    # --- Simulation Parameters ---
    FPS: int = 60
    MAX_AGENTS: int = 5000  # Maximum number of agents allowed in the simulation

    # --- Agent Initial Parameters ---
    INITIAL_FOXES: int = 60
    INITIAL_RABBITS: int = 160
    # Speed is defined in pixels per second.
    AGENT_SPEED_PIXELS_PER_SEC: float = 65.0

    # --- Fox Replication (Collision-based) ---
    # Governs the probabilistic replication of foxes upon eating a rabbit.
    # The number of new foxes is chosen from a distribution with this mean.
    FOX_REPLICATION_MEAN: float = 0.1

    # A small sigma (e.g., 0.1) makes replication deterministic (always FOX_REPLICATION_MEAN).
    # A large sigma (e.g., 5.0) makes replication more random.
    FOX_REPLICATION_SIGMA: float = 6.5
    # The possible outcomes for the number of new foxes (e.g., 0 to 8).
    FOX_REPLICATION_RANGE: np.ndarray = field(default_factory=lambda: np.arange(0, 4))

    # --- Natural Death (Time-based) ---
    # The probability that a fox will die in any given frame, independent of other factors.
    # A value of 0.001 means a 0.1% chance per frame.
    FOX_DEATH_PROB_PER_FRAME: float = 0.005

    # --- Rabbit Replication (Time-based) ---
    # Each rabbit has a chance to produce this many offspring per minute, on average.
    RABBIT_REPLICATION_RATE_PER_MIN: float = 14.0

    # --- Collision Parameters ---
    COLLISION_DISTANCE: int = 5  # in pixels

    # --- Derived Constants (do not change directly) ---
    AGENT_SPEED_PER_FRAME: float = field(init=False)
    RABBIT_REPLICATION_PROB_PER_FRAME: float = field(init=False)

    def __post_init__(self):
        self.AGENT_SPEED_PER_FRAME = self.AGENT_SPEED_PIXELS_PER_SEC / self.FPS
        if self.RABBIT_REPLICATION_RATE_PER_MIN > 0:
            self.RABBIT_REPLICATION_PROB_PER_FRAME = (self.RABBIT_REPLICATION_RATE_PER_MIN / 60) / self.FPS
        else:
            self.RABBIT_REPLICATION_PROB_PER_FRAME = 0


# Create a global instance of the configuration
sim_cfg = SimConfig()
