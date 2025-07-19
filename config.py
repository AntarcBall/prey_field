import numpy as np

# --- Field Parameters ---
FIELD_WIDTH = 800
FIELD_HEIGHT = 600
FIELD_COLOR = (20, 20, 20)  # Dark Grey

# --- Simulation Parameters ---
FPS = 60

# --- Agent Initial Parameters ---
INITIAL_FOXES = 10
INITIAL_RABBITS = 50
# Speed is defined in pixels per second.
AGENT_SPEED_PIXELS_PER_SEC = 2.0

# --- Fox Replication (Collision-based) ---
# Governs the probabilistic replication of foxes upon eating a rabbit.
# The number of new foxes is chosen from a distribution with this mean.
FOX_REPLICATION_MEAN = 2.0
# The "spread" or standard deviation of the replication distribution.
# A small sigma (e.g., 0.1) makes replication deterministic (always FOX_REPLICATION_MEAN).
# A larger sigma (e.g., 1.5) makes replication more random.
FOX_REPLICATION_SIGMA = 1.5
# The possible outcomes for the number of new foxes (e.g., 0 to 8).
FOX_REPLICATION_RANGE = np.arange(0, 9)

# --- Rabbit Replication (Time-based) ---
# Each rabbit has a chance to produce this many offspring per minute, on average.
RABBIT_REPLICATION_RATE_PER_MIN = 2.0

# --- Collision Parameters ---
COLLISION_DISTANCE = 5  # in pixels

# --- Derived Constants (do not change directly) ---
AGENT_SPEED_PER_FRAME = AGENT_SPEED_PIXELS_PER_SEC / FPS
# Probability for one rabbit to replicate in a single frame
if RABBIT_REPLICATION_RATE_PER_MIN > 0:
    RABBIT_REPLICATION_PROB_PER_FRAME = (RABBIT_REPLICATION_RATE_PER_MIN / 60) / FPS
else:
    RABBIT_REPLICATION_PROB_PER_FRAME = 0
