import pygame
import numpy as np
import random
import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
import config as cfg

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((cfg.FIELD_WIDTH, cfg.FIELD_HEIGHT))
pygame.display.set_caption("Killing Field Simulation")
clock = pygame.time.Clock()

# --- PyQtGraph Setup ---
app = QApplication.instance() or QApplication(sys.argv)
win = pg.GraphicsLayoutWidget(show=True, title="Population over Time")
win.resize(800, 400)
win.setWindowTitle('Population Dynamics')
pg.setConfigOptions(antialias=True)

plot = win.addPlot(title="Population")
plot.setLabel('left', 'Count')
plot.setLabel('bottom', 'Time (s)')
plot.addLegend()
fox_curve = plot.plot(pen='r', name='Foxes')
rabbit_curve = plot.plot(pen='g', name='Rabbits')

time_points = []
fox_counts = []
rabbit_counts = []


# --- Agent Classes ---
class Agent:
    """Base class for all agents in the simulation."""
    def __init__(self, x, y, speed):
        self.pos = np.array([x, y], dtype=float)
        angle = random.uniform(0, 2 * np.pi)
        self.vel = np.array([np.cos(angle), np.sin(angle)]) * speed

    def move(self):
        """Update agent's position and handle wall collisions."""
        self.pos += self.vel
        if not (0 <= self.pos[0] <= cfg.FIELD_WIDTH):
            self.vel[0] *= -1
            self.pos[0] = np.clip(self.pos[0], 0, cfg.FIELD_WIDTH)
        if not (0 <= self.pos[1] <= cfg.FIELD_HEIGHT):
            self.vel[1] *= -1
            self.pos[1] = np.clip(self.pos[1], 0, cfg.FIELD_HEIGHT)

    def draw(self, surface):
        """Draw the agent on the screen. To be implemented by subclasses."""
        raise NotImplementedError


class Fox(Agent):
    """Represents a fox, the predator."""
    def __init__(self, x, y, speed=cfg.AGENT_SPEED_PER_FRAME):
        super().__init__(x, y, speed)
        self.size = 8

    def draw(self, surface):
        """Draw the fox as a triangle pointing in its direction of movement."""
        angle = np.arctan2(self.vel[1], self.vel[0])
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        p1 = self.pos + np.array([self.size, 0]) @ rotation_matrix.T
        p2 = self.pos + np.array([-self.size / 2, -self.size / 1.5]) @ rotation_matrix.T
        p3 = self.pos + np.array([-self.size / 2, self.size / 1.5]) @ rotation_matrix.T
        pygame.draw.polygon(surface, (255, 100, 100), [p1, p2, p3])


class Rabbit(Agent):
    """Represents a rabbit, the prey."""
    def __init__(self, x, y, speed=cfg.AGENT_SPEED_PER_FRAME):
        super().__init__(x, y, speed)
        self.radius = 5

    def draw(self, surface):
        """Draw the rabbit as a circle."""
        pygame.draw.circle(surface, (100, 255, 100), self.pos.astype(int), self.radius)


# --- Simulation Functions ---
def get_replication_count():
    """
    Determines the number of new foxes to create based on a discretized
    normal distribution.
    """
    if cfg.FOX_REPLICATION_SIGMA < 0.01:
        return int(round(cfg.FOX_REPLICATION_MEAN))
    
    weights = np.exp(-0.5 * ((cfg.FOX_REPLICATION_RANGE - cfg.FOX_REPLICATION_MEAN) / cfg.FOX_REPLICATION_SIGMA)**2)
    probabilities = weights / np.sum(weights)
    return random.choices(cfg.FOX_REPLICATION_RANGE, weights=probabilities, k=1)[0]

