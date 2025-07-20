import numpy as np

class Config:
    def __init__(self):
        self.field = self.Field()
        self.simulation = self.Simulation()
        self.agent = self.Agent()
        self.fox = self.Fox()
        self.rabbit = self.Rabbit()
        self.collision = self.Collision()

        # Derived constants that depend on multiple sections
        self.agent.speed_per_frame = self.agent.speed_pixels_per_sec / self.simulation.fps
        if self.rabbit.replication_rate_per_min > 0:
            self.rabbit.replication_prob_per_frame = (self.rabbit.replication_rate_per_min / 60) / self.simulation.fps
        else:
            self.rabbit.replication_prob_per_frame = 0

    class Field:
        def __init__(self):
            self.width = 600
            self.height = 600
            self.color = (20, 20, 20)  # Dark Grey

    class Simulation:
        def __init__(self):
            self.fps = 60
            self.max_agents = 5000  # Maximum number of agents allowed in the simulation
            self.close_on_extinction = True

    class Agent:
        def __init__(self):
            self.initial_foxes = 20
            self.initial_rabbits = 160
            self.speed_pixels_per_sec = 120.0
            self.speed_per_frame = 0.0 # Placeholder, calculated in main Config __init__

    class Fox:
        def __init__(self):
            self.replication_mean = 0
            self.replication_sigma = 4.5
            self.replication_range = np.arange(0, 3)
            self.death_prob_per_frame = 0.005

    class Rabbit:
        def __init__(self):
            self.replication_rate_per_min = 18.0
            self.replication_prob_per_frame = 0.0 # Placeholder, calculated in main Config __init__

    class Collision:
        def __init__(self):
            self.distance = 4  # in pixels

# Create a global instance of the configuration
sim_cfg = Config()