import pygame
import numpy as np
import sys
import os
import csv
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
from config import sim_cfg, SimConfig

# --- Constants ---
AGENT_TYPE_RABBIT = 0
AGENT_TYPE_FOX = 1

# --- Simulation Logging ---
LOG_FILE = "simulation_log.csv"

def log_simulation_data(duration: float, config: SimConfig):
    """Logs simulation duration and configuration parameters to a CSV file."""
    fieldnames = []
    row_data = {}

    # Get all parameters from the SimConfig dataclass
    for field_name in config.__dataclass_fields__:
        # Exclude derived fields that are not initialized directly
        if config.__dataclass_fields__[field_name].init:
            fieldnames.append(field_name)
            value = getattr(config, field_name)
            if isinstance(value, np.ndarray):
                row_data[field_name] = str(value.tolist())
            else:
                row_data[field_name] = value
    
    fieldnames.append("duration_seconds")
    row_data["duration_seconds"] = duration

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # Write header only if file is new
        writer.writerow(row_data)



# --- Constants ---
AGENT_TYPE_RABBIT = 0
AGENT_TYPE_FOX = 1

# --- Pygame Setup ---
os.environ['SDL_VIDEO_WINDOW_POS'] = f"0,0"
pygame.init()
screen = pygame.display.set_mode((sim_cfg.FIELD_WIDTH, sim_cfg.FIELD_HEIGHT))
pygame.display.set_caption("Optimized Killing Field Simulation")
clock = pygame.time.Clock()

# --- PyQtGraph Setup ---
app = QApplication.instance() or QApplication(sys.argv)
win = pg.GraphicsLayoutWidget(show=True, title="Population over Time")
win.resize(800, 400)
win.setWindowTitle('Population Dynamics')
win.move(sim_cfg.FIELD_WIDTH, 0) # Position next to Pygame window
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

# --- Agent Data (NumPy Array) ---
# [pos_x, pos_y, vel_x, vel_y, type, active]
agents = np.zeros((sim_cfg.MAX_AGENTS, 6), dtype=np.float32)
num_agents = 0

# --- Simulation Functions ---
def add_agent(agent_type, x, y):
    """Adds a new agent to the simulation."""
    global num_agents
    if num_agents >= sim_cfg.MAX_AGENTS:
        return

    agents[num_agents, 0] = x
    agents[num_agents, 1] = y
    angle = np.random.uniform(0, 2 * np.pi)
    agents[num_agents, 2] = np.cos(angle) * sim_cfg.AGENT_SPEED_PER_FRAME
    agents[num_agents, 3] = np.sin(angle) * sim_cfg.AGENT_SPEED_PER_FRAME
    agents[num_agents, 4] = agent_type
    agents[num_agents, 5] = 1  # Active
    num_agents += 1

def remove_agent(index):
    """Removes an agent by swapping with the last active one."""
    global num_agents
    num_agents -= 1
    agents[index] = agents[num_agents]
    agents[num_agents, 5] = 0 # Mark as inactive


def get_replication_count():
    """
    Determines the number of new foxes to create based on a discretized
    normal distribution.
    """
    if sim_cfg.FOX_REPLICATION_SIGMA < 0.01:
        return int(round(sim_cfg.FOX_REPLICATION_MEAN))
    
    weights = np.exp(-0.5 * ((sim_cfg.FOX_REPLICATION_RANGE - sim_cfg.FOX_REPLICATION_MEAN) / sim_cfg.FOX_REPLICATION_SIGMA)**2)
    probabilities = weights / np.sum(weights)
    return np.random.choice(sim_cfg.FOX_REPLICATION_RANGE, p=probabilities)

def create_initial_agents():
    """Creates the initial set of agents."""
    for _ in range(sim_cfg.INITIAL_RABBITS):
        add_agent(AGENT_TYPE_RABBIT, np.random.randint(20, sim_cfg.FIELD_WIDTH - 20), np.random.randint(20, sim_cfg.FIELD_HEIGHT - 20))
    for _ in range(sim_cfg.INITIAL_FOXES):
        add_agent(AGENT_TYPE_FOX, np.random.randint(20, sim_cfg.FIELD_WIDTH - 20), np.random.randint(20, sim_cfg.FIELD_HEIGHT - 20))


def draw_agents(surface):
    """Draws all active agents."""
    active_agents = agents[:num_agents]
    is_rabbit = active_agents[:, 4] == AGENT_TYPE_RABBIT
    is_fox = ~is_rabbit

    # Draw Rabbits
    for pos in active_agents[is_rabbit, :2]:
        pygame.draw.circle(surface, (100, 255, 100), pos.astype(int), 5)

    # Draw Foxes
    for agent in active_agents[is_fox]:
        pos = agent[:2]
        vel = agent[2:4]
        angle = np.arctan2(vel[1], vel[0])
        size = 8
        p1 = pos + np.array([np.cos(angle), np.sin(angle)]) * size
        p2 = pos + np.array([np.cos(angle + 2.5), np.sin(angle + 2.5)]) * size * 0.8
        p3 = pos + np.array([np.cos(angle - 2.5), np.sin(angle - 2.5)]) * size * 0.8
        pygame.draw.polygon(surface, (255, 100, 100), [p1.tolist(), p2.tolist(), p3.tolist()])