def create_initial_agents():
    """Creates the initial set of agents, ensuring they don't overlap."""
    agents = []
    for _ in range(cfg.INITIAL_RABBITS):
        while True:
            pos = (random.randint(20, cfg.FIELD_WIDTH - 20), random.randint(20, cfg.FIELD_HEIGHT - 20))
            if not any(np.linalg.norm(np.array(pos) - agent.pos) < 20 for agent in agents):
                agents.append(Rabbit(pos[0], pos[1]))
                break
    for _ in range(cfg.INITIAL_FOXES):
        while True:
            pos = (random.randint(20, cfg.FIELD_WIDTH - 20), random.randint(20, cfg.FIELD_HEIGHT - 20))
            if not any(np.linalg.norm(np.array(pos) - agent.pos) < 20 for agent in agents):
                agents.append(Fox(pos[0], pos[1]))
                break
    return agents


# --- Main Simulation ---
def main():
    """Main function to run the simulation loop."""
    all_agents = create_initial_agents()
    foxes = [agent for agent in all_agents if isinstance(agent, Fox)]
    rabbits = [agent for agent in all_agents if isinstance(agent, Rabbit)]

    running = True
    start_time = pygame.time.get_ticks()
    last_plot_update = start_time

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        app.processEvents()

        for agent in all_agents:
            agent.move()

        # --- Natural Rabbit Replication (Time-based) ---
        new_rabbits = []
        if cfg.RABBIT_REPLICATION_PROB_PER_FRAME > 0:
            for rabbit in rabbits:
                if random.random() < cfg.RABBIT_REPLICATION_PROB_PER_FRAME:
                    new_rabbits.append(Rabbit(rabbit.pos[0], rabbit.pos[1]))
        
        # --- Natural Fox Death (Time-based) ---
        foxes_to_remove_natural = set()
        if cfg.FOX_DEATH_PROB_PER_FRAME > 0:
            for fox in foxes:
                if random.random() < cfg.FOX_DEATH_PROB_PER_FRAME:
                    foxes_to_remove_natural.add(fox)

        # --- Collision Detection (Foxes vs Rabbits) ---
        new_foxes = []
        rabbits_to_remove = set()

        for fox in foxes:
            for rabbit in rabbits:
                if rabbit in rabbits_to_remove:
                    continue
                
                if np.linalg.norm(fox.pos - rabbit.pos) < cfg.COLLISION_DISTANCE:
                    rabbits_to_remove.add(rabbit)
                    num_new_foxes = get_replication_count()
                    for _ in range(num_new_foxes):
                        new_foxes.append(Fox(fox.pos[0], fox.pos[1]))
                    break 

        # --- Update Agent Lists ---
        if rabbits_to_remove:
            rabbits = [rabbit for rabbit in rabbits if rabbit not in rabbits_to_remove]
        if foxes_to_remove_natural:
            foxes = [fox for fox in foxes if fox not in foxes_to_remove_natural]
        if new_rabbits:
            rabbits.extend(new_rabbits)
        if new_foxes:
            foxes.extend(new_foxes)
        
        all_agents = foxes + rabbits

        # --- Drawing ---
        screen.fill(cfg.FIELD_COLOR)
        for agent in all_agents:
            agent.draw(screen)
        pygame.display.flip()

        # --- Data Update for Plot ---
        current_time = pygame.time.get_ticks()
        if current_time - last_plot_update > 250:
            elapsed_time_sec = (current_time - start_time) / 1000.0
            time_points.append(elapsed_time_sec)
            fox_counts.append(len(foxes))
            rabbit_counts.append(len(rabbits))
            
            fox_curve.setData(time_points, fox_counts)
            rabbit_curve.setData(time_points, rabbit_counts)
            last_plot_update = current_time

        # --- Tick and Termination ---
        clock.tick(cfg.FPS)
        if not rabbits or not foxes:
            running = False

    print("Simulation over. Closing in 5 seconds...")
    pygame.time.wait(5000)
    
    pygame.quit()
    win.close()
    app.quit()
    sys.exit()


if __name__ == '__main__':
    main()