# --- Main Simulation ---
def main():
    """Main function to run the simulation loop."""
    global num_agents
    create_initial_agents()

    running = True
    simulation_active = True
    simulation_ended_naturally = False
    start_time = pygame.time.get_ticks()
    last_plot_update = start_time

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Check if PyQtGraph window is closed
        if not win.isVisible():
            running = False

        app.processEvents()

        if simulation_active:
            active_agents = agents[:num_agents]

            # --- Agent Movement ---
            active_agents[:, :2] += active_agents[:, 2:4]
            
            # Wall collisions
            hit_left_wall = active_agents[:, 0] < 0
            hit_right_wall = active_agents[:, 0] > sim_cfg.FIELD_WIDTH
            hit_top_wall = active_agents[:, 1] < 0
            hit_bottom_wall = active_agents[:, 1] > sim_cfg.FIELD_HEIGHT

            active_agents[hit_left_wall | hit_right_wall, 2] *= -1
            active_agents[hit_top_wall | hit_bottom_wall, 3] *= -1
            
            np.clip(active_agents[:, 0], 0, sim_cfg.FIELD_WIDTH, out=active_agents[:, 0])
            np.clip(active_agents[:, 1], 0, sim_cfg.FIELD_HEIGHT, out=active_agents[:, 1])


            # --- Agent Masks ---
            is_rabbit = active_agents[:, 4] == AGENT_TYPE_RABBIT
            is_fox = ~is_rabbit
            
            # --- Natural Rabbit Replication ---
            if sim_cfg.RABBIT_REPLICATION_PROB_PER_FRAME > 0:
                num_rabbits = np.sum(is_rabbit)
                replication_chance = np.random.rand(num_rabbits) < sim_cfg.RABBIT_REPLICATION_PROB_PER_FRAME
                rabbits_that_replicated = active_agents[is_rabbit][replication_chance]
                for r in rabbits_that_replicated:
                    add_agent(AGENT_TYPE_RABBIT, r[0], r[1])

            # --- Natural Fox Death ---
            if sim_cfg.FOX_DEATH_PROB_PER_FRAME > 0:
                num_foxes = np.sum(is_fox)
                death_chance = np.random.rand(num_foxes) < sim_cfg.FOX_DEATH_PROB_PER_FRAME
                fox_indices_to_remove = np.where(is_fox)[0][death_chance]
                # Iterate backwards to not mess up indices while removing
                for i in sorted(fox_indices_to_remove, reverse=True):
                    remove_agent(i)
                    
            # --- Collision Detection ---
            # Re-calculate masks after potential removals
            active_agents = agents[:num_agents]
            is_rabbit = active_agents[:, 4] == AGENT_TYPE_RABBIT
            is_fox = ~is_rabbit
            
            fox_pos = active_agents[is_fox, :2]
            rabbit_pos = active_agents[is_rabbit, :2]
            
            if fox_pos.size > 0 and rabbit_pos.size > 0:
                # Calculate pairwise distances efficiently
                dist_matrix = np.sqrt(((fox_pos[:, np.newaxis, :] - rabbit_pos[np.newaxis, :, :])**2).sum(axis=2))
                collisions = dist_matrix < sim_cfg.COLLISION_DISTANCE
                
                collided_fox_indices, collided_rabbit_indices = np.where(collisions)
                
                # Avoid multiple foxes eating the same rabbit in one frame
                unique_collided_rabbits, unique_indices = np.unique(collided_rabbit_indices, return_index=True)
                
                if unique_collided_rabbits.size > 0:
                    # Map original fox indices from the collision matrix
                    colliding_fox_original_indices = np.where(is_fox)[0][collided_fox_indices[unique_indices]]
                    # Map original rabbit indices
                    rabbits_to_remove_original_indices = np.where(is_rabbit)[0][unique_collided_rabbits]

                    # Add new foxes
                    for i in colliding_fox_original_indices:
                        num_new_foxes = get_replication_count()
                        for _ in range(num_new_foxes):
                            add_agent(AGENT_TYPE_FOX, agents[i, 0], agents[i, 1])
                    
                    # Remove eaten rabbits (iterate backwards)
                    for i in sorted(rabbits_to_remove_original_indices, reverse=True):
                        remove_agent(i)

            # Check for simulation end conditions
            if np.sum(agents[:num_agents, 4] == AGENT_TYPE_RABBIT) == 0 or \
               np.sum(agents[:num_agents, 4] == AGENT_TYPE_FOX) == 0:
                simulation_active = False
                simulation_ended_naturally = True
                print("Simulation over. Populations died out.")

        # --- Drawing ---
        screen.fill(sim_cfg.FIELD_COLOR)
        draw_agents(screen)
        pygame.display.flip()

        # --- Data Update for Plot ---
        if simulation_active:
            current_time = pygame.time.get_ticks()
            if current_time - last_plot_update > 250:
                elapsed_time_sec = (current_time - start_time) / 1000.0
                time_points.append(elapsed_time_sec)
                
                active_agents = agents[:num_agents]
                num_foxes = np.sum(active_agents[:, 4] == AGENT_TYPE_FOX)
                num_rabbits = num_agents - num_foxes
                
                fox_counts.append(num_foxes)
                rabbit_counts.append(num_rabbits)
                
                fox_curve.setData(time_points, fox_counts)
                rabbit_curve.setData(time_points, rabbit_counts)
                last_plot_update = current_time

        # --- Tick ---
        clock.tick(sim_cfg.FPS)

    # Log simulation data before quitting
    if simulation_ended_naturally:
        final_elapsed_time_sec = (pygame.time.get_ticks() - start_time) / 1000.0
        log_simulation_data(final_elapsed_time_sec, sim_cfg)

    pygame.quit()
    win.close()
    app.quit()
    sys.exit()


if __name__ == '__main__':
    main()